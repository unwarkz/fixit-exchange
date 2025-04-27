# fixit-exchange Project


src/
├── domain/
│   ├── entities.py
│   ├── enums.py
│   ├── flows/
│   │   └── simple_lead_flow.py
│   └── services.py
│
├── application/
│   ├── ports/
│   │   ├── message_sender.py
│   │   ├── dialog_repo.py
│   │   ├── issue_creator.py
│   │   └── accounting_connector.py
│   └── use_cases/
│       └── process_event.py
│
├── infrastructure/
│   ├── adapters/
│   │   ├── whatsapp_api.py
│   │   ├── okdesk_api.py
│   │   └── onec_connector.py
│   └── web/
│       ├── webhook_waba.py
│       └── webhook_okdesk.py
│
├── config.py
└── main.py

## Overview
Middleware for creating dialog flows and event exchange between different systems. For example okdesk, whatsapp, telegram, 1c accounting

Проект WABA-Okdesk: архитектура и реализация
Проект интеграции WhatsApp Business API (WABA) с системой Okdesk и учётом статусов из 1С требует чёткой архитектуры и надёжной обработки вебхуков. По принципам чистой архитектуры код разбит на слои Domain, Application и Infrastructure​
dev.to
. В слое Domain находятся сущности (например, Dialog и Message) и бизнес-логика обработки сообщений. Слой Application отвечает за сценарии (use cases): приём WhatsApp-сообщения, обновление статуса оплаты, закрытие заявки и т.п. Слой Infrastructure содержит технические детали: работу с HTTP (FastAPI/Flask), БД (SQLite), логирование и проверку аутентификации. Такой подход («Domain > Application > Infrastructure»​
dev.to
) упрощает поддержку и тестирование кода.
База данных SQLite для диалогов
Для хранения переписки целесообразно использовать встроенный модуль Python sqlite3, что даёт лёгкую файловую БД без отдельного сервера​
docs.python.org
. При старте приложения по схеме DDD следует создать объект соединения с файлом БД, например:
import sqlite3
conn = sqlite3.connect("dialogs.db")  # создаст файл и подключится к нему
Такой подход соответствует документации sqlite3: “create a connection to the database in the current working directory, implicitly creating it if it does not exist”​
docs.python.org
. После выполнения операций с помощью курсора (cursor.execute(...)) следует вызывать conn.commit() для сохранения транзакции​
docs.python.org
. Важно защищаться от SQL-инъекций: при формировании запросов не конкатенировать строки, а использовать плейсхолдеры (символ ?) и передавать параметры отдельно​
docs.python.org
. Например:
cursor.execute("INSERT INTO messages(dialog_id, text) VALUES (?, ?)", (dialog_id, text))
conn.commit()
Это позволяет SQLite корректно экранировать данные и избегать уязвимостей. Таким образом, модели домена (например, класс Dialog) могут использовать инфраструктурный слой с репозиториями, которые выполняют подобные SQL-запросы через sqlite3​
docs.python.org
​
docs.python.org
.
Обработка вебхука WhatsApp
При поступлении webhook от WhatsApp по адресу API необходимо проверить подпись X-Hub-Signature-256, вычисляемую на основе app_secret. Для этого вычисляют HMAC-SHA256 от тела запроса (payload) с секретом приложения. Пример реализации на Python:
import hmac, hashlib

def verify_whatsapp_signature(secret: str, payload: bytes, header_signature: str) -> bool:
    received = header_signature.removeprefix('sha256=')
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(received, digest)
Здесь используется hmac.compare_digest для защиты от атак по времени сравнения​
stackoverflow.com
. Такой код совпадает с рекомендациями сообщества (StackOverflow)​
stackoverflow.com
. Если подпись не проходит проверку, сервер должен сразу вернуть 401 Unauthorized. После проверки сервер обрабатывает JSON от WhatsApp: создаёт или обновляет запись диалога в БД и сохраняет сообщение. Также следует учесть, что при регистрации webhook’а Facebook/WhatsApp шлёт GET-запрос с параметром hub.challenge – его нужно вернуть в ответе, чтобы подтвердить endpoint.
Обработка вебхука Okdesk (Basic Auth)
Okdesk отправляет уведомления о событиях (например, закрытие заявки) на наш endpoint, защищая их HTTP Basic Auth. Это означает, что заголовок Authorization содержит строку вида Basic <base64(login:password)>. По спецификации, для Basic-аутентификации “credentials are constructed by first combining the username and password with a colon…, and then by encoding the resulting string in base64”​
developer.mozilla.org
. На нашей стороне необходимо декодировать заголовок, извлечь логин и пароль и сверить с ожидаемыми (например, из env-переменных). Если проверка не прошла, возвращается 401 Unauthorized. После удачной авторизации сервер читает тело запроса (JSON от Okdesk), определяет номер заявки и её статус. Если это событие “заявка закрыта”, соответствующую запись в БД можно пометить закрытой или записать в лог. Такой механизм соответствует рекомендациям Okdesk (использование Basic Auth, см. документацию).
Обработка событий из 1С
Платёжная система 1С при изменении статуса оплаты может слать запрос к нашему API. Этот webhook-эндпоинт также должен принимать JSON с данными платежа и обрабатывать их: находить по идентификатору соответствующую запись (например, заявку или диалог) и обновлять статус оплаты. Без специальных инструкций, обычно достаточно проверять, что запрос корректен (можно использовать, например, секретный токен или IP-фильтр). Затем внутри Domain-слоя вызывается use-case: отметить запрос как “оплачен”. Этот функционал тестируется аналогично: при поступлении данных обновляется состояние в БД.
Логирование
Важная часть проекта – детальное логирование на всех этапах. Веб-фреймворки (Flask/FastAPI) используют стандартный модуль Python logging (в Flask – через app.logger)​
circleci.com
. Рекомендуется создавать один logger и вызывать logger.debug(), logger.info(), logger.error() в ключевых местах (получение запроса, результаты валидации, ошибки). Например:
logger = logging.getLogger("waba_okdesk")
logger.debug(f"Получен запрос WhatsApp: {data}")
logger.info(f"Сообщение сохранено в диалоге {dialog_id}")
logger.error(f"Ошибка обработки Okdesk: {e}", exc_info=True)
Это соответствует подходу “используйте logging для записи событий в приложении”​
circleci.com
. Логи уровня DEBUG/INFO помогут отследить поток выполнения, а ERROR – оперативно заметить проблемы. Не следует логировать чувствительные данные (секреты, пароли) – логгеры настроены на вывод только нужной информации.
Автотесты (pytest)
Для обеспечения надёжности создаём тесты на pytest для ключевых сценариев:
WhatsApp webhook: моделируем POST-запрос с поддельной подписью (ожидаем 401) и с правильной подписью (ожидаем 200 и запись в БД). Пример: сгенерировать HMAC-SHA256, передать в заголовке X-Hub-Signature-256 и проверить, что в SQLite добавилась новая запись.
Webhook оплаты из 1С: симулируем POST с JSON-данными оплаты; проверяем, что после обработки обновился статус в БД или соответствующий лог появился.
Webhook закрытия заявки Okdesk: отправляем POST с Basic Auth (используя тестовые логин/пароль) и JSON-запросом. Проверяем, что сервис вернул 200 и, например, пометил заявку в БД как закрытую.
Тесты можно писать с помощью встроенного клиента фреймворка (например, TestClient FastAPI или app.test_client() в Flask). Настраиваем фикстуру с независимой SQLite (например, в памяти) и перед каждым тестом очищаем таблицы. Такой подход соответствует лучшим практикам модульного тестирования: независимость тестов и проверка каждой функции поведения API.
Docker и запуск проекта
Для удобства развёртывания проект помещается в контейнеры Docker. В docker-compose.yml обычно описывается один сервис приложения:
version: '3'
services:
  waba_okdesk:
    build: .
    image: waba_okdesk_app
    ports:
      - "8000:8000"  # например, FastAPI на 8000
    volumes:
      - .:/app  # монтирование кода при разработке
    environment:
      - APP_SECRET=${APP_SECRET}
      - OKDESK_USER=${OKDESK_USER}
      - OKDESK_PASS=${OKDESK_PASS}
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
Такой docker-compose.yml запускает веб-сервер с Python, настраивает переменные окружения (секреты берутся из .env) и монтирует код. (Если используется Flask, командой может быть flask run, FastAPI – uvicorn). Отдельный сервис БД не нужен – SQLite хранится в файле внутри контейнера или примонтированной папке. После сборки и запуска команда docker-compose up поднимет приложение, готовое принимать запросы.
README и документация
Файл README.md должен содержать инструкции по установке и запуску:
Требования: Python 3.x, Docker.
Перечень необходимых переменных окружения (например, APP_SECRET, OKDESK_USER, OKDESK_PASS).
Описание структуры проекта (Domain/Application/Infrastructure).
Как запустить через Docker Compose (docker-compose up --build).
Как выполнить тесты (например, pytest).
Пример curl-запросов к API (для проверки работы webhook’ов).
Подробное README поможет новым разработчикам и администраторам быстро развернуть систему.
Безопасность вебхуков
Особое внимание уделяем безопасности:
Проверка подписи WhatsApp: используем HMAC-SHA256 с секретом приложения и сравнение через hmac.compare_digest​
stackoverflow.com
, что защищает от подделки запросов.
Basic Auth Okdesk: требуем валидные логин/пароль, оформленные в заголовке Authorization: Basic ...​
developer.mozilla.org
.
Защита SQL: как упоминалось, используем плейсхолдеры в sqlite3​
docs.python.org
, чтобы предотвратить SQL-инъекции.
HTTPS (по возможности): в продакшене вебхуки должны приходить по защищённому каналу (Docker можно проксировать через HTTPS).
Логи: не сохранять секреты в логах и логировать ошибки через .error(..., exc_info=True).
Ограничение методов: все webhook-эндпоинты должны принимать только POST (и для верификации GET, если требуется) и возвращать 405 на неподдерживаемые методы.
Такой подход обеспечивает, что только авторизованные и корректно подписанные уведомления будут обработаны сервисом, а все подозрительные запросы – отклонены. Итог: проект организован в трех слоях (Domain/Application/Infrastructure)​
dev.to
, диалоги хранятся в SQLite (используя sqlite3​
docs.python.org
 и безопасные плейсхолдеры​
docs.python.org
), входящие webhook’и проверяются на подпись и авторизацию (см. примеры кода​
stackoverflow.com
​
developer.mozilla.org
), используется подробное логирование (см. рекомендации по Flask логам​
circleci.com
), написаны автотесты pytest для ключевых сценариев и подготовлены Docker Compose и README для удобства развёртывания. Всю работу приложения можно упаковать в ZIP-архив с исходниками и документацией для передачи и дальнейшего использования. Источники и материалы: официальная документация Python (sqlite3)​
docs.python.org
​
docs.python.org
, примеры проверки подписи вебхуков​
stackoverflow.com
, спецификация HTTP Basic Auth​
developer.mozilla.org
, гайд по логированию во Flask​
circleci.com
 и руководства по архитектуре (Domain/Application/Infrastructure)​
dev.to
.


## Setup
1. Copy `.env.example` to `.env` and fill values.
2. Run `docker-compose up --build -d`
3. Access FastAPI docs at `http://localhost:8000/docs`

## Testing
Run `pytest` to execute unit tests.


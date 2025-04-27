## Проект: fixit-exchange (Clean Architecture)

### 1. Abstract

Создать сервис для интеграции между собой различных систем учета и общения, построенный по принципам чистой архитектуры. Ключевая цель — отделить **чистый домен** (бизнес-логику) от технических деталей (API, БД, вебхуки), чтобы проект был легко расширяем, тестируем и сопровождён.

### 2. Overview

- **WhatsApp Webhook**: приём входящих сообщений из WABA, проверка подписи HMAC (`X-Hub-Signature-256`).
- **Flow Engine**: движок состояний диалога (flows), обрабатывающий любые события (`DomainEvent`): сообщения, статусы оплат, апдейты заявок.
- **Issue Creation**: создание тикетов в Okdesk через API и генерация ссылок для клиентов.
- **Accounting Sync**: (stub) приём статусов оплаты из 1С и уведомление системы.
- **Webhooks**: единый интерфейс для WABA и Okdesk (Basic Auth).
- **SQLite**: локальное хранение диалогов (таблица `dialogs`).
- **Logging**: `logger.debug/info/error` во всех ключевых местах.
- **Testing**: автотесты на pytest для основных сценариев.
- **Deployment**: контейнеризация через Docker + docker-compose.

### 3. Architecture

#### 3.1 Domain Layer
- **Entities**: `DomainEvent`, `User`, `Message`, `Issue`, `Dialog`, `DialogAction`.
- **Enums**: `State` (NEW, ASK_NAME, ASK_COMPANY, AWAITING_PAYMENT, PAID, DONE).
- **FlowRule** и **FlowEngine**: реализуют потоковые правила по состояниям и событиям.

#### 3.2 Application Layer
- **Ports (Interfaces)**:
  - `IMessageSender`: отправка сообщений.
  - `IDialogRepository`: хранение/загрузка диалогов.
  - `IIssueCreator`: создание тикетов.
  - `IAccountingConnector`: получение/отправка данных об оплате.
- **Use Case**: `ProcessEvent` — принимает `DomainEvent`, запускает `FlowEngine`, сохраняет диалог, выполняет действия (`reply`, `create_issue`).

#### 3.3 Infrastructure Layer
- **Adapters**:
  - `WhatsAppSender`: реализация `IMessageSender` через HTTP-запрос к WABA.
  - `SQLiteDialogRepo`: хранение в SQLite.
  - `OkdeskIssueCreator`: реализация `IIssueCreator` с Okdesk API и функцией `generate_ticket_link`.
  - `OneCConnector`: stub-адаптер для 1С (пока логгирует вызовы).
- **Web** (FastAPI): роутеры `/webhook/waba` и `/webhook/okdesk`, проверка подписи и Basic Auth.
- **Config**: загрузка `.env`, настройка `logger`.

### 4. Core Entities

| Класс             | Назначение                                                        |
|-------------------|-------------------------------------------------------------------|
| DomainEvent       | Обобщённое событие (type + payload)                              |
| User              | Пользователь (id, name)                                          |
| Message           | Входящее текстовое сообщение                                     |
| Issue             | Данные тикета (title, description)                               |
| DialogAction      | Действие: ответ или создание тикета                              |
| Dialog            | Состояние диалога (user_id, state, context)                      |
| FlowRule          | Правило перехода (state, predicate, next_state, actions)         |
| FlowEngine        | Применение правил к событиям и изменение состояния диалога       |

### 5. Flow Engine

1. **Инициализация**: индекс правил по исходному состоянию.
2. **start_new_dialog(user)**: создаёт `Dialog(state=NEW)`.
3. **next(dialog, event)**: проверяет список `FlowRule` для `dialog.state`, вызывает первый подходящий, обновляет `dialog.state`, возвращает список `DialogAction.with_context(context)`.

### 6. Ports & Adapters

- **Ports** определяют контракты, без конкретных реализаций.
- **Adapters** реализуют порты и содержат логику HTTP, SQL, HMAC.

### 7. Webhooks

- **WhatsApp**: POST `/webhook/waba`, проверка HMAC подписи по `app_secret`, парсинг JSON, создание `DomainEvent(EVENT.MESSAGE)`.
- **Okdesk**: POST `/webhook/okdesk`, Basic Auth (env: `OKDESK_USER`, `OKDESK_PASS`), парсинг JSON, `DomainEvent(EVENT.ISSUE_UPDATED)`.

### 8. Authentication & Authorization

- **WABA**: HMAC-SHA256 (`X-Hub-Signature-256`) vs `app_secret`.
- **Okdesk**: HTTP Basic Auth, сравнение логин:пароль из `.env`.

### 9. Logging

- Используется `logging` с уровнем DEBUG.
- В каждом адаптере и роутере: `logger.debug()`, `logger.info()`, `logger.error()` с `exc_info=True` для ошибок.

### 10. Testing

- Фреймворк: **pytest**.
- Тесты:
  - Webhook WABA: подпись неверная (401), правильная (200).
  - ProcessEvent: базовый поток.
  - Basic Auth Okdesk.
- Фикстуры: in-memory SQLite для `SQLiteDialogRepo`.

### 11. Deployment

- **Dockerfile** + **docker-compose.yml**
- Сервис FastAPI, порт 8000.
- Том для SQLite: `waba_db`.
- `.env` подключается через `env_file`.

---

*Этот документ — контракт и спецификация проекта. По нему мы будем проверять реализацию кода, тесты и конфигурацию.*


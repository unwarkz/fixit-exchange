import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
)
logger = logging.getLogger("waba_okdesk")

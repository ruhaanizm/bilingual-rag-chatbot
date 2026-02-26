from config import settings
from logger import get_logger
from utils import set_seed

logger = get_logger("TEST")

set_seed(settings.RANDOM_SEED)

logger.info(f"Project: {settings.PROJECT_NAME}")
logger.info(f"Raw Dir: {settings.RAW_DIR}")
logger.info("Deterministic seed set successfully.")
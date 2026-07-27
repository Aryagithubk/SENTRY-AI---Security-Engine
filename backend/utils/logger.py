import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "secureops.log"

# Configure custom formatter
class ColoredConsoleFormatter(logging.Formatter):
    """Custom formatter with visual stage indicators."""
    
    FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
    
    def format(self, record):
        formatter = logging.Formatter(self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

# Initialize logger
logger = logging.getLogger("SecureOps-AI")
logger.setLevel(logging.INFO)

# Remove existing handlers to avoid duplicates
if logger.hasHandlers():
    logger.handlers.clear()

# File Handler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredConsoleFormatter())
logger.addHandler(console_handler)

def log_stage(stage_name: str, message: str, level: str = "info"):
    """Helper to log multi-agent stages cleanly."""
    formatted_msg = f"[{stage_name.upper()}] {message}"
    if level == "warning":
        logger.warning(formatted_msg)
    elif level == "error":
        logger.error(formatted_msg)
    else:
        logger.info(formatted_msg)

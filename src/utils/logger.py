import logging
from pathlib import Path
from datetime import datetime
from src.configs.config import PATHES
import pytz
kst = pytz.timezone('Asia/Seoul')

class KSTPytzFormatter(logging.Formatter):
    """
        Des:
            Change the log time to Korean time
    """
    def formatTime(self, record, datefmt=None):
        kst = pytz.timezone('Asia/Seoul')
        converter = datetime.fromtimestamp(record.created, tz=pytz.UTC)
        converter = converter.astimezone(kst)
        return converter.strftime('%Y-%m-%d %H:%M:%S')
    
def setup_logger(script_name: str,
                 log_name:str=None, 
                 log_level: int = logging.INFO) -> logging.Logger:
    """
    Des:
        Set up a logger that includes both file and console handlers.
    Args:
        script_name (str): The name of the script (used for both logger name and directory)
        - example ) script_name = Path(__file__).stem
        log_level (int): Logging level (default: logging.INFO)
    Returns:
        logging.Logger: The configured logger instance
    """
    # Log name
    log_name = script_name if log_name is None else log_name
        
    # Create log directory
    log_dir = Path(PATHES["log"]) / script_name
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create log file path (include date)
    current_date = datetime.now(kst).strftime("%Y%m%d")
    log_file = log_dir / f"{log_name}_{current_date}.log"

    # Set up logger
    logger = logging.getLogger(script_name)
    logger.setLevel(log_level)

    # Prevent duplicate handlers
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        formatter = KSTPytzFormatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

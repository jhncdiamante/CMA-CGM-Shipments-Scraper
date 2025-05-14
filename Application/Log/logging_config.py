# logger_config.py
import logging

def setup_logger():
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            filename='app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s\n',
            datefmt='%Y-%m-%d %H:%M:%S',
            filemode='w'
        )
    return logging

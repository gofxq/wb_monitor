# plog/handlers.py

import logging

class LarkLogHandler(logging.Handler):
    def __init__(self, bot, level=logging.WARNING):
        super().__init__(level)
        self.bot = bot

    def emit(self, record):
        if record.levelno >= self.level:
            log_entry = self.format(record)
            self.bot.sendmsg(f"Alert from {record.name}", log_entry)

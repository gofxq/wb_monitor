# plog/__init__.py
from lark_boot_webhook_msg import LarkBot
from .logger import setup_logger
import logging

# 设置一个默认的全局日志器
_default_logger = setup_logger()


# 定义简易接口
def debug(message):
    _default_logger.debug(message)


def info(message):
    _default_logger.info(message)


def warning(message):
    _default_logger.warning(message)


def error(message):
    _default_logger.error(message)


def critical(message):
    _default_logger.critical(message)

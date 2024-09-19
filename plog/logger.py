import logging
import logging.handlers
import os
import tempfile

class ColoredFormatter(logging.Formatter):
    # ANSI escape sequences for coloring
    COLORS = {
        'DEBUG': "\033[34m",      # Blue
        'INFO': "\033[32m",       # Green
        'WARNING': "\033[33m",    # Yellow
        'ERROR': "\033[91m",      # Red
        'CRITICAL': "\033[31;1m",   # Purple
    }
    RESET = "\033[0m"

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s{self.RESET}"
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(name='plog', 
                    log_file=None, 
                    level=logging.DEBUG, 
                    format='%(asctime)s [%(levelname)s] %(message)s', 
                    when='midnight',
                    interval=1, 
                    backupCount=7):
    """配置并获取一个日志器"""
    # 如果未提供日志文件路径，使用系统临时目录
    if log_file is None:
        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, f'{name}.log')
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    print(f'log_file:{log_file}')
    
    formatter = logging.Formatter(format)


    # 文件处理器
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when=when, interval=interval, backupCount=backupCount)
    file_handler.setFormatter(formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 创建带颜色的 Formatter
    colored_formatter = ColoredFormatter()
    file_handler.setFormatter(colored_formatter)
    console_handler.setFormatter(colored_formatter)

    # 创建并配置日志器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


if __name__ == '__main__':
    logger = setup_logger(name='demo')
    # 使用日志器记录信息
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')

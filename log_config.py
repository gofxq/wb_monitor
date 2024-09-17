import logging
import logging.handlers
import os
import tempfile

def setup_logger(name, 
                    log_file=None, 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
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

    # 创建处理器，使用时间轮转日志
    handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when=when, interval=interval, backupCount=backupCount)
    handler.setFormatter(formatter)

    # 创建并配置日志器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # 防止日志重复
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

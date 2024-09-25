from datetime import datetime
import time
from app.wb_monitor import check


def sleep_until_next_period(period_seconds):
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    next_period = (seconds_since_midnight // period_seconds + 1) * period_seconds
    sleep_duration = next_period - seconds_since_midnight
    time.sleep(sleep_duration)

if __name__ == "__main__":
    period_seconds = 600  # 定义周期长度

    while True:
        try:
            check()
            sleep_until_next_period(period_seconds)
        except Exception as e:
            print(f"执行main函数时发生异常：{e}")
            # 可选：在此处进行一些恢复或清理工作
            continue

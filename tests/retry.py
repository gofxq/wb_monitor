import time
from functools import wraps

from tenacity import retry, stop_after_attempt, wait_fixed

# 使用装饰器
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def test_func(x):
    # print(x)
    if x == 0:
        raise ValueError("x不能为0!")
    return 10 / x


if __name__ == "__main__":
    # 测试函数
    print(test_func(2))  # 正常运行
    print(test_func(0))  # 将触发重试
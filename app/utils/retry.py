import time
from functools import wraps

def retry(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < n:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"函数出错，正在尝试第{attempts + 1}次重试...")
                    attempts += 1
                    time.sleep(1)  # 可以设置等待时间
            return None  # 如果所有重试都失败了，可以返回特定的值或者抛出异常
        return wrapper
    return decorator

# 使用装饰器
@retry(3)
def test_func(x):
    print(x)
    if x == 0:
        raise ValueError("x不能为0!")
    return 10 / x


if __name__ == "__main__":
    # 测试函数
    print(test_func(2))  # 正常运行
    print(test_func(0))  # 将触发重试
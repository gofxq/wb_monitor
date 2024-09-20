## tenacity 使用指南

`tenacity` 是一个 Python 库，用于简化在失败后重试函数或方法调用的过程。它非常适用于需要处理网络请求、外部资源访问或任何有可能失败且需要重试的操作。使用 `retry` 装饰器可以非常灵活地控制重试逻辑，例如重试次数、等待时间、触发重试的异常类型等。

你可以使用以下命令来安装 tenacity：

```bash
pip install tenacity
```

### 使用 `retry` 装饰器的基本语法：

```python
from tenacity import retry

@retry
def some_function_that_might_fail():
    # 这里是可能会失败的代码逻辑，比如网络请求
    pass
```

在这个基础上，你可以通过传递参数给 `retry` 装饰器来自定义重试策略。

### 常用参数：

- `stop`: 指定何时停止重试。例如，停止在尝试了一定次数后（`stop_after_attempt(n)`）或停止在经过一定时间后（`stop_after_delay(n)`）。
- `wait`: 指定两次重试之间的等待时间。例如，固定等待（`wait_fixed(millis)`）、增加等待时间（`wait_exponential(multiplier=1, max=10)`）等。
- `retry`: 指定在什么条件下重试。例如，根据异常类型（`retry_on_exception()`）或根据返回值（`retry_if_result()`）。
- `before`: 在重试之前执行的回调函数。
- `after`: 在重试之后执行的回调函数。
- `reraise`: 重试结束后是否抛出异常。

### 使用注意事项：

1. **资源管理**：确保在使用重试时不会导致资源泄漏，例如文件描述符、网络连接等。
2. **幂等性**：被重试的操作应该是幂等的，意味着多次执行同一操作的结果应该相同，以避免副作用。
3. **性能影响**：重试可能会显著增加系统负载和响应时间。合理配置重试参数，确保系统性能不会受到严重影响。
4. **异常处理**：需要仔细考虑哪些异常类型应该触发重试。不是所有的异常都值得重试，例如，程序逻辑错误通常不应该重试。
5. **终止条件**：应当明确设置重试的终止条件，避免无限重试。

### 实际应用示例：

```python
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_data():
    # 从网络资源获取数据，可能会抛出异常
    return "Some data"

try:
    result = fetch_data()
except RetryError as e:
    print("Failed after several attempts:", e)
```

在这个示例中，如果 `fetch_data` 函数失败，它会在每次失败后等待2秒钟，最多重试3次。如果所有尝试都失败了，将抛出一个 `RetryError` 异常。

总之，`tenacity` 提供了强大而灵活的重试机制，可以显著增强应用程序在面对失败操作时的鲁棒性。
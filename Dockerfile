# 使用官方Python镜像。你可以选择特定的Python版本
FROM python:3.12-slim

# 设置工作目录为根目录
WORKDIR /

# 将app目录下的文件复制到容器的/app目录中
COPY app /app

# 将 config_demo.yml 文件复制到/app目录并重命名为 config.yml
COPY config_demo.yml config.yml
COPY requirements.txt requirements.txt

# 安装任何需要的包和推荐的安全性能工具
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 容器启动时执行的命令，注意更改为从app模块运行checker
CMD ["python", "-m", "app.checker"]

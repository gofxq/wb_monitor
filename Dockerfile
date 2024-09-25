# 使用官方 Python 运行环境作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /

# 复制依赖文件到容器中
COPY requirements.txt .
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置时区，便于定时任务按本地时间执行
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 运行定时任务
CMD ["python","-m", "app.wb_monitor"]

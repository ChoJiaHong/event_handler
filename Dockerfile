FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製當前目錄到容器中
COPY . /app

# 安裝依賴
RUN pip install --upgrade pip \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# 預設啟動 shell（可改為 entrypoint.py）
CMD [ "bash" ]

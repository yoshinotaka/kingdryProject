FROM python:3.9-slim as builder

WORKDIR /app

# システム依存関係とGitをインストール（WeasyPrint関連を追加）
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY app.py .
COPY models.py .
COPY forms.py .
COPY templates/ templates/
COPY gunicorn_config.py .

# バッチ処理ファイルのコピー
COPY batch/ batch/

# 必要なディレクトリの作成
RUN mkdir -p batch/download batch/logs  && \
chmod -R 777 batch/download batch/logs

EXPOSE 5000

CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]

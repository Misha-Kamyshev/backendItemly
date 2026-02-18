FROM python:3.12-slim
ENV TZ=Asia/Vladivostok

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc python3-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 8000

COPY app ./app
COPY static ./static

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]

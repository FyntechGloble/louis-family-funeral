FROM python:3.12-slim
WORKDIR /srv
RUN apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -r -u 10001 appuser && mkdir -p /data && chown -R appuser:appuser /data
COPY app ./app
COPY docker-entrypoint.sh /usr/local/bin/family-entrypoint
RUN chmod 755 /usr/local/bin/family-entrypoint
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/family-entrypoint"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]

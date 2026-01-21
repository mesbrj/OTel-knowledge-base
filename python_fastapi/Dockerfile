FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env .env

EXPOSE 8080

# Set PYTHONPATH so src modules can be imported
ENV PYTHONPATH=/app/src

CMD ["python", "/app/src/main.py"]

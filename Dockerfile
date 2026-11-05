FROM python:3.11-slim

WORKDIR /app

COPY Docker-requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY salary_model ./salary_model

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

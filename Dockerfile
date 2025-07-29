FROM python:3.11-slim-bullseye

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY .env .env

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]

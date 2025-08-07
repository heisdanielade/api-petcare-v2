FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

COPY ./start.sh ./start.sh

RUN chmod +x ./start.sh

CMD ["./start.sh"]

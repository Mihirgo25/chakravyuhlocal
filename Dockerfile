FROM python:3-slim as base

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install

RUN apt-get install -y \
  dos2unix \
  libpq-dev \
  libmariadb-dev-compat \
  libmariadb-dev \
  gcc \
  && apt-get clean

RUN pip3 install --upgrade pip

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY .env ./

WORKDIR /src

COPY ./src /src

EXPOSE 8110
EXPOSE 8111

FROM base as rms
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port", "8110"]

From base as celery
CMD ["celery", "-A", "celery_worker.celery", "flower", "--port=5555"]

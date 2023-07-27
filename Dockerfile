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

#COPY .env ./

WORKDIR /src

COPY ./src /src

EXPOSE 8110
EXPOSE 8111

FROM base as rms
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8110", "--preload", "--access-logfile", "-"]

FROM base as celery
CMD ["celery" ,"-A" ,"celery_worker.celery" , "worker" ,"-B", "--concurrency", "5", "--loglevel=info" , "-Q" , "communication,critical,low,fcl_freight_rate,bulk_operations"]

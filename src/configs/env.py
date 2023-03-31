import os
from dotenv import load_dotenv
load_dotenv()

# ENV
APP_ENV=os.getenv("APP_ENV")

# Main DB connection
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")

# RAILS DB connection

RAILS_DATABASE_NAME = os.getenv("RAILS_DATABASE_NAME")
RAILS_DATABASE_USER = os.getenv("RAILS_DATABASE_USER")
RAILS_DATABASE_PASSWORD = os.getenv("RAILS_DATABASE_PASSWORD")
RAILS_DATABASE_HOST = os.getenv("RAILS_DATABASE_HOST")
RAILS_DATABASE_PORT = os.getenv("RAILS_DATABASE_PORT")

# microservice
RUBY_ADDRESS_URL=os.getenv("RUBY_ADDRESS_URL")
RUBY_AUTHTOKEN = "25d1237f-e573-4185-bc80-c9d1da78625b"  #os.getenv('RUBY_AUTHTOKEN')
RUBY_AUTHSCOPE = os.getenv('RUBY_AUTHSCOPE')
RUBY_AUTHSCOPEID = "8d8a499e-0c84-4950-b192-05c324d3c6c8"  #os.getenv('RUBY_AUTHSCOPEID')


COMMON_SERVICE_PORT=os.getenv("COMMON_SERVICE_PORT")
AUTH_SERVICE_PORT=os.getenv("AUTH_SERVICE_PORT")
COGOMAPS_SERVICE_PORT =os.getenv("COGOMAPS_SERVICE_PORT")
SPOT_SEARCH_PORT=os.getenv("SPOT_SEARCH_PORT")
CHECKOUT_PORT=os.getenv("CHECKOUT_PORT")
INTERNAL_NLB=os.getenv("INTERNAL_NLB")

# Redis
REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=os.getenv("REDIS_PORT")
REDIS_USERNAME=os.getenv("REDIS_USERNAME")
REDIS_PASSWORD=os.getenv("REDIS_PASSWORD")

CELERY_REDIS_URL = "rediss://{}:{}@{}:{}/0?ssl_cert_reqs=CERT_NONE".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_S3_REGION_NAME = "ap-south-1"

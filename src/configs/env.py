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
RUBY_AUTHTOKEN = os.getenv('RUBY_AUTHTOKEN')
RUBY_AUTHSCOPE = os.getenv('RUBY_AUTHSCOPE')
RUBY_AUTHSCOPEID = os.getenv('RUBY_AUTHSCOPEID')


COMMON_SERVICE_PORT=os.getenv("COMMON_SERVICE_PORT")
AUTH_SERVICE_PORT=os.getenv("AUTH_SERVICE_PORT")
COGOMAPS_SERVICE_PORT =os.getenv("COGOMAPS_SERVICE_PORT")
INTERNAL_NLB=os.getenv("INTERNAL_NLB")

# Redis
REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=os.getenv("REDIS_PORT")
REDIS_USERNAME=os.getenv("REDIS_USERNAME")
REDIS_PASSWORD=os.getenv("REDIS_PASSWORD")

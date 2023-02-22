import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
RUBY_ADDRESS_URL=os.getenv("RUBY_ADDRESS_URL")
RUBY_AUTHTOKEN = os.getenv('RUBY_AUTHTOKEN')
RUBY_AUTHSCOPE = os.getenv('RUBY_AUTHSCOPE')
RUBY_AUTHSCOPEID = os.getenv('RUBY_AUTHSCOPEID')
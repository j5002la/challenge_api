import os
from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# Configure database connection
app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DB connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
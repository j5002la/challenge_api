from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
DATABASE_URI = 'postgresql://user:password@localhost:5432/globant_challenge'  # Update credentials
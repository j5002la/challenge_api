import os
from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# Configure database connection
app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
# DB connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def load_sql_query(filename):
    """Load SQL query from file"""
    try:
        query_path = os.path.join(BASE_DIR, 'queries', filename)
        with open(query_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise RuntimeError(f"SQL file {filename} not found")
    except Exception as e:
        raise RuntimeError(f"Error loading SQL file: {str(e)}")

@app.route('/metrics/hires_by_quarter', methods=['GET'])
def get_hires_by_quarter():
    session = Session()
    try:
        query = text(load_sql_query('2021perQuarter.sql'))
        result = session.execute(query)
        data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/metrics/departments_above_average', methods=['GET'])
def get_departments_above_average():
    session = Session()
    try:
        query = text(load_sql_query('AboveAVG2021.sql'))
        result = session.execute(query)
        data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)
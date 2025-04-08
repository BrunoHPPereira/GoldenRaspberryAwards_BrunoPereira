from flask import Flask, jsonify
import sqlite3
import csv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all API routes with explicit configuration


# Database setup
def init_db():
    connection = sqlite3.connect(':memory:', check_same_thread=False) #create a connection to the in-memory database
    c = connection.cursor()

    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INT,
            title TEXT,
            studios TEXT,
            winner BOOLEAN
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS producers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS movie_producers (
            movie_id INTEGER,
            producer_id INTEGER,
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            FOREIGN KEY (producer_id) REFERENCES producers (id),
            PRIMARY KEY (movie_id, producer_id)
        )
    ''')

    connection.commit()
    return connection


def load_csv_data(connection, csv_file):
    c = connection.cursor()

    # Read CSV file
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter=';')

        for row in csv_reader:
            # Insert movie
            winner = 1 if row['winner'].lower() == 'yes' else 0
            c.execute('INSERT INTO movies (year, title, studios, winner) VALUES (?, ?, ?, ?)',
                      (row['year'], row['title'], row['studios'], winner))

            movie_id = c.lastrowid

            # Process producers (can be multiple per movie)
            producers_list = [p.strip() for p in row['producers'].split(',') if p.strip()]
            for producer_name in producers_list:
                # Check if producer exists
                c.execute('SELECT id FROM producers WHERE name = ?', (producer_name,))
                producer = c.fetchone()

                if producer:
                    producer_id = producer[0]
                else:
                    c.execute('INSERT INTO producers (name) VALUES (?)', (producer_name,))
                    producer_id = c.lastrowid

                # Link movie to producer
                c.execute('INSERT INTO movie_producers (movie_id, producer_id) VALUES (?, ?)',
                          (movie_id, producer_id))




def get_producer_intervals():
    conn = db_connection
    c = conn.cursor()

    # Get all producers who won at least twice
    c.execute('''
        SELECT p.id, p.name 
        FROM producers p
        JOIN movie_producers mp ON p.id = mp.producer_id
        JOIN movies m ON mp.movie_id = m.id
        WHERE m.winner = 1
        GROUP BY p.id
        HAVING COUNT(DISTINCT m.id) >= 2
    ''')

    producers = c.fetchall()

    results = {
        "max": [],
        "min": []
    }

    max_interval = 0
    min_interval = float('inf')

    for producer_id, producer_name in producers:
        # Get all winning years for this producer
        c.execute('''
            SELECT m.year
            FROM movies m
            JOIN movie_producers mp ON m.id = mp.movie_id
            WHERE mp.producer_id = ? AND m.winner = 1
            ORDER BY m.year
        ''', (producer_id,))

        years = [row[0] for row in c.fetchall()]

        # Calculate intervals between consecutive wins
        for i in range(1, len(years)):
            interval = years[i] - years[i -1]

            if interval > max_interval:
                max_interval = interval
                results["max"] = [{
                    "producer": producer_name,
                    "interval": interval,
                    "previousWin": years[i - 1],
                    "followingWin": years[i]
                }]
            elif interval == max_interval:
                results["max"].append({
                    "producer": producer_name,
                    "interval": interval,
                    "previousWin": years[i - 1],
                    "followingWin": years[i]
                })

            if interval < min_interval:
                min_interval = interval
                results["min"] = [{
                    "producer": producer_name,
                    "interval": interval,
                    "previousWin": years[i - 1],
                    "followingWin": years[i]
                }]
            elif interval == min_interval:
                results["min"].append({
                    "producer": producer_name,
                    "interval": interval,
                    "previousWin": years[i - 1],
                    "followingWin": years[i]
                })

    return results


# Initialize database and load data
db_connection = init_db()
csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'movielist.csv')
load_csv_data(db_connection, csv_path)


@app.route('/api/producers/awards-interval', methods=['GET'])
def producer_intervals():
    try:
        results = get_producer_intervals()
        # Explicitly set content type and CORS headers
        response = jsonify(results)
        response.headers.add('Content-Type', 'application/json')
        return response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
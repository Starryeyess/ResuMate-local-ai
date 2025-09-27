import hashlib
import sqlite3
import pandas as pd
import json

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password):
    """Adds a new user to the database with a SHA-256 hashed password."""
    conn = db_connect()
    c = conn.cursor()
    try:
        # This function now correctly uses our new hashing method
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists
    finally:
        conn.close()


def db_connect():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('proresume.db', check_same_thread=False)
    return conn

def create_tables():
    """Creates the necessary database tables if they don't exist."""
    conn = db_connect()
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    # Analysis history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            analysis_type TEXT,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()


def log_analysis(username, analysis_type, result):
    """Logs a new analysis result to the history table for a user."""
    conn = db_connect()
    c = conn.cursor()
    c.execute("INSERT INTO history (username, analysis_type, result) VALUES (?, ?, ?)", (username, analysis_type, result))
    conn.commit()
    conn.close()

def get_user_history(username):
    """Retrieves all analysis history for a given user."""
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT analysis_type, result, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC", (username,))
    history = c.fetchall()
    conn.close()
    return history
def get_history_for_dashboard(username):
    """Retrieves history and formats it as a Pandas DataFrame for visualization."""
    conn = db_connect()
    # Query to get data, focusing on ATS score which we'll parse from the JSON result
    query = """
    SELECT 
        timestamp, 
        analysis_type, 
        result 
    FROM history 
    WHERE username = ? 
    ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, params=(username,))
    conn.close()

    # Process the data to extract scores
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        def extract_score(row):
            if row['analysis_type'] != 'ATS Checker':
                return None
            try:
                # The result is stored as a JSON string, so we load it
                data = json.loads(row['result'])
                return data.get('ats_score')
            except (json.JSONDecodeError, TypeError):
                return None

        df['ats_score'] = df.apply(extract_score, axis=1)
    return df

# Initialize the database and tables when the module is first imported
create_tables()
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
    # Users table and History table schemas are fine as they are.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
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

def get_history_for_dashboard(username):
    """
    Retrieves history and formats it as a Pandas DataFrame for visualization.
    This function is updated to extract both match_score and ats_score.
    """
    conn = db_connect()
    query = "SELECT timestamp, analysis_type, result FROM history WHERE username = ? ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn, params=(username,))
    conn.close()

    if df.empty:
        # Return an empty DataFrame with the expected columns if there's no history
        return pd.DataFrame(columns=['timestamp', 'match_score', 'ats_score'])

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    def extract_score(result_str, score_type):
        """Safely extracts a score from a JSON string in the result column."""
        try:
            # The result is stored as a JSON string, so we load it
            data = json.loads(result_str)
            return data.get(score_type) # .get() safely returns None if key is not found
        except (json.JSONDecodeError, TypeError):
            return None

    # Create columns for each score type by applying the extraction function
    df['match_score'] = df.apply(lambda row: extract_score(row['result'], 'match_score') if row['analysis_type'] == 'Resume Matcher' else None, axis=1)
    df['ats_score'] = df.apply(lambda row: extract_score(row['result'], 'ats_score') if row['analysis_type'] == 'ATS Checker' else None, axis=1)
    
    return df

# Initialize the database and tables when the module is first imported
create_tables()


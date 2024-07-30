import sqlite3
import json


def save_cookie(cookie_value):
    # Connect to the SQLite database
    conn = sqlite3.connect("cookies.sql")

    # Create a cursor object
    cursor = conn.cursor()
    # Create the cookies table if it does not exist
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cookies (id INTEGER PRIMARY KEY AUTOINCREMENT, cookie_value TEXT)"
    )

    # Insert the cookie_value into the cookies_table
    cursor.execute(
        "INSERT INTO cookies (cookie_value) VALUES (?)", (json.dumps(cookie_value),)
    )

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()


def load_cookie():
    # Connect to the SQLite database
    conn = sqlite3.connect("cookies.sql")

    # Create a cursor object
    cursor = conn.cursor()

    # Execute SELECT query to fetch the latest cookie_text
    cursor.execute("""SELECT cookie_value FROM cookies ORDER BY id DESC LIMIT 1""")

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Extract the cookie value if result is not None
    return json.loads(result[0]) if result else None

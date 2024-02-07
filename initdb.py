import sqlite3

conn = sqlite3.connect('quotes.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS quotes
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               quote TEXT NOT NULL,
               url TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS already_sent_quotes
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             quote TEXT NOT NULL,
             url TEXT NOT NULL)''')

conn.commit()
conn.close()

print("Database and tables created successfully.")
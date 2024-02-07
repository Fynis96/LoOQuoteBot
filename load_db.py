import sqlite3
import json
from quotes import data


conn = sqlite3.connect('quotes.db')

cursor = conn.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS quotes
               (id INTEGER PRIMARY KEY, quote TEXT, url TEXT)
               ''')

for item in data:
  cursor.execute('INSERT INTO quotes (quote, url) VALUES (?, ?)', (item['quote'], item['url']))
  
conn.commit()
conn.close()

print('Database created successfully')
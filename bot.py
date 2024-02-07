import discord
import sqlite3
import os
import random
import re
import spacy
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

max_length = 390

nlp = spacy.load("en_core_web_sm")

def refill_quotes(conn):
  print("checking if quotes table is empty...")
  cursor = conn.cursor()

  # Check if the quotes table is empty
  cursor.execute('SELECT COUNT(*) FROM quotes')
  if cursor.fetchone()[0] == 0:
    print("Quotes table is empty. Refilling...")
    # Move all quotes back to the quotes table
    cursor.execute('''
        INSERT INTO quotes (quote, url)
        SELECT quote, url FROM already_sent_quotes
    ''')

    # Empty the already_sent_quotes table
    cursor.execute('DELETE FROM already_sent_quotes')

    conn.commit()
    print("Quotes table refilled successfully")
        
def move_to_already_sent(conn, quote_id):
  cursor = conn.cursor()
  print("Moving quote to already_sent_quotes table")

  # Copy the quote to the already_sent_quotes table
  cursor.execute('''
      INSERT INTO already_sent_quotes (id, quote, url)
      SELECT id, quote, url FROM quotes WHERE id = ?
  ''', (quote_id,))

  # Delete the quote from the quotes table
  cursor.execute('DELETE FROM quotes WHERE id = ?', (quote_id,))

  conn.commit()

  print("Quote moved successfully")
    
def get_random_quote(conn):
  cursor = conn.cursor()
  cursor.execute('SELECT id, quote, url FROM quotes ORDER BY RANDOM() LIMIT 1')
  return cursor.fetchone()

def clean_quote(quote):
    cleaned_quote = quote.strip()
    cleaned_quote = re.sub(r'\s+', ' ', cleaned_quote)  # Normalize spaces
    cleaned_quote = cleaned_quote.replace("‘", "'").replace("’", "'").replace('“', '"').replace('”', '"')
    cleaned_quote = cleaned_quote.replace('--', '—')
    cleaned_quote = re.sub(r'\[.*?\]', '', cleaned_quote)
    
    pattern = re.compile(r'(?<!^)(?=(Q\'uo:|Ra:|Questioner:))', re.MULTILINE)
    cleaned_quote = pattern.sub('\n', cleaned_quote)
    cleaned_quote = re.sub(r'(Q\'uo:|Ra:|Questioner:)', r'**\1**', cleaned_quote)  # Bold the entities and questioner
    cleaned_quote = re.sub(r'(\n\*\*Q\'uo:\*\*|\n\*\*Ra:\*\*)', r'\n    \1', cleaned_quote)  # Indent responses
    
    return cleaned_quote

def split_paragraphs_nlp(text, max_length=390):
    doc = nlp(text)
    paragraphs = []
    current_paragraph = ""
    
    for sent in doc.sents:
        if len(current_paragraph) + len(sent.text) <= max_length:
            current_paragraph += " " + sent.text
        else:
            paragraphs.append(current_paragraph.strip())
            current_paragraph = sent.text
    paragraphs.append(current_paragraph.strip())  # Add the last paragraph
    
    return "\n\n".join(paragraphs)

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  channel = bot.get_channel(CHANNEL_ID)
  if channel:
    conn = sqlite3.connect('quotes.db')
    refill_quotes(conn)
    quote_data = get_random_quote(conn)
    if quote_data:
      quote_id, quote, url = quote_data
      cleaner_quote = clean_quote(quote)
      cleaned_quote = split_paragraphs_nlp(cleaner_quote, max_length)
      message = f"**Quote:** {cleaned_quote}\n\n**URL:** {url}"
      
      await channel.send(message)
      
      move_to_already_sent(conn, quote_id)
    else:
      print("No quotes found in the database.")
    
    conn.close()
      
    await bot.close()


bot.run(TOKEN)

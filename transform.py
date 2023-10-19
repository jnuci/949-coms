import pandas as pd
import psycopg2
import re
import html
from textblob import Word
from config import DB_PASS, LOCALHOST

def preprocess(text):
    
    # remove bracket enclosed elements (links, linebreaks, timestamps)
    text = re.sub(r'<[^>]+>', '', text)
    
    # remove time entries
    text = re.sub(r'\b\d{1,2}:\d{2}\b', '', text)
    
    # deal with these annoying single and double quotes
    text = text.replace('’', '\'')

    # deal with some punctuation
    text = re.sub(r'[@#$%^*()]', '', text)
    text = text.replace('-', ' ')
    text = text.replace('.', ' . ')
    text = text.replace('?', ' ? ')
    text = text.replace('!', ' ! ')
    text = text.replace(',', ' , ')
    text = text.replace('"', ' " ')

    # multiple spaces
    text = re.sub(r'\s+', ' ', text)

    #repeated characters
    rx = re.compile(r'([^\W\d_])\1{2,}')
    re.sub(r'[^\W\d_]+', lambda x: Word(rx.sub(r'\1\1', x.group())).correct() if rx.search(x.group()) else x.group(), text)

    # remove not alpahumeric characters, leaving punctuation.
    text = ''.join([char for char in text if (char.isalnum() or char.isspace() or (char in ["'", ".", ",", "!", "?", "\"", "<", "@"]))])

    text = text.strip()

    text = text.lower()
    
    text = text.replace('...', '')

    return text


def main():
    conn = psycopg2.connect(
        host = LOCALHOST,
        port = 5432,
        database = 'youtube_comments',
        user = 'postgres',
        password = DB_PASS,
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments_raw WHERE comment_id NOT IN (SELECT comment_id FROM comments_cleaned)")

    data = cursor.fetchall()

    data = pd.DataFrame(data, columns = ['video_id', 'comment_id', 'content', 'published', 'username', 'profile_image', 'likes'])

    data['content'] = [html.unescape(comment) for comment in data['content']]

    data['content'] = data['content'].apply(preprocess)

    data = data[data['content'] != '']

    for row in data.values:
        cursor.execute("INSERT INTO comments_cleaned (video_id, comment_id, content, published, username, profile_image, likes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        
        conn.commit()

    cursor.execute("SELECT count(comment_id) FROM comments_cleaned")
    count = cursor.fetchall()
    print(f"{count[0][0]} total comments ready for analytics!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
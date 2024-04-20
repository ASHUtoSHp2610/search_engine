import sqlite3
import zipfile
import io
import pandas as pd
import re
import random
from sentence_transformers import SentenceTransformer
import numpy as np
import chromadb

db_name = 'eng_subtitles_database.db'

def data_read(path, percent=50):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info('zipfiles')")
    rows = cursor.fetchall()
    total_rows = None
    for row in rows:
        if row[1] == 'num':
            total_rows = row[2]
            break
    if total_rows is None:
        raise ValueError("Column 'num' not found in table 'zipfiles'")
    cursor.execute(f"SELECT COUNT(*) FROM zipfiles")
    total_rows = cursor.fetchone()[0]
    limit = int(total_rows * (percent / 100))
    df = pd.read_sql_query(f"SELECT * FROM zipfiles LIMIT {limit}", conn)
    return df

cnt = 0
def decode_method(data):
    global cnt
    cnt += 1
    with io.BytesIO(data) as f:
        with zipfile.ZipFile(f, 'r') as zip_file:
            subtitle_content = zip_file.read(zip_file.namelist()[0])
    return subtitle_content.decode('latin-1')

def clean_text(text):
    text = text.strip()
    text = re.sub(r'^\d+\s', '', text)
    text = re.sub(r'\r\n', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', text)
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text

def clean_movie(input_string):
    clean_string = re.sub(r'\([^()]*\)', '', input_string)
    clean_string = clean_string.replace('.', ' ')
    clean_string = clean_string.title()
    clean_string = re.sub(r'\s*Eng.*$', '', clean_string)
    return clean_string

def random_sampling(data, sampling_ratio=0.3):
    num_samples = int(len(data) * sampling_ratio)
    sampled_indices = random.sample(range(len(data)), num_samples)
    sampled_data = data.iloc[sampled_indices]
    return sampled_data

def generate_embeddings(texts):
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    embeddings = model.encode(texts)
    return embeddings

def document_chunker(data, chunk_size=500, overlap_size=50):
    tokens = data
    chunks = []
    start_idx = 0
    while start_idx < len(tokens):
        end_idx = min(start_idx + chunk_size, len(tokens))
        chunk = ' '.join(tokens[start_idx:end_idx])
        chunks.append(chunk)
        start_idx += chunk_size - overlap_size
    return chunks

df = data_read(db_name)
df['file_content'] = df['content'].apply(decode_method)
df['file_content'] = df['file_content'].apply(clean_text)
df['name'] = df['name'].apply(clean_movie)
df = df.rename(columns={'num': 'movie_num', 'name': 'movie_name', 'file_content': 'subtitle'}).drop(['content'], axis=1)
sampled_data = random_sampling(df)



corpus_embeddings = generate_embeddings(sampled_data['subtitle'].tolist())

# Connect to ChromaDB
client = chromadb.PersistentClient(path="subtitle")
collection = client.get_or_create_collection(name="subtitle")
# # Convert numpy array embeddings to lists


# #======================================================================
# corpus_embeddings = np.load('embeddings.npy')
# #==============================================================

corpus_embeddings = corpus_embeddings.tolist()

# # Insert documents into ChromaDB collection
for index, row in sampled_data.iterrows():
    document_id = str(row['movie_num'])  # Use a unique identifier for each document
    document_text = row['subtitle']
    # document_embedding = corpus_embeddings[index % len(corpus_embeddings)]  # Assuming embeddings are aligned with the rows
    
    # ------------------------------------------------------------------------
    corpus_index = index % len(corpus_embeddings)
    document_embedding = corpus_embeddings[corpus_index]
    #--------------------------------------------------------------------------
    metadata = {'movie_name': row['movie_name']}

    # Insert document into ChromaDB collection
    collection.add(ids=document_id, documents=[document_text], embeddings=[document_embedding], metadatas=[metadata])


print("Insertion into ChromaDB collection complete")



query = 'The Message'
query = generate_embeddings(query)

results = collection.query(
    query_embeddings=query.tolist(),
    n_results=2
)

print(results)
from flask import Flask, request, render_template, jsonify
from scipy.spatial.distance import cosine
import chromadb
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Connect to ChromaDB and get the collection
client = chromadb.PersistentClient(path="subtitle")
collection = client.get_collection(name="subtitle")

# Initialize the SentenceTransformer model
model = SentenceTransformer('bert-base-nli-mean-tokens', device='cpu')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    # Get the query string from the request
    query = request.args.get('query')

    # Ensure query is treated as a string
    query = str(query)

    def generate_embeddings(texts):
        model = SentenceTransformer('bert-base-nli-mean-tokens')
        embeddings = model.encode(texts)
        return embeddings

    query = generate_embeddings(query)

    results = collection.query(
        query_embeddings=query.tolist(),
        n_results=20
    )

    # Process search results
    top_documents = []
    for i in range(len(results['ids'])):
        document_ids = results['ids'][i]
        movie_names = [metadata['movie_name'] for metadata in results['metadatas'][i]]
        subtitles = results['documents'][i]
    
        for j, (movie_name, subtitle) in enumerate(zip(movie_names, subtitles)):
            # Retrieve the document embedding directly using the first document ID
            document_embedding = collection.get(document_ids[j])['embeddings']
    
            if document_embedding is not None:
                # Flatten the query and document embedding arrays
                query_flat = query.flatten()
                document_embedding_flat = document_embedding.flatten()
    
                # Calculate cosine similarity
                similarity_score = 1 - cosine(query_flat, document_embedding_flat)
            else:
                # Set similarity score to 0 if document embedding is not found
                similarity_score = 0
    
            # Append the document information to top_documents list
            top_documents.append({"document_ids": document_ids[j], "movie_name": movie_name, "subtitle": subtitle, "score": similarity_score})

    # Render the template with the search results
    return jsonify(top_documents)

if __name__ == '__main__':
    app.run(debug=True)

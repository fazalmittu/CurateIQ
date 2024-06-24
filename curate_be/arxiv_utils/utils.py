from pinecone import Pinecone, ServerlessSpec
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables from .env file
load_dotenv()

# Get the API keys from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# Initialize OpenAI client
openai_client = OpenAI(api_key=openai_api_key)

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)

index_name = "curate-iq"
index = pc.Index(index_name)

def get_ids_from_query(index,input_vector):
    print("searching pinecone...")
    results = index.query(
        top_k=10000,
        include_values=False,
        include_metadata=True,
        vector=input_vector,
    )
    ids = set()
    for result in results['matches']:
        ids.add(result.id)
    return ids

def get_all_ids_from_index(index, num_dimensions, namespace=""):
    num_vectors = index.describe_index_stats()
    num_vectors = num_vectors.namespaces[namespace].vector_count
    all_titles = set()
    while len(all_titles) < num_vectors:
        print("Length of ids list is shorter than the number of total vectors...")
        input_vector = np.random.rand(num_dimensions).tolist()
        print("creating random vector...")
        titles = get_ids_from_query(index, input_vector)
        print("getting titles from a vector query...")
        all_titles.update(titles)
        print("updating titles set...")
        print(f"Collected {len(all_titles)} ids out of {num_vectors}.")

    return all_titles

if __name__ == "__main__":
    index_name = "curate-iq"
    index = pc.Index(index_name)
    all_titles = get_all_ids_from_index(index, 1536)
    print(list(all_titles))

    # python3 -m curate_be.arxiv_utils.utils
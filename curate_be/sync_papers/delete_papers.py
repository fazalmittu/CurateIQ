from pinecone import Pinecone
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Get the index name from environment variable or set it directly
index_name = os.getenv("PINECONE_INDEX_NAME", "curate-iq")

# Initialize the index
index = pc.Index(index_name)

def delete_all_records_from_index(index):
    # Get index stats
    stats = index.describe_index_stats()
    namespaces = stats.namespaces

    for namespace, ns_stats in namespaces.items():
        print(f"Deleting records from namespace: {namespace}")
        num_vectors = ns_stats.vector_count
        
        while num_vectors > 0:
            # Generate a random vector to query
            query_vector = np.random.rand(1536).tolist()
            
            # Query to get IDs
            results = index.query(vector=query_vector, top_k=10000, include_values=False, namespace=namespace)
            
            # Extract IDs
            ids_to_delete = [match.id for match in results.matches]
            
            # Delete the vectors
            index.delete(ids=ids_to_delete, namespace=namespace)
            
            print(f"Deleted {len(ids_to_delete)} vectors from namespace {namespace}")
            
            # Update the number of vectors left
            num_vectors -= len(ids_to_delete)

    print("All records deleted from all namespaces.")

if __name__ == "__main__":
    delete_all_records_from_index(index)

    # python3 -m curate_be.sync_papers.delete_papers

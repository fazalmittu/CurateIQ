import pprint
from typing import Dict, List
import arxiv
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv
from openai import OpenAI

from curate_be.arxiv_utils.utils import get_all_ids_from_index

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

def fetch_latest_papers(category, max_results=300):
    """
    Fetch the latest papers from arXiv for a given category.

    Args:
    category (str): The arXiv category to fetch papers from.
    max_results (int): The maximum number of papers to fetch.

    Returns:
    list: A list of dictionaries containing paper information.
    """
    query = f"cat:{category}"
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for result in search.results():
        paper_info = {
            'id': result.entry_id.split('/')[-1],
            'title': result.title,
            'summary': result.summary,
            'authors': [author.name for author in result.authors],
            'published': result.published,
            'pdf_url': result.pdf_url
        }
        papers.append(paper_info)
    return papers

def get_embeddings(text):
    """
    Generate embeddings for the given text using OpenAI's embedding model.

    Args:
    text (str): The text to embed.

    Returns:
    list: The embedding vector.
    """
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def upsert_papers_to_pinecone(papers: List[Dict], namespace: str):
    """
    Upsert a list of papers into the Pinecone vector database.

    Args:
    papers (list): A list of dictionaries containing paper information.
    namespace (str): The namespace to insert the vectors into.
    """
    vectors = []
    for paper in papers:
        embedding = get_embeddings(paper['title'])
        vector = {
            "id": paper['id'],
            "values": embedding,
            "metadata": {
                "title": paper['title'],
                "authors": ", ".join(paper['authors']),
                "published": paper['published'].strftime('%Y-%m-%d'),
                "pdf_url": paper['pdf_url'],
                "summary": paper['summary']
            }
        }
        vectors.append(vector)

    if vectors:
        index.upsert(vectors=vectors, namespace=namespace)

def pull_and_upsert_latest_papers(category, max_results=300):
    """
    Pull the latest papers from arXiv and upsert them into Pinecone.

    Args:
    category (str): The arXiv category to fetch papers from.
    max_results (int): The maximum number of papers to fetch.
    """
    papers = fetch_latest_papers(category, max_results)
    
    ids = [paper['id'] for paper in papers]
    stored_ids = get_all_ids_from_index(index, 1536, namespace=category)
    
    new_papers = [id for id in ids if id not in stored_ids]
    papers_to_upsert = [paper for paper in papers if paper['id'] in new_papers]
    upsert_papers_to_pinecone(papers_to_upsert, namespace=category)
    print(f"Upserted {len(papers_to_upsert)} new papers from category {category} to Pinecone.")

if __name__ == "__main__":
    category = input("Enter the arXiv subject area (e.g., cs.AI for Artificial Intelligence): ")
    pull_and_upsert_latest_papers(category, max_results=5)

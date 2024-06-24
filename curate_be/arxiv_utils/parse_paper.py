from langchain_community.document_loaders import ArxivLoader
from unstructured.partition.text import partition_text
from typing import List
from langchain_core.documents import Document

# Function to get arXiv paper by ID
def get_arxiv_text_metadata(arxiv_id):
    # Initialize the arXiv loader
    docs: List[Document] = ArxivLoader(query=arxiv_id).load()
    # put together all the text
    full_text = ""
    for doc in docs:
        full_text += doc.page_content

    return full_text

# Function to semantically chunk the text using unstructured's text loader
def chunk_text(document):
    # Create a PlainTextDocument from the document content
    # text_document = PlainTextDocument(text=document['content'])
    # Use the partition_text method to chunk the document
    # chunks = semantic_chunker(text=document, metadata=metadata)
    chunks = partition_text(text=document, min_partition=50, chunking_strategy="by_title")
    return chunks

if __name__ == "__main__":
    # Main code
    arxiv_id = "2306.04050"  # Replace with your desired arXiv ID
    arxiv_text= get_arxiv_text_metadata(arxiv_id)
    chunked_document = chunk_text(arxiv_text)

    # Print the chunked document
    for chunk in chunked_document:
        print(chunk)
        print('--')

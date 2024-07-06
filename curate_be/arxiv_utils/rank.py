from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv
import os
import arxiv
import json
from rank_bm25 import BM25Okapi
from curate_be.arxiv_utils.pull_latest import get_embeddings
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RANK_SYSTEM_MSG = """

You are a research assistant and your job is to look through some of the latest arXiv papers and rank the most relevant ones for your boss. 
I am going to give you a list of arXiv paper abstracts of papers that your boss wrote. This should be what your ranking is based on.

I am also giving you a list of paper summaries from the latest arXiv feed in your boss' research area. Please return a ranked list of the papers in a list.
The ranking should be based on what papers your boss might find relevant to their research. 
Part of your reasoning process should include finding keywords in the author's papers and searching for them in the new papers you have pulled.

YOUR RESPONSE SHOULD BE JSON IN THE FOLLOWING FORMAT: 
{
    "ranking": ['paper_id_1', 'paper_id_2', ...]
}

THE IDS SHOULD BE RANKED FROM MOST RELEVANT TO LEAST RELEVANT. THERE SHOULD NOT BE ANY DUPLICATES. KEEP TRACK OF THE PAPER IDS PLEASE!

MAKE SURE YOUR RESPONSE IS JSON ONLY WITH NO OTHER TEXT. I WILL BE DIRECTLY PARSING YOUR RESPONSE AS JSON.
DO NOT WRAP YOUR JSON IN ```json``` or any other text please.
"""

KW_SYSTEM_MSG = """

You are a research assistant and your job is to look at a list of papers and generate a list of keywords for them.
These keywords will be used to look for papers that are similar to the ones you have.

Only generate 5 keywords and make sure they are specific and terms that can possibly be found in other papers you encounter later.
For example you wouldn't want to generate keywords like "model" or "method" or "approach". These are too general.
You also wouldn't want to generate keywords that are very specific like names of novel techniques a paper invented.
Rather, you want to generate keywords that are more like concepts or ideas that are discussed in the papers.

Each string should be max 2 words.

YOUR RESPONSE SHOULD BE JSON IN THE FOLLOWING FORMAT: 
{
    "keywords": ['keyword_1', 'keyword_2', 'keyword_3', 'keyword_4', 'keyword_5']
}

MAKE SURE YOUR RESPONSE IS JSON ONLY WITH NO OTHER TEXT. I WILL BE DIRECTLY PARSING YOUR RESPONSE AS JSON.
DO NOT WRAP YOUR JSON IN ```json``` or any other text please.
"""

def rank_papers(author_paper_ids, papers):
    
    # use arxiv api to get abstracts of selected paper ids
    arxiv_resp = arxiv.Search(id_list=author_paper_ids)
    # author_abstracts = [paper.summary for paper in arxiv_resp.results()]

    author_str = "HERE ARE THE PAPERS THAT YOU HAVE TO BASE YOUR RANKING ON:\n"

    # give title and abstract of each paper
    for paper in arxiv_resp.results():
        author_str += f"\n\nPaper ID: {paper.entry_id}\n{paper.title}\n{paper.summary}"

    author_str += "\n\n--------------------\n\n"
    author_str += "HERE ARE THE NEW PAPERS THAT YOU ACTUALLY HAVE TO RANK:\n"

    # do the same for pulled papers
    for paper in papers:
        author_str += f"\n\nPaper ID: {paper['id']}\n\n{paper['title']}\n\n{paper['summary']}"

    print(author_str)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": RANK_SYSTEM_MSG},
            {"role": "user", "content": author_str + "\nMAKE SURE YOUR RESPONSE IS JSON ONLY WITH NO OTHER TEXT. I WILL BE DIRECTLY PARSING YOUR RESPONSE AS JSON."}
        ],
        max_tokens=1000,
        response_format={"type": "json_object"}
    )

    print(response.choices[0].message.content)

    return json.loads(response.choices[0].message.content)["ranking"]

def bm25_search(papers, query):
    tokenized_corpus = [paper['summary'].split() for paper in papers]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.split()
    bm25_scores = bm25.get_scores(tokenized_query)
    return bm25_scores

def tfidf_search(papers, query, top_k=10):
    # Prepare the corpus and vectorizer
    corpus = [paper['summary'] for paper in papers]
    vectorizer = TfidfVectorizer().fit(corpus)
    
    # Transform the corpus and query to TF-IDF vectors
    tfidf_matrix = vectorizer.transform(corpus)
    query_vector = vectorizer.transform([query])
    
    # Calculate cosine similarity between query and documents
    cosine_similarities = np.dot(tfidf_matrix, query_vector.T).toarray().flatten()
    
    # Get top_k results
    top_indices = np.argsort(cosine_similarities)[-top_k:][::-1]
    tfidf_scores = cosine_similarities[top_indices]
    
    # Prepare the results
    results = [{'id': papers[i]['id'], 'score': tfidf_scores[j], 'metadata': papers[i]} for j, i in enumerate(top_indices)]
    return results

def keyword_matching_score(papers, keywords):
    keyword_scores = []
    keywords = [keyword.lower() for keyword in keywords]

    for paper in papers:
        summary = paper['summary'].lower()
        score = sum(summary.count(keyword) for keyword in keywords)
        keyword_scores.append(score)

    return keyword_scores


# def combined_search(index, query, papers, weight_bm25=0.6, weight_embedding=0.4, top_k=10):
#     query_embedding = get_embeddings(query)
#     bm25_scores = bm25_search(papers, query)
#     print("BM25 SCORES: ", bm25_scores)

#     pinecone_results = index.query(
#         vector=query_embedding,
#         top_k=top_k,
#         include_metadata=True
#     )

#     print("PINECONE RESULTS: ", pinecone_results)

#     paper_ids = [paper['id'] for paper in papers]
#     combined_results = []

#     for result in pinecone_results['matches']:
#         paper_id = result['id']
#         if paper_id in paper_ids:
#             matching_paper = papers[paper_ids.index(paper_id)]
#             bm25_score = bm25_scores[paper_ids.index(paper_id)]
#             embedding_score = result['score']
#             combined_score = weight_bm25 * bm25_score + weight_embedding * embedding_score
#             combined_results.append({
#                 'id': paper_id,
#                 'combined_score': combined_score,
#                 'metadata': result['metadata']
#             })
#         else:
#             print(f"No matching paper found for paper_id: {paper_id}")

#     combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
#     print("COMBINED RESULTS: ", combined_results)
#     return combined_results[:top_k]

def combined_search(index, query, papers, weight_bm25=0.3, weight_embedding=0.3, weight_tfidf=0.4, top_k=10):
    query_embedding = get_embeddings(query)
    bm25_scores = bm25_search(papers, query)
    tfidf_results = tfidf_search(papers, query, top_k)
    print("BM25 SCORES: ", bm25_scores)
    print("TF-IDF RESULTS: ", tfidf_results)

    pinecone_results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    print("PINECONE RESULTS: ", pinecone_results)

    paper_ids = [paper['id'] for paper in papers]
    combined_results = []

    for result in pinecone_results['matches']:
        paper_id = result['id']
        if paper_id in paper_ids:
            matching_paper = papers[paper_ids.index(paper_id)]
            bm25_score = bm25_scores[paper_ids.index(paper_id)]
            tfidf_score = next((item['score'] for item in tfidf_results if item['id'] == paper_id), 0)
            embedding_score = result['score']
            combined_score = (weight_bm25 * bm25_score + weight_embedding * embedding_score + weight_tfidf * tfidf_score)
            combined_results.append({
                'id': paper_id,
                'combined_score': combined_score,
                'metadata': result['metadata']
            })
        else:
            print(f"No matching paper found for paper_id: {paper_id}")

    combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
    print("COMBINED RESULTS: ", combined_results)
    return combined_results[:top_k]

def combined_search(index, query, papers, keywords=None, weight_bm25=0.2, weight_embedding=0.2, weight_tfidf=0.2, weight_keyword=0.2, top_k=20):
    query_embedding = get_embeddings(query)
    bm25_scores = bm25_search(papers, query)
    tfidf_results = tfidf_search(papers, query, top_k)
    if keywords:
        keyword_scores = keyword_matching_score(papers, keywords)
    print("BM25 SCORES: ", bm25_scores)
    print("TF-IDF RESULTS: ", tfidf_results)
    print("KEYWORD SCORES: ", keyword_scores)

    pinecone_results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    print("PINECONE RESULTS: ", pinecone_results)

    paper_ids = [paper['id'] for paper in papers]
    combined_results = []

    for result in pinecone_results['matches']:
        paper_id = result['id']
        if paper_id in paper_ids:
            matching_paper = papers[paper_ids.index(paper_id)]
            bm25_score = bm25_scores[paper_ids.index(paper_id)]
            if keywords:
                keyword_score = keyword_scores[paper_ids.index(paper_id)]
            tfidf_score = next((item['score'] for item in tfidf_results if item['id'] == paper_id), 0)
            embedding_score = result['score']
            if keywords:
                combined_score = (weight_bm25 * bm25_score + weight_embedding * embedding_score + 
                                  weight_tfidf * tfidf_score + weight_keyword * keyword_score)
            else:
                combined_score = (weight_bm25 * bm25_score + weight_embedding * embedding_score + 
                                  weight_tfidf * tfidf_score)
            combined_results.append({
                'id': paper_id,
                'combined_score': combined_score,
                'metadata': result['metadata']
            })
        else:
            print(f"No matching paper found for paper_id: {paper_id}")

    combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
    print("COMBINED RESULTS: ", combined_results)
    return combined_results[:top_k]

def generate_kw(papers):
    # given some papers, show them to GPT and get a list of keywords
    author_str = "PLEASE GENERATE 5 KEYWORDS. MAKE YOUR RESPONSE IN JSON PLEASE. HERE ARE THE PAPERS THAT YOU HAVE TO GENERATE KEYWORDS FOR:\n"

    # give title and abstract of each paper
    for paper in papers:
        author_str += f"\n\nPaper ID: {paper['id']}\n{paper['title']}\n{paper['summary']}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": KW_SYSTEM_MSG},
            {"role": "user", "content": author_str}
        ],
        max_tokens=1000,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)["keywords"]

if __name__ == "__main__":
    pass

    
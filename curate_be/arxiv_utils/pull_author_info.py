import arxiv
from curate_be.arxiv_utils.pull_latest import get_embeddings, index, fetch_latest_papers, pull_and_upsert_latest_papers
import pprint

def fetch_papers_by_author(author_name):
    """
    Fetch all papers written by a given author from arXiv.

    Args:
    author_name (str): The name of the author in the format "John Doe".

    Returns:
    list: A list of dictionaries containing paper information.
    """
    formatted_name = f"\"{author_name}\""
    
    query = f'au:{formatted_name}'
    search = arxiv.Search(
        query=query,
        max_results=1000,  # Adjust as needed
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

def fetch_and_find_similar_papers(author_name, category):
    """
    Fetch papers by the author and find similar papers using Pinecone.

    Args:
    author_name (str): The name of the author in the format "John Doe".
    category (str): The arXiv category to fetch latest papers from.

    Returns:
    list: A list of similar papers sorted by relevance.
    """
    pull_and_upsert_latest_papers(category, max_results=10)
    
    # Fetch papers by the author
    author_papers = fetch_papers_by_author(author_name)
    
    # Generate embeddings for the author's papers
    author_embeddings = [get_embeddings(paper['summary']) for paper in author_papers]
    recent_paper_embeddings = author_embeddings[:5]
    
    similar_papers = {}

    for i, embedding in enumerate(recent_paper_embeddings):
        matches = index.query(
            top_k=10,
            include_metadata=True,
            vector=embedding
        )
        metadatas = [match['metadata'] for match in matches['matches']]
        for metadata in metadatas:
            metadata['id'] = metadata['pdf_url'].split('/')[-1]

        similar_papers[i] = metadatas

    unique_paper_ids = set()
    for i, papers in similar_papers.items():
        for paper in papers:
            unique_paper_ids.add(paper['id'])
    
    # Debug print statements
    print("Unique paper IDs:", unique_paper_ids)
    print("Author papers:", [paper['id'] for paper in author_papers])
    
    scores = {id: 0 for id in unique_paper_ids}
    for id in unique_paper_ids:
        for i, papers in similar_papers.items():
            if id in [paper['id'] for paper in papers]:
                scores[id] += [paper['id'] for paper in papers].index(id)

    # Debug print statement to check scores
    print("Scores:", scores)
    print("Len scores:", len(scores))

    # we have a dict mapping id to score
    # now get the corresponding paper dicts for the ids from the matches, not author papers
    unique_papers = []
    print("Len metadatas:", len(metadatas))
    print("Len unique paper ids:", len(unique_paper_ids))
    for metadata in metadatas:
        for id in unique_paper_ids:
            if metadata['id'] == id:
                unique_papers.append({'id': id, 'paper': metadata})

    print("Len unique papers:", len(unique_papers))
        
    # Debug print statement
    print("Unique papers:", unique_papers)

    unique_papers = [paper['paper'] for paper in unique_papers]
    
    for i in range(len(unique_papers)):
        print(unique_papers[i]['title'], ":", scores[unique_papers[i]['id']])

    # sort unique papers by score and then return top 10
    sorted_papers = sorted(unique_papers, key=lambda x: scores[x['id']])
    return sorted_papers[:10]

if __name__ == "__main__":
    # papers = fetch_papers_by_author("Akshat Gupta")
    # pprint.pprint(papers)
    # print(len(papers))

    pprint.pprint(fetch_and_find_similar_papers("Akshat Gupta", "cs.CL"))

    # python3 -m curate_be.arxiv_utils.pull_author_info
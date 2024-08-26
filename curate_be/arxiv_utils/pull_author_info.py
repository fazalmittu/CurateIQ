import arxiv
from curate_be.arxiv_utils.pull_latest import get_embeddings, index, fetch_latest_papers, pull_and_upsert_latest_papers
import pprint

from curate_be.arxiv_utils.rank import combined_search, extract_keywords, generate_kw, rank_papers
from curate_be.sync_papers.add_and_delete import update_namespace

def fetch_papers_by_author(author_name):
    """
    Fetch all papers written by a given author from arXiv.

    Args:
    author_name (str): The name of the author in the format "John Doe".

    Returns:
    list: A list of dictionaries containing paper information.
    """
    print(f"Fetching papers for author: {author_name}")  
    formatted_name = f"\"{author_name}\""
    query = f'au:{formatted_name}'
    print(f"arXiv query: {query}") 
    search = arxiv.Search(
        query=query,
        max_results=300, 
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
    print(f"Found {len(papers)} papers for {author_name}") 
    return papers

def fetch_and_find_similar_papers(author_name, category, selected_paper_ids):
    """
    Fetch papers by the author and find similar papers using Pinecone.

    Args:
    author_name (str): The name of the author in the format "John Doe".
    category (str): The arXiv category to fetch latest papers from.
    selected_paper_ids (list): A list of paper IDs selected by the author.

    Returns:
    list: A list of similar papers sorted by relevance.
    """
    pull_and_upsert_latest_papers(category, max_results=300)
    
    # Fetch papers by the author
    author_papers = fetch_papers_by_author(author_name)
    
    # Filter papers based on selected IDs
    selected_papers = [paper for paper in author_papers if paper['id'] in selected_paper_ids]
    
    # Generate embeddings for the selected papers
    selected_embeddings = [get_embeddings(paper['summary']) for paper in selected_papers]
    
    similar_papers = {}
    for i, embedding in enumerate(selected_embeddings):
        matches = index.query(
            top_k=100,
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
    
    scores = {id: 0 for id in unique_paper_ids}
    for id in unique_paper_ids:
        for i, papers in similar_papers.items():
            if id in [paper['id'] for paper in papers]:
                scores[id] += [paper['id'] for paper in papers].index(id)

    unique_papers = []
    for metadata in metadatas:
        for id in unique_paper_ids:
            if metadata['id'] == id:
                unique_papers.append({'id': id, 'paper': metadata})

    unique_papers = [paper['paper'] for paper in unique_papers]
    
    sorted_papers = sorted(unique_papers, key=lambda x: scores[x['id']])
    return sorted_papers[:100]

def fetch_and_compare_selected_papers(selected_paper_ids, author_name, category):
    """
    Fetch selected papers from arXiv and compare them to find similar papers.

    Args:
    selected_paper_ids (list): A list of arXiv IDs for the selected papers.
    author_name (str): The name of the author in the format "John Doe".
    category (str): The arXiv category to fetch latest papers from.

    Returns:
    list: A list of similar papers sorted by relevance.
    """

    pull_and_upsert_latest_papers(category, max_results=300)

    if len(selected_paper_ids) == 0:
        author_papers = fetch_papers_by_author(author_name)
        selected_paper_ids = [paper['id'] for paper in author_papers][:5]
    
    selected_papers = []
    for paper_id in selected_paper_ids:
        search = arxiv.Search(id_list=[paper_id])
        for result in search.results():
            paper_info = {
                'id': result.entry_id.split('/')[-1],
                'title': result.title,
                'summary': result.summary,
                'authors': [author.name for author in result.authors],
                'published': result.published,
                'pdf_url': result.pdf_url
            }
            selected_papers.append(paper_info)

    selected_embeddings = [get_embeddings(paper['title']) for paper in selected_papers]

    similar_papers = {}
    for i, embedding in enumerate(selected_embeddings):
        matches = index.query(
            top_k=100,
            include_metadata=True,
            vector=embedding
        )
        metadatas = [match['metadata'] for match in matches['matches']]
        for metadata in metadatas:
            metadata['id'] = metadata['pdf_url'].split('/')[-1]

        similar_papers[i] = metadatas

    unique_paper_ids = set()
    for papers in similar_papers.values():
        for paper in papers:
            unique_paper_ids.add(paper['id'])

    scores = {id: 0 for id in unique_paper_ids}
    for id in unique_paper_ids:
        for i, papers in similar_papers.items():
            if id in [paper['id'] for paper in papers]:
                scores[id] += [paper['id'] for paper in papers].index(id)

    unique_papers = []
    for papers in similar_papers.values():
        for paper in papers:
            if paper['id'] in unique_paper_ids:
                unique_papers.append(paper)

    sorted_papers = sorted(unique_papers, key=lambda x: scores[x['id']])
    pprint.pprint(sorted_papers)

    # once we have the top papers, we want to pass their summaries all into GPT and then ask for a ranking back
    # we first pass in the titles of the author's selected ids
    # pass in a dictionary that maps id to summary (for arxiv papers)
    # make it very clear that we are expecting a dictionary back that maps id to ranking
    # we want it in order from most relevant to least relevant

    # separate by newlines
    # total_string = "You are a researcher and you are trying to find relevant papers to your research. Here are the titles of the papers you have selected to base your search on:\n"
    # total_string += "\n- ".join([paper['title'] for paper in selected_papers])
    
    # total_string += "\n\nHere are the summaries of the papers you want to rank in order from most relevant to least relevant:\n"
    # for paper in sorted_papers:
    #     total_string += f"\n{paper['title']}:\n{paper['summary']}"

    # best_paper_ids = list(set(rank_papers(selected_paper_ids, sorted_papers)))
    
    # final_paper_list = []

    # # Remove duplicates and sort the final papers list by the best_paper_ids
    # seen_paper_ids = set()
    # for id in best_paper_ids:
    #     for paper in sorted_papers:
    #         if paper['id'] == id and id not in seen_paper_ids:
    #             final_paper_list.append(paper)
    #             seen_paper_ids.add(id)

    # pprint.pprint(final_paper_list)

    # return final_paper_list
    return sorted_papers

# def hybrid_search_author_comparison(selected_paper_ids, author_name, category):
#     """
#     Perform a hybrid search to compare selected papers and find similar papers.
    
#     Args:
#     selected_paper_ids (list): A list of arXiv IDs for the selected papers.
#     author_name (str): The name of the author in the format "John Doe".
#     category (str): The arXiv category to fetch latest papers from.
    
#     Returns:
#     list: A list of similar papers sorted by relevance.
#     """
#     pull_and_upsert_latest_papers(category, max_results=300)

#     if len(selected_paper_ids) == 0:
#         author_papers = fetch_papers_by_author(author_name)
#         selected_paper_ids = [paper['id'] for paper in author_papers][:5]

#     selected_papers = []
#     for paper_id in selected_paper_ids:
#         search = arxiv.Search(id_list=[paper_id])
#         for result in search.results():
#             paper_info = {
#                 'id': result.entry_id.split('/')[-1],
#                 'title': result.title,
#                 'summary': result.summary,
#                 'authors': [author.name for author in result.authors],
#                 'published': result.published,
#                 'pdf_url': result.pdf_url
#             }
#             selected_papers.append(paper_info)

#     combined_results = []
#     all_papers = fetch_latest_papers(category, max_results=300)
#     for paper in selected_papers:
#         query = paper['title']
#         search_results = combined_search(index, query, all_papers, weight_bm25=0.5, weight_embedding=0.5, top_k=30)
#         combined_results.extend(search_results)
#         print(f"Results for query '{query}':", search_results)

#     pprint.pprint(combined_results)

#     # Count frequencies and accumulate scores
#     result_count = {}
#     result_scores = {}
#     for result in combined_results:
#         paper_id = result['id']
#         if paper_id not in result_count:
#             result_count[paper_id] = 0
#             result_scores[paper_id] = 0
#         result_count[paper_id] += 1
#         result_scores[paper_id] += result['combined_score']

#     # Rank papers based on frequency and score
#     ranked_papers = sorted(result_count.keys(), key=lambda id: (result_count[id], result_scores[id]), reverse=True)

#     unique_papers = [next(result['metadata'] for result in combined_results if result['id'] == paper_id) for paper_id in ranked_papers]

#     return unique_papers

# def hybrid_search_author_comparison(selected_paper_ids, author_name, category):
#     """
#     Perform a hybrid search to compare selected papers and find similar papers.
    
#     Args:
#     selected_paper_ids (list): A list of arXiv IDs for the selected papers.
#     author_name (str): The name of the author in the format "John Doe".
#     category (str): The arXiv category to fetch latest papers from.
    
#     Returns:
#     list: A list of similar papers sorted by relevance.
#     """
#     pull_and_upsert_latest_papers(category, max_results=300)

#     if len(selected_paper_ids) == 0 or selected_paper_ids[0] == "":
#         author_papers = fetch_papers_by_author(author_name)
#         selected_paper_ids = [paper['id'] for paper in author_papers][:5]

#     selected_papers = []
#     for paper_id in selected_paper_ids:
#         search = arxiv.Search(id_list=[paper_id])
#         for result in search.results():
#             paper_info = {
#                 'id': result.entry_id.split('/')[-1],
#                 'title': result.title,
#                 'summary': result.summary,
#                 'authors': [author.name for author in result.authors],
#                 'published': result.published,
#                 'pdf_url': result.pdf_url
#             }
#             selected_papers.append(paper_info)

#     combined_results = []
#     all_papers = fetch_latest_papers(category, max_results=300)
#     for paper in selected_papers:
#         query = paper['title']
#         search_results = combined_search(index, query, all_papers, weight_bm25=0.2, weight_embedding=0.2, weight_tfidf=0.6, top_k=50)
#         combined_results.extend(search_results)
#         print(f"Results for query '{query}':", search_results)

#     pprint.pprint(combined_results)

#     # Count frequencies and accumulate scores
#     result_count = {}
#     result_scores = {}
#     for result in combined_results:
#         paper_id = result['id']
#         if paper_id not in result_count:
#             result_count[paper_id] = 0
#             result_scores[paper_id] = 0
#         result_count[paper_id] += 1
#         result_scores[paper_id] += result['combined_score']

#     # Rank papers based on frequency and score
#     ranked_papers = sorted(result_count.keys(), key=lambda id: (result_count[id], result_scores[id]), reverse=True)

#     unique_papers = [next(result['metadata'] for result in combined_results if result['id'] == paper_id) for paper_id in ranked_papers]

#     return unique_papers

# def hybrid_search_author_comparison(selected_paper_ids, author_name, category):
#     """
#     Perform a hybrid search to compare selected papers and find similar papers.
    
#     Args:
#     selected_paper_ids (list): A list of arXiv IDs for the selected papers.
#     author_name (str): The name of the author in the format "John Doe".
#     category (str): The arXiv category to fetch latest papers from.
#     keywords (list): A list of keywords to use for keyword matching.
    
#     Returns:
#     list: A list of similar papers sorted by relevance.
#     """
#     pull_and_upsert_latest_papers(category, max_results=300)

#     keywords = ["model editing"]

#     if len(selected_paper_ids) == 0:
#         author_papers = fetch_papers_by_author(author_name)
#         selected_paper_ids = [paper['id'] for paper in author_papers][:5]

#     selected_papers = []
#     for paper_id in selected_paper_ids:
#         search = arxiv.Search(id_list=[paper_id])
#         for result in search.results():
#             paper_info = {
#                 'id': result.entry_id.split('/')[-1],
#                 'title': result.title,
#                 'summary': result.summary,
#                 'authors': [author.name for author in result.authors],
#                 'published': result.published,
#                 'pdf_url': result.pdf_url
#             }
#             selected_papers.append(paper_info)

#     combined_results = []
#     all_papers = fetch_latest_papers(category, max_results=300)
#     for paper in selected_papers:
#         query = paper['title']
#         search_results = combined_search(index, query, all_papers, weight_bm25=0.2, weight_embedding=0.2, weight_tfidf=0.2, top_k=10)
#         combined_results.extend(search_results)
#         print(f"Results for query '{query}':", search_results)

#     pprint.pprint(combined_results)

#     # Count frequencies and accumulate scores
#     result_count = {}
#     result_scores = {}
#     for result in combined_results:
#         paper_id = result['id']
#         if paper_id not in result_count:
#             result_count[paper_id] = 0
#             result_scores[paper_id] = 0
#         result_count[paper_id] += 1
#         result_scores[paper_id] += result['combined_score']

#     # Rank papers based on frequency and score
#     ranked_papers = sorted(result_count.keys(), key=lambda id: (result_count[id], result_scores[id]), reverse=True)

#     unique_papers = [next(result['metadata'] for result in combined_results if result['id'] == paper_id) for paper_id in ranked_papers]

#     return unique_papers

def hybrid_search_author_comparison(selected_paper_ids, author_name, category):
    """
    Perform a hybrid search to compare selected papers and find similar papers.
    
    Args:
    selected_paper_ids (list): A list of arXiv IDs for the selected papers.
    author_name (str): The name of the author in the format "John Doe".
    category (str): The arXiv category to fetch latest papers from.
    
    Returns:
    dict: A dictionary containing a list of similar papers sorted by relevance and the generated keywords.
    """
    # pull_and_upsert_latest_papers(category, max_results=300)

    if len(selected_paper_ids) == 0:
        author_papers = fetch_papers_by_author(author_name)
        selected_paper_ids = [paper['id'] for paper in author_papers][:5]

    selected_papers = []
    for paper_id in selected_paper_ids:
        search = arxiv.Search(id_list=[paper_id])
        for result in search.results():
            paper_info = {
                'id': result.entry_id.split('/')[-1],
                'title': result.title,
                'summary': result.summary,
                'authors': [author.name for author in result.authors],
                'published': result.published,
                'pdf_url': result.pdf_url
            }
            selected_papers.append(paper_info)

    try:
        # keywords = generate_kw(selected_papers)
        keywords = [keyword[0] for keyword in extract_keywords(selected_papers)]
        print("KEYWORDS: ", keywords)
    except Exception as e:
        print("ERROR GENERATING KEYWORDS: ", e)
        keywords = []

    combined_results = []
    update_namespace(index, category)
    all_papers = fetch_latest_papers(category, max_results=50)
    for paper in selected_papers:
        query = paper['title']
        if keywords:
            print("KW SEARCH")
            search_results = combined_search(index, category, query, all_papers, keywords, weight_bm25=0.4, weight_embedding=0, weight_tfidf=0.5, weight_keyword=0.05, top_k=50)
        else:
            search_results = combined_search(index, category, query, all_papers, weight_bm25=0., weight_embedding=0.2, weight_tfidf=0.2, top_k=50)
        combined_results.extend(search_results)
        print(f"Results for query '{query}':", search_results)

    # pprint.pprint(combined_results)

    # Count frequencies and accumulate scores
    result_count = {}
    result_scores = {}
    for result in combined_results:
        paper_id = result['id']
        if paper_id not in result_count:
            result_count[paper_id] = 0
            result_scores[paper_id] = 0
        result_count[paper_id] += 1
        result_scores[paper_id] += result['combined_score']

    # Rank papers based on frequency and score
    ranked_papers = sorted(result_count.keys(), key=lambda id: (result_count[id], result_scores[id]), reverse=True)

    unique_papers = [next(result for result in combined_results if result['id'] == paper_id) for paper_id in ranked_papers]

    return {
        'papers': unique_papers,
        'keywords': keywords
    }

if __name__ == "__main__":
    category = input("Enter the arXiv subject area (e.g., cs.AI for Artificial Intelligence): ")
    author_name = input("Enter the author's name: ")
    selected_paper_ids = input("Enter selected paper IDs (comma separated): ").split(',')
    combined_results = hybrid_search_author_comparison(selected_paper_ids, author_name, category)
    pprint.pprint(combined_results)



if __name__ == "__main__":
    # papers = fetch_papers_by_author("Akshat Gupta")
    # pprint.pprint(papers)
    # print(len(papers))

    pprint.pprint(fetch_and_find_similar_papers("Akshat Gupta", "cs.CL"))

    # python3 -m curate_be.arxiv_utils.pull_author_info
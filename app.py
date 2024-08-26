from flask import Flask, request, jsonify, send_from_directory
# from supabase import create_client
import os
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin
from curate_be.arxiv_utils.pull_latest import fetch_latest_papers
from curate_be.arxiv_utils.pull_author_info import fetch_and_compare_selected_papers, fetch_papers_by_author, hybrid_search_author_comparison

load_dotenv()

app = Flask(__name__, static_folder='curate_fe/build', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# url = os.environ.get("SUPABASE_URL")
# key = os.environ.get("SUPABASE_KEY")

# supabase = create_client(url, key)
# 
# @app.route('/')
# @cross_origin()
# def index():
#     return 'Welcome to the Research Feed API'

# @app.route('/')
# @cross_origin()
# def serve_react_app():
#     return send_from_directory(app.static_folder, 'index.html')
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@cross_origin()
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/researcher', methods=['POST', 'OPTIONS'])
def add_researcher():
    if request.method == 'OPTIONS':
        return build_cors_preflight_response()
    
    data = request.json
    # response = supabase.table('users').insert({
    #     'full_name': data['fullName'],
    #     'subject_areas': data['subjectArea'],
    #     # 'email': data['email']
    # }).execute()
    
    return jsonify(data), 200

@app.route('/api/arxiv', methods=['GET'])
def get_arxiv_papers():
    subject_area = request.args.get('subjectArea')
    papers = fetch_latest_papers(subject_area, max_results=300)
    return jsonify(papers), 200

@app.route('/api/author_papers', methods=['GET'])
def get_author_papers():
    author_name = request.args.get('authorName')
    print(f"Received request for author: {author_name}")  # Debug log
    papers = fetch_papers_by_author(author_name)
    print(f"Found {len(papers)} papers")  # Debug log
    return jsonify(papers), 200

# @app.route('/api/similar_papers', methods=['GET'])
# def get_similar_papers():
#     author_name = request.args.get('authorName')
#     category = request.args.get('category')
#     selected_paper_ids = request.args.get('selectedPaperIds', '').split(',')
#     # papers = fetch_and_compare_selected_papers(selected_paper_ids, author_name, category)
#     papers = hybrid_search_author_comparison(selected_paper_ids, author_name, category)
#     return jsonify(papers), 200
@app.route('/api/similar_papers', methods=['GET'])
def get_similar_papers():
    author_name = request.args.get('authorName')
    category = request.args.get('category')
    selected_paper_ids = request.args.get('selectedPaperIds').split(',')

    result = hybrid_search_author_comparison(selected_paper_ids, author_name, category)

    return jsonify(result), 200

def build_cors_preflight_response():
    response = jsonify()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

def corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    app.run(debug=True)


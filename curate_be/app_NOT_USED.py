from flask import Flask, request, jsonify
from supabase import create_client
import os
from dotenv import load_dotenv
from flask_cors import CORS
from arxiv_utils.pull_latest import fetch_latest_papers
from arxiv_utils.pull_author_info import fetch_and_find_similar_papers, fetch_papers_by_author

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

@app.route('/')
def index():
    return 'Welcome to the Research Feed API'

@app.route('/api/researcher', methods=['POST', 'OPTIONS'])
def add_researcher():
    if request.method == 'OPTIONS':
        return build_cors_preflight_response()
    
    data = request.json
    response = supabase.table('users').insert({
        'full_name': data['fullName'],
        'subject_areas': data['subjectArea'],
        'email': data['email']
    }).execute()
    
    return jsonify(response.data), 200

@app.route('/api/arxiv', methods=['GET'])
def get_arxiv_papers():
    subject_area = request.args.get('subjectArea')
    papers = fetch_latest_papers(subject_area, max_results=10)
    return jsonify(papers), 200

@app.route('/api/author_papers', methods=['GET'])
def get_author_papers():
    author_name = request.args.get('authorName')
    print(f"Received request for author: {author_name}")  # Debug log
    papers = fetch_papers_by_author(author_name)
    print(f"Found {len(papers)} papers")  # Debug log
    return jsonify(papers), 200

@app.route('/api/similar_papers', methods=['POST'])
def get_similar_papers():
    data = request.json
    author_name = data['authorName']
    category = data['category']
    selected_paper_ids = data['selectedPaperIds']
    papers = fetch_and_find_similar_papers(author_name, category, selected_paper_ids)
    return jsonify(papers), 200

def build_cors_preflight_response():
    response = jsonify()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS", "GET")
    return response

def corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    app.run(debug=True)

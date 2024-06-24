import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

data = supabase.table("users").insert(
    {
        "full_name":"fazal",
        "subject_areas": "AI",
        "google_scholar_link": "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=1234567890&citation_for_view=1234567890",
        "email": "fazal@gmail.com"
    }
).execute()

print(data)
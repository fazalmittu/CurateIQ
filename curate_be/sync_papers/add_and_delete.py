import os
from dotenv import load_dotenv
from pinecone import Pinecone
from curate_be.arxiv_utils.pull_latest import fetch_latest_papers, upsert_papers_to_pinecone
# from curate_be.sync_papers.add_papers import arxiv_categories

# arxiv_categories = [
#     "cs.AI", "cs.AR", "cs.CC", "cs.CE", "cs.CG", "cs.CL", "cs.CR", "cs.CV", "cs.CY", "cs.DB",
#     "cs.DC", "cs.DL", "cs.DM", "cs.DS", "cs.ET", "cs.FL", "cs.GL", "cs.GR", "cs.GT", "cs.HC",
#     "cs.IR", "cs.IT", "cs.LG", "cs.LO", "cs.MA", "cs.MM", "cs.MS", "cs.NA", "cs.NE", "cs.NI",
#     "cs.OH", "cs.OS", "cs.PF", "cs.PL", "cs.RO", "cs.SC", "cs.SD", "cs.SE", "cs.SI", "cs.SY",
#     "econ.EM", "econ.GN", "econ.TH", "eess.AS", "eess.IV", "eess.SP", "eess.SY", "math.AC",
#     "math.AG", "math.AP", "math.AT", "math.CA", "math.CO", "math.CT", "math.CV", "math.DG",
#     "math.DS", "math.FA", "math.GM", "math.GN", "math.GR", "math.GT", "math.HO", "math.IT",
#     "math.KT", "math.LO", "math.MG", "math.MP", "math.NA", "math.NT", "math.OA", "math.OC",
#     "math.PR", "math.QA", "math.RA", "math.RT", "math.SG", "math.SP", "math.ST", "astro-ph.CO",
#     "astro-ph.EP", "astro-ph.GA", "astro-ph.HE", "astro-ph.IM", "astro-ph.SR", "cond-mat.dis-nn",
#     "cond-mat.mes-hall", "cond-mat.mtrl-sci", "cond-mat.other", "cond-mat.quant-gas",
#     "cond-mat.soft", "cond-mat.stat-mech", "cond-mat.str-el", "cond-mat.supr-con", "gr-qc",
#     "hep-ex", "hep-lat", "hep-ph", "hep-th", "math-ph", "nlin.AO", "nlin.CD", "nlin.CG", "nlin.PS",
#     "nlin.SI", "nucl-ex", "nucl-th", "physics.acc-ph", "physics.ao-ph", "physics.app-ph",
#     "physics.atm-clus", "physics.atom-ph", "physics.bio-ph", "physics.chem-ph", "physics.class-ph",
#     "physics.comp-ph", "physics.data-an", "physics.ed-ph", "physics.flu-dyn", "physics.gen-ph",
#     "physics.geo-ph", "physics.hist-ph", "physics.ins-det", "physics.med-ph", "physics.optics",
#     "physics.plasm-ph", "physics.pop-ph", "physics.soc-ph", "physics.space-ph", "quant-ph",
#     "q-bio.BM", "q-bio.CB", "q-bio.GN", "q-bio.MN", "q-bio.NC", "q-bio.OT", "q-bio.PE", "q-bio.QM",
#     "q-bio.SC", "q-bio.TO", "q-fin.CP", "q-fin.EC", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.PR",
#     "q-fin.RM", "q-fin.ST", "q-fin.TR", "stat.AP", "stat.CO", "stat.ME", "stat.ML", "stat.OT",
#     "stat.TH"
# ]
arxiv_categories = ["cs.CL"]

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Get the index name from environment variable or set it directly
index_name = os.getenv("PINECONE_INDEX_NAME", "curate-iq")

# Initialize the index
index = pc.Index(index_name)

def delete_all_records_from_namespace(index, namespace):
    try:
        stats = index.describe_index_stats()
    
        results = index.query(vector=[0]*1536, top_k=600, include_values=False, namespace=namespace)
        ids_to_delete = [match.id for match in results.matches]
        
        index.delete(ids=ids_to_delete, namespace=namespace)
        print(f"Deleted {len(ids_to_delete)} vectors from namespace {namespace}")
    except Exception as e:
        print(f"Error deleting all records from namespace {namespace}: {e}")

def update_namespace(index, category):
    print(f"Updating namespace: {category}")
    
    # Delete all records in the current namespace
    delete_all_records_from_namespace(index, category)
    
    # Fetch latest papers for the category
    papers = fetch_latest_papers(category, max_results=300)
    
    # Upsert new papers to Pinecone
    upsert_papers_to_pinecone(papers, namespace=category)
    
    print(f"Updated namespace {category} with {len(papers)} new papers")

def update_all_namespaces(index):
    for category in arxiv_categories:
        update_namespace(index, category)

if __name__ == "__main__":
    update_all_namespaces(index)

    # python3 -m curate_be.sync_papers.add_and_delete

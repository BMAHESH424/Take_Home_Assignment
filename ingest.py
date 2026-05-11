import requests
import json
import faiss
import re
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def find_url(obj, base="https://www.shl.com"):
    """Recursively searches for any URL-like string in the JSON object."""
    keys = ['url', 'link', 'product_url', 'path', 'href']
    for key in keys:
        if key in obj and obj[key]:
            val = str(obj[key])
            if val.startswith('http'): return val
            return f"{base}{val if val.startswith('/') else '/' + val}"
    
    for k, v in obj.items():
        if isinstance(v, str) and ('/products/' in v or 'shl.com' in v):
            if v.startswith('http'): return v
            return f"{base}{v if v.startswith('/') else '/' + v}"
    return f"{base}/solutions/products/"

def build_vector_store():
    url = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"
    
    print("Fetching and fixing catalog URLs...")
    try:
        response = requests.get(url, timeout=30)
        cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', response.text)
        items = json.loads(cleaned_text, strict=False)
        
        catalog_results = []
        for i in items:
            name = i.get('name', '')
            if not name or "job solution" in name.lower():
                continue

            final_url = find_url(i)

            catalog_results.append({
                "name": name,
                "url": final_url,
                "test_type": i.get('test_type') or ("P" if "personality" in name.lower() else "K"),
                "description": i.get('description') or i.get('summary') or "SHL professional assessment."
            })
        
        texts = [f"Assessment: {i['name']}. {i['description']}" for i in catalog_results]
        embeddings = model.encode(texts).astype('float32')
        index = faiss.IndexFlatL2(384)
        index.add(embeddings)
        
        faiss.write_index(index, "catalog.index")
        with open("catalog_metadata.json", "w") as f:
            json.dump(catalog_results, f, indent=4)
            
        print(f"SUCCESS: {len(catalog_results)} assessments indexed.")
    except Exception as e:
        print(f"Ingestion failed: {e}")

if __name__ == "__main__":
    build_vector_store()
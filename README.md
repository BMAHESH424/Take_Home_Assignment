**SHL Assessment Recommender Agent**
This is a specialized Retrieval-Augmented Generation (RAG) conversational agent designed to help recruiters and hiring managers find the perfect SHL assessments. Instead of digging through a massive catalog, users can describe their hiring needs, and the agent provides grounded, clickable recommendations.

**How it Works**
- Ingestion: The system pulls live data from the SHL Product Catalog. It cleans the data (handling hidden control characters in the JSON) and filters it to include only Individual Test Solutions.

- Vector Search: Assessment descriptions are converted into 384-dimension vectors using the all-MiniLM-L6-v2 model for high-accuracy semantic matching.

- Conversational Intelligence: Powered by Groq (Llama 3), the agent is stateless. It analyzes the full history to clarify vague queries, refine results, and compare different assessments.

- Absolute Routing: Every recommendation link is formatted as an absolute URL to shl.com, ensuring users reach the actual product page.

**Tech Stack**
- LLM Engine: Groq (Llama-3.3-70b-versatile).

- Backend: FastAPI (Python).

- Vector Engine: FAISS (Facebook AI Similarity Search).

- Embeddings: Sentence-Transformers (all-MiniLM-L6-v2).

- Frontend: Vanilla JS, CSS3, HTML5.

**Installation & Setup**

1. Configure Environment
Create a .env file in the root directory and add your Groq API key:
GROQ_API_KEY=gsk_your_actual_key_here

2. Install Dependencies
Make sure you have Python 3.10+ installed.

pip install fastapi uvicorn requests faiss-cpu sentence-transformers numpy groq python-dotenv

3. Build the Knowledge Base (Crucial Step)
Run the ingestion script first to create the local database (catalog.index and catalog_metadata.json) by fetching and cleaning the live SHL data.

python ingest_2.py

4. Launch the Agent
Start the FastAPI server:

uvicorn app_2:app --reload
Navigate to http://127.0.0.1:8000 in your browser.

📋 Folder Structure
Plaintext
/SHL-Agent/
├── app_2.py            # The "Brain" - FastAPI, Groq Integration & RAG Logic
├── ingest_2.py         # The "Collector" - Data cleaning & Vectorization
├── .env                # API Key storage
├── catalog.index       # The FAISS vector database
├── catalog_metadata.json # Parsed metadata with absolute URLs
└── static/             # Frontend Assets
    ├── index.html
    ├── style.css
    └── script.js

**Key Features & Constraints**
Clarification First: The agent will strictly ask for seniority or role details if the initial query is too vague.

Scoped Answers: It refuses to provide legal advice, salary info, or general hiring tips—it only discusses SHL products.

Grounded Comparisons: If asked to compare tests (e.g., "OPQ vs GSA"), it uses catalog descriptions to explain the differences.

Direct Navigation: "View in Catalog" links open in a new tab (_blank) to the official SHL domain, bypassing local port redirection.

Note: The ingest_2.py script includes a robust recursive URL finder and a regex cleaner to handle messy formatting in the raw SHL source files.

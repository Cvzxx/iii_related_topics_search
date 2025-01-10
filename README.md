# Enhanced Article Explorer

A Streamlit-based application that allows you to analyze content from URLs or uploaded PDFs. The app uses an LLM to summarize content, extract key concepts, and generate search queries to find related articles online.

---

## Requirements

### Software
- **Python**: Version 3.10.10.
- **Rust**: Required for some dependencies.

### API Keys
- **Serper API Key**: Required for querying related articles.
- **Cohere API Key**: Required for LLM-based summarization and query generation.

---

## Installation Instructions
### 1. Generate API Keys
Create an account https://cohere.com/ and generate API Key, same for https://serper.dev/.

### 2. Clone the Repository
```bash
git clone https://github.com/Cvzxx/iii_related_topics_search.git
cd iii_related_topics_search
```

### 3. Set Up Python Environment
It’s recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate 
```

### 4. Install Rust
Install Rust to ensure all dependencies can be built:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 5. Install Python Dependencies
Install the libraries listed in requirements.txt:

```bash
pip install -r requirements.txt
````
### 6. Set API Keys
Set API keys as env variables or in app.py code:
```bash
SERPER_API_KEY=your_serper_api_key
COHERE_API_KEY=your_cohere_api_key
```

### 7. Run the Application
Start the Streamlit application:

```bash
streamlit run app.py
```


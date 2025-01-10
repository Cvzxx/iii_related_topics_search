import streamlit as st
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import logging
import validators
from langchain.prompts import PromptTemplate
from langchain.llms import Cohere
from langchain.chains import LLMChain

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# API Keys
SERPER_API_KEY = "your_serper_api_key"  # Replace with your Serper API Key
COHERE_API_KEY = "your_cohere_api_key"  # Replace with your Cohere API Key

# Initialize Cohere LLM with LangChain
llm = Cohere(cohere_api_key=COHERE_API_KEY, model="command-xlarge-nightly", temperature=0)

# Define LangChain prompts
language_detection_prompt = PromptTemplate(
    input_variables=["content"],
    template="Determine the language of the following text. Respond only with the language name (e.g., English, Polish, etc.):\n{content}"
)

summary_prompt = PromptTemplate(
    input_variables=["content", "language"],
    template="Summarize the following article content in {language}:\n{content}"
)

concept_prompt = PromptTemplate(
    input_variables=["content", "language"],
    template="Extract the main concepts and ideas from the following article content in {language}:\n{content}"
)

# LangChain Chains
language_chain = LLMChain(llm=llm, prompt=language_detection_prompt)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
concept_chain = LLMChain(llm=llm, prompt=concept_prompt)

def extract_content_and_title(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No Title Found"
        paragraphs = soup.find_all("p")
        content = " ".join([p.get_text() for p in paragraphs])
        return title, content
    except Exception as e:
        logger.exception("Error fetching content from URL")
        raise ValueError("Failed to fetch or parse the provided URL.")

def validate_url(url):
    if not validators.url(url):
        raise ValueError("The URL is not valid.")
    return True

def process_pdf_with_llm(pdf_file, language="English"):
    reader = PdfReader(pdf_file)
    summaries = []

    for page in reader.pages:
        raw_text = page.extract_text()
        if raw_text.strip():  
            prompt = f"""
            You are an assistant that summarizes sections of text from PDFs.
            
            Language: {language}
            Text: {raw_text[:1000]}...  
            
            Summarize this section in {language} and highlight the most important points:
            """
            try:
                response = llm.generate(prompts=[prompt], temperature=0.5, max_tokens=200)
                section_summary = response.generations[0][0].text.strip()
                summaries.append(section_summary)
            except Exception as e:
                logger.exception("Error processing PDF section with LLM")
                summaries.append("Error summarizing this section.")

    return " ".join(summaries)

def detect_language(content):
    return language_chain.run(content=content).strip()

def summarize_content(content, language="English"):
    return summary_chain.run(content=content, language=language)

def extract_concepts(content, language="English"):
    return concept_chain.run(content=content, language=language)

def generate_query_with_llm(title, keywords, content, language="English"):
    prompt = f"""
    You are an assistant that generates concise search queries to find articles related to a given text.
    
    Title: {title}
    Keywords: {keywords}
    Content: {content[:500]}...  
    
    Based on this information, generate a concise query to search for related topics. 
    Ensure the query is clear and avoids conversational or chat-based prompts.
    """
    try:
        response = llm.generate(prompts=[prompt], temperature=0.5, max_tokens=50)
        return response.generations[0][0].text.strip()
    except Exception as e:
        logger.exception("Error generating query with LLM")
        raise

def search_with_serper(query, language="English"):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY}
    payload = {"q": query, "num": 5, "hl": "pl" if language == "Polish" else "en"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    results = response.json().get("organic", [])
    return [
        {"title": result["title"], "url": result["link"], "snippet": result.get("snippet", "")}
        for result in results
    ]

def analyze_content(content, title=None):
    detected_language = detect_language(content)
    summary = summarize_content(content, detected_language)
    concepts = extract_concepts(content, detected_language)
    query = generate_query_with_llm(title or "Document", concepts, content, detected_language)
    related_articles = search_with_serper(query, detected_language)
    return detected_language, summary, concepts, query, related_articles

def display_results(title, detected_language, summary, keywords, query, related_articles, user_url=None):
    st.subheader("Original Title:")
    st.write(title)
    if user_url:
        st.markdown(f"[Original Link]({user_url})")

    st.subheader("Detected Language:")
    st.write(detected_language)

    st.subheader(f"Summary ({detected_language}):")
    st.write(summary)

    st.subheader(f"Key Concepts ({detected_language}):")
    st.write(keywords)

    st.subheader("Generated Search Query:")
    st.write(query)

    st.subheader(f"Related Articles ({detected_language}):")
    for result in related_articles:
        st.write(f"**{result['title']}**")
        st.write(result["snippet"])
        st.markdown(f"[Read More]({result['url']})")

def main():
    st.title("Enhanced Article Explorer")
    st.write("Paste a URL or upload a PDF file, and we'll analyze its content and find related articles.")

    if "url" not in st.session_state:
        st.session_state["url"] = ""
    if "uploaded_pdf" not in st.session_state:
        st.session_state["uploaded_pdf"] = None

    user_url = st.text_input("Enter a URL", value=st.session_state["url"], placeholder="E.g., https://example.com/article")
    uploaded_pdf = st.file_uploader("Or upload a PDF file", type=["pdf"])

    if st.button("Analyze and Find Related Articles"):
        with st.spinner("Processing..."):
            try:
                if user_url:
                    validate_url(user_url)
                    title, content = extract_content_and_title(user_url)
                    st.session_state["url"] = ""
                    st.session_state["uploaded_pdf"] = None
                elif uploaded_pdf:
                    content = process_pdf_with_llm(uploaded_pdf)
                    title = "Uploaded PDF"
                    st.session_state["url"] = ""
                    st.session_state["uploaded_pdf"] = None
                else:
                    st.error("Please provide a URL or upload a PDF file.")
                    return

                detected_language, summary, keywords, query, related_articles = analyze_content(content, title)
                display_results(title, detected_language, summary, keywords, query, related_articles, user_url=user_url)
            except Exception as e:
                logger.exception("An error occurred while processing the request.")
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

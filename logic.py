import os
import json
import requests
import io
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
# HackRx-60-Bajaj-Finserv - LLM Document Processing System
# Advanced RAG system for universal document analysis and query processing
# --- Load Environment Variables ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# --- Initialize LLM ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0)

# --- Core Logic Functions ---

def get_documents_from_pdf_url(pdf_url):
    """
    Downloads a PDF, extracts text page by page, and creates Document objects
    that store the text and the original page number in their metadata.
    """
    try:
        print(f"Downloading PDF from: {pdf_url}")
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)
        documents = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                documents.append(Document(page_content=page_text, metadata={"source_page": i + 1}))
        print(f"PDF processed successfully. Found {len(documents)} pages with text.")
        return documents
    except Exception as e:
        print(f"Error processing PDF from URL: {e}")
        return None

def get_text_chunks(documents):
    """Splits Document objects into smaller chunks for processing."""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1200,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_documents(documents)

def get_vector_store(text_chunks):
    """Creates a FAISS vector store from document chunks using a local model."""
    if not text_chunks:
        print("Error: No text chunks to process.")
        return None
    try:
        print("Creating vector store with local embeddings... (This may take a moment on first run)")
        # Using a local model is much faster after the initial download
        embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        vector_store = FAISS.from_documents(documents=text_chunks, embedding=embedding)
        print("Vector store created successfully.")
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None

def llm_parser_extract_query_topic(user_question):
    """Uses the LLM to parse natural language queries and extract structured data."""
    prompt = f"""
    You are an expert document analyst. Analyze the following query and extract structured information.
    
    Query: "{user_question}"
    
    Extract and return a JSON object with the following structure:
    {{
        "query_topic": "main topic for semantic search",
        "structured_data": {{
            "entities": "key entities mentioned (people, places, things)",
            "parameters": "specific parameters or values",
            "relationships": "relationships between entities",
            "document_type": "type of document this query relates to",
            "action_items": "what the user is looking for"
        }}
    }}
    
    Respond ONLY with the JSON object.
    """
    try:
        response = llm.invoke(prompt)
        json_string = response.content.strip().replace("```json", "").replace("```", "")
        parsed_json = json.loads(json_string)
        if isinstance(parsed_json, list) and parsed_json:
            return parsed_json[0].get("query_topic", user_question)
        return parsed_json.get("query_topic", user_question)
    except Exception:
        return user_question

def generate_simple_answer(context, question):
    """
    Generates intelligent responses based on document analysis.
    This prompt is designed for universal document processing with structured output.
    """
    prompt = f"""
    You are an expert document analyst for Bajaj Finserv.
    Your task is to analyze queries based **STRICTLY AND ONLY** on the provided document context.

    **Provided Document Context:**
    ---
    {context}
    ---

    **User Query:**
    ---
    {question}
    ---

    **Your Task:**
    Analyze the query against the document and provide a structured response with:
    1. **Decision**: Relevant information found/Not found/Partially found
    2. **Details**: Specific information extracted from the document
    3. **Justification**: Clear explanation with specific document references
    4. **Document Mapping**: Reference the exact sections/clauses used

    **Response Format:**
    Provide a clear, professional response that includes:
    - Whether the requested information is available in the document
    - Specific document sections that apply
    - Any relevant conditions, terms, or requirements
    - Key details and amounts if mentioned
    - Clear reasoning for the response

    If the context **DOES NOT** contain relevant information, respond with: "Information not found in the provided document."
    """
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"An error occurred during LLM call: {e}")
        return "Failed to process the document query request."

def process_document_and_questions(pdf_url, questions):
    """
    Main document processing pipeline. Returns structured document analysis results.
    """
    documents = get_documents_from_pdf_url(pdf_url)
    if not documents:
        return {"error": "Failed to retrieve or read the document."}

    text_chunks = get_text_chunks(documents)
    vector_store = get_vector_store(text_chunks)
    if not vector_store:
        return {"error": "Failed to create the vector store for document analysis."}

    final_document_analysis = []
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    print("\n--- DOCUMENT PROCESSING LOG ---")
    for i, question in enumerate(questions):
        print(f"\nProcessing query {i+1}/{len(questions)}: '{question}'")
        query_topic = llm_parser_extract_query_topic(question)
        retrieved_docs = retriever.get_relevant_documents(query_topic)
        
        context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

        if retrieved_docs:
            document_analysis = generate_simple_answer(context, question)
            print(f"  -> Document Analysis: {document_analysis}")
            final_document_analysis.append(document_analysis)
        else:
            error_analysis = "Could not find any relevant information for this query in the document."
            print(f"  -> {error_analysis}")
            final_document_analysis.append(error_analysis)

    # This is the final object that will be sent to the judge
    final_response = {"answers": final_document_analysis}
    print("\n--- FINAL DOCUMENT ANALYSIS RESPONSE (as sent to judge) ---")
    print(json.dumps(final_response, indent=2))
    return final_response

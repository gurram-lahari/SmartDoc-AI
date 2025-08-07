import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

# Import the core processing logic from your other file
from logic import process_document_and_questions

# --- FastAPI App Initialization ---
app = FastAPI(
    title="🧠 SmartDoc AI - Intelligent Document Assistant",
    description="""
    **🚀 Advanced AI-Powered Document Analysis Platform**
    
    Transform any PDF document into an intelligent knowledge base! Our cutting-edge RAG (Retrieval-Augmented Generation) 
    system combines state-of-the-art vector embeddings with Google's Gemini 2.5 Flash AI to provide accurate, 
    context-aware answers to your questions.
    
    ## ✨ Key Features:
    - 📄 **Smart PDF Processing**: Automatic text extraction and intelligent chunking
    - 🔍 **Vector Search**: Lightning-fast semantic search using FAISS
    - 🤖 **AI-Powered Answers**: Context-aware responses powered by Gemini AI
    - 📊 **Batch Processing**: Handle multiple questions simultaneously
    - 🔒 **Secure & Reliable**: Enterprise-grade document processing
    
    ## 🎯 Perfect for:
    - Legal document analysis
    - Research paper summarization  
    - Policy document Q&A
    - Educational content exploration
    - Business document insights
    
    ## 🚀 Quick Start:
    1. **Upload your PDF**: Provide a URL to your PDF document
    2. **Ask questions**: Submit your questions about the document
    3. **Get AI answers**: Receive intelligent, context-aware responses
    
    ## 💡 Example Usage:
    ```json
    {
      "documents": "https://example.com/document.pdf",
      "questions": ["What is the main topic?", "Who are the stakeholders?"]
    }
    ```
    """,
    version="4.2.0",
    terms_of_service="https://smartdoc-ai.com/terms",
    contact={
        "name": "SmartDoc AI Support",
        "url": "https://smartdoc-ai.com/contact",
        "email": "support@smartdoc-ai.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_url="/api/openapi.json"
)

# --- CORS (Cross-Origin Resource Sharing) Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request Body Validation ---
class QueryRequest(BaseModel):
    documents: str = Field(..., description="URL of the PDF document to analyze", example="https://example.com/document.pdf")
    questions: List[str] = Field(..., description="List of questions to ask about the document", example=["What is the main topic?", "Who are the key stakeholders?"])
    
class AnalysisResponse(BaseModel):
    answers: List[str] = Field(description="AI-generated answers to your questions")


# --- API Endpoints ---

@app.post("/hackrx/run", 
         summary="🔍 Analyze Document & Answer Questions",
         description="""
         **Transform your PDF into an intelligent Q&A system!**
         
         Upload a PDF document URL and get AI-powered answers to your questions. Our advanced RAG system:
         - 📄 Extracts and processes PDF content intelligently
         - 🧠 Creates semantic embeddings for better understanding  
         - 🤖 Uses Gemini AI for contextually accurate answers
         - ⚡ Processes multiple questions simultaneously
         
         **Example Use Cases:**
         - Legal document analysis
         - Research paper insights
         - Policy document Q&A
         - Educational content exploration
         """,
         response_description="Array of AI-generated answers to your questions",
         tags=["🎯 Core AI Analysis"])
async def analyze_document(request_data: QueryRequest) -> List[str]:
    """
    **🚀 Main Analysis Endpoint**
    
    Transform any PDF document into an intelligent knowledge base and get instant answers!
    """
    print("🔍 Received document analysis request")
    import time
    start_time = time.time()
    
    try:
        # The main logic is now cleanly separated in another file.
        results = process_document_and_questions(
            pdf_url=request_data.documents, 
            questions=request_data.questions
        )
        
        if "error" in results:
            # If the logic file returns an error, pass it to the client
            raise HTTPException(status_code=400, detail=results["error"])
        
        # Return only the answers array in a clean format
        print(f"✅ Successfully processed request in {time.time() - start_time:.2f}s")
        return results.get("answers", [])

    except Exception as e:
        # Catch any other unexpected errors
        print(f"❌ An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

class QuickSummaryRequest(BaseModel):
    documents: str = Field(..., description="URL of the PDF document to summarize", example="https://example.com/document.pdf")

@app.post("/api/quick-summary",
         summary="📋 Quick Document Summary", 
         description="Get a rapid AI-generated summary of your PDF document",
         tags=["🎯 Core AI Analysis"])
async def quick_summary(request_data: QuickSummaryRequest):
    """Generate a quick summary of the document content"""
    try:
        results = process_document_and_questions(
            pdf_url=request_data.documents,
            questions=["Provide a comprehensive summary of this document including key points, main topics, and important details."]
        )
        if "error" in results:
            raise HTTPException(status_code=400, detail=results["error"])
        return {
            "success": True,
            "summary": results.get("answers", ["Unable to generate summary"])[0],
            "document_url": request_data.documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Health Check & Info Endpoints ---
@app.get("/", 
        summary="🏠 API Health Check",
        description="Check if the SmartDoc AI service is running and get quick info",
        tags=["📊 System Status"])
def read_root():
    """
    **🏠 Welcome to SmartDoc AI!**
    
    Your intelligent document analysis companion is ready to transform PDFs into smart knowledge bases.
    """
    return {
        "service": "SmartDoc AI - Intelligent Document Assistant",
        "status": "🟢 ONLINE",
        "version": "4.2.0",
        "ai_model": "Google Gemini 2.5 Flash",
        "features": ["PDF Analysis", "AI Q&A", "Vector Search", "Batch Processing"],
        "main_endpoint": "/hackrx/run",
        "docs": "/docs",
        "message": "🚀 Ready to analyze your documents!"
    }

@app.get("/api/health",
        summary="🔍 Detailed Health Check", 
        description="Get detailed system health and capability information",
        tags=["📊 System Status"])
def health_check():
    """Get detailed health information about the AI service"""
    import os
    return {
        "status": "healthy",
        "service": "SmartDoc AI",
        "capabilities": {
            "pdf_processing": True,
            "ai_analysis": True,
            "vector_search": True,
            "batch_questions": True,
            "real_time_processing": True
        },
        "ai_models": {
            "language_model": "Google Gemini 2.5 Flash",
            "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
            "vector_store": "FAISS"
        },
        "environment": {
            "python_version": "3.12+",
            "api_key_configured": bool(os.getenv("GEMINI_API_KEY"))
        }
    }

@app.get("/api/supported-formats",
        summary="📄 Supported Document Formats",
        description="List of supported document formats and processing capabilities", 
        tags=["📊 System Status"])
def supported_formats():
    """Get information about supported document formats"""
    return {
        "supported_formats": ["PDF"],
        "processing_capabilities": {
            "text_extraction": "✅ Advanced text extraction with page-by-page processing",
            "large_documents": "✅ Handles documents up to 100+ pages",
            "multilingual": "✅ Supports multiple languages",
            "complex_layouts": "✅ Handles tables, columns, and complex layouts"
        },
        "limitations": {
            "image_only_pdfs": "❌ Scanned PDFs without text layer not fully supported",
            "password_protected": "❌ Password-protected PDFs not supported",
            "max_size": "📏 Recommended max size: 50MB"
        }
    }

# --- Custom Documentation Endpoints ---
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Interactive API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "operationsSorter": "method",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "tryItOutEnabled": True,
        },
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc documentation"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartDoc AI - API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body { margin: 0; padding: 0; }
            .redoc-container { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        </style>
    </head>
    <body>
        <div id="redoc-container"></div>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js"></script>
        <script>
            Redoc.init('/api/openapi.json', {
                theme: {
                    colors: {
                        primary: {
                            main: '#667eea'
                        }
                    },
                    typography: {
                        fontSize: '14px',
                        lineHeight: '1.5em',
                        code: {
                            fontSize: '13px',
                            fontFamily: 'Courier, monospace'
                        },
                        headings: {
                            fontFamily: 'Montserrat, sans-serif',
                            fontWeight: '400'
                        }
                    },
                    sidebar: {
                        backgroundColor: '#fafafa'
                    }
                },
                scrollYOffset: 60,
                hideDownloadButton: false,
                disableSearch: false,
                nativeScrollbars: false
            }, document.getElementById('redoc-container'));
        </script>
    </body>
    </html>
    """)

def custom_openapi():
    """Generate custom OpenAPI schema with enhanced metadata"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="🧠 SmartDoc AI - Intelligent Document Assistant",
        version="4.2.0",
        description=app.description,
        routes=app.routes,
        servers=[
            {"url": "http://localhost:8000", "description": "Local development server"},
            {"url": "https://smartdoc-ai.vercel.app", "description": "Production server"}
        ]
    )
    
    # Customize the OpenAPI schema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        "altText": "SmartDoc AI Logo"
    }
    
    # Add custom styling to Swagger UI
    openapi_schema["info"]["x-api-id"] = "smartdoc-ai"
    
    # Add tag descriptions
    openapi_schema["tags"] = [
        {
            "name": "🎯 Core AI Analysis",
            "description": "**Main AI-powered document analysis endpoints.** These endpoints provide the core functionality for transforming PDFs into intelligent knowledge bases."
        },
        {
            "name": "📊 System Status", 
            "description": "**Health checks and system information.** Monitor service status, capabilities, and supported formats."
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# To run this server, use the command: uvicorn main:app --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
import os
import tempfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RAG PDF Question Answering System", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables to store the QA chain and document info
qa_chain = None
current_document_info = None

# Initialize embeddings model (this will be loaded once)
try:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    logger.info("Embeddings model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load embeddings model: {e}")
    embeddings = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: Frontend files not found</h1>", status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "embeddings_loaded": embeddings is not None,
        "document_processed": qa_chain is not None
    }

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file for question answering
    """
    global qa_chain, current_document_info
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if embeddings is None:
        raise HTTPException(status_code=500, detail="Embeddings model not loaded. Please restart the server.")
    
    try:
        # Create temporary file to store uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            pdf_path = temp_file.name
        
        logger.info(f"Processing PDF: {file.filename} (size: {len(content)} bytes)")
        
        # Load and process the PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        if not documents:
            raise HTTPException(status_code=400, detail="No content found in the PDF file")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        docs = text_splitter.split_documents(documents)
        
        logger.info(f"Document split into {len(docs)} chunks")
        
        # Create FAISS vector store
        faiss_index = FAISS.from_documents(docs, embeddings)
        
        # Initialize Groq LLM
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set")
        
        llm = ChatGroq(
            api_key=groq_api_key,
            model_name="llama3-8b-8192",
            temperature=0.1,
            max_tokens=1000
        )
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=faiss_index.as_retriever(k=4),
            return_source_documents=True
        )
        
        # Store document information
        current_document_info = {
            "filename": file.filename,
            "num_pages": len(documents),
            "num_chunks": len(docs),
            "total_characters": sum(len(doc.page_content) for doc in docs)
        }
        
        # Clean up temporary file
        os.unlink(pdf_path)
        
        logger.info(f"PDF processed successfully: {current_document_info}")
        
        return {
            "message": f"PDF '{file.filename}' uploaded and processed successfully",
            "document_info": current_document_info
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'pdf_path' in locals():
            try:
                os.unlink(pdf_path)
            except:
                pass
        
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    """
    Ask a question about the uploaded PDF document
    """
    if not qa_chain:
        raise HTTPException(
            status_code=400, 
            detail="No PDF document has been uploaded and processed. Please upload a PDF first."
        )
    
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        logger.info(f"Processing question: {question[:100]}...")
        
        # Get answer from QA chain
        result = qa_chain({"query": question})
        answer = result["result"]
        source_docs = result.get("source_documents", [])
        
        # Extract source information
        sources = []
        for i, doc in enumerate(source_docs):
            sources.append({
                "chunk_id": i + 1,
                "page": doc.metadata.get("page", "Unknown"),
                "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        response = {
            "question": question,
            "answer": answer,
            "document_info": current_document_info,
            "sources": sources,
            "num_sources": len(sources)
        }
        
        logger.info(f"Question answered successfully (sources: {len(sources)})")
        return response
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/status/")
async def get_status():
    """
    Get current system status
    """
    return {
        "system_ready": qa_chain is not None,
        "embeddings_loaded": embeddings is not None,
        "current_document": current_document_info,
        "groq_api_configured": bool(os.getenv("GROQ_API_KEY"))
    }

@app.delete("/reset/")
async def reset_system():
    """
    Reset the system (clear current document and QA chain)
    """
    global qa_chain, current_document_info
    
    qa_chain = None
    current_document_info = None
    
    logger.info("System reset successfully")
    return {"message": "System reset successfully. You can now upload a new PDF."}

if __name__ == "__main__":
    import uvicorn
    
    # Check for required environment variables
    if not os.getenv("GROQ_API_KEY"):
        logger.warning("GROQ_API_KEY environment variable not set. PDF processing will fail.")
    
    # Start the server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )

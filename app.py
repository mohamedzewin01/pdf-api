from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
import os

app = FastAPI()
qa_chain = None

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_path = f"/tmp/{file.filename}"
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = splitter.split_documents(documents)

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        faiss_index = FAISS.from_documents(docs, embeddings)

        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-8b-8192"
        )

        global qa_chain
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=faiss_index.as_retriever(k=4))

        return {"message": "PDF uploaded and processed successfully."}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    if not qa_chain:
        return JSONResponse(status_code=400, content={"error": "Upload and process a PDF first."})
    try:
        answer = qa_chain.run(question)
        return {"question": question, "answer": answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

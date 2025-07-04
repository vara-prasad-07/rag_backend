import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import pickle
import google.generativeai as genai

model = SentenceTransformer("all-MiniLM-L6-v2")
client=genai.Client(api_key="AIzaSyDeaiOo290CBQ2KpYJRHpfxjE59dT8lXoY")
class chatbot:
    def __init__(self, pdf_path, faiss_path="faiss_index"):
        self.pdf_path = pdf_path
        self.faiss_path = faiss_path
        self.vectorstore = None

    def read_pdf(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text

    def chuck_content(self):
        text = self.read_pdf()
        text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)
        chunks = text_splitter.split_text(text)
        return chunks

    def get_embedding(self):
        chunks = self.chuck_content()
        embeddings = model.encode(chunks)
        return chunks, embeddings

    def store_embeddings(self):
        # Only store if FAISS index does not exist
        if not os.path.exists(self.faiss_path):
            chunks, embeddings = self.get_embedding()
            # Use langchain's FAISS wrapper
            embedding_func = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.vectorstore = FAISS.from_texts(chunks, embedding_func)
            self.vectorstore.save_local(self.faiss_path)
        else:
            print("FAISS index already stored on disk.")

    def load_vectorstore(self):
        if self.vectorstore is None:
            embedding_func = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.vectorstore = FAISS.load_local(
                self.faiss_path,
                embedding_func,
                allow_dangerous_deserialization=True  # <-- add this argument
            )

    def query(self, query_text):
        self.load_vectorstore()
        results = self.vectorstore.similarity_search(query_text,k=3)
        # Combine the retrieved chunks
        context = "\n".join([doc.page_content for doc in results])
        # Compose a prompt for the LLM
        prompt = (
            f"Given the following context from a resume:\n{context}\n\n"
            f"Answer the following question:\n{query_text}\n"
        )
        # Call the LLM (OpenAI example)
        response = client.models.generate_content(
                  model="gemini-2.5-flash", contents=f"You are an assistant that answers questions based on resume content give me only a single sentence no any other external characters and try to make response spicy by adding some extra friendly words here you need to answer list first person which includes I,my,i am etc.{prompt}")

        return response.text

if __name__ == "__main__":
    obj = chatbot("resume_modified.pdf")
    obj.store_embeddings()
    

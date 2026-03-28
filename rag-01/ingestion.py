from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

# ENVIRONMENT SETUP
load_dotenv()

# CONFIGURATION

PDF_FILE = "doc.pdf"
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL = "text-embedding-3-large"
COLLECTION_NAME = "networknuts_c1"

# STEP 1: LOAD THE PDF DOCUMENT

loader = PyPDFLoader(PDF_FILE)
documents = loader.load()

# STEP 2: BREAK THE PDF INTO CHUNKS

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

chunked_documents = text_splitter.split_documents(documents) 
# do not use split_text for pdf data

# INITIALIZE CHOSEN EMBEDDING MODEL 

embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

# STORE THE CHUNKS IN THE VECTOR DATABASE

qdrant = QdrantVectorStore.from_documents(
    documents=chunked_documents,
    embedding=embeddings,
    url=QDRANT_URL,
    collection_name=COLLECTION_NAME
)

print("Ingestion completed")
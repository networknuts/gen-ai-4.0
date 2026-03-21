from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI 

# ENVIRONMENT SETUP
load_dotenv()
client = OpenAI()
COLLECTION_NAME="networknuts_c1"

#EMBEDDING MODEL - MUST MATCH INGESTION MODEL
EMBEDDING_MODEL = "text-embedding-3-large"
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

# CONNECTING TO VECTOR DB WITH RELEVANT COLLECTION

qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    url="http://localhost:6333",
)

# ASK THE USER FOR AN INPUT

query = input("Human: ")

# SEARCH THE VECTOR DATABASE FOR RELEVANT SIMILARITY DATA

search_results = qdrant.similarity_search(query)

# BUILDING CONTEXT FROM THE VECTOR DATABASE

context_list = []
for result in search_results:
    block = f"""
    Page Content:
    {result.page_content}
    Page Number:
    {result.metadata.get("page_label","N/A")}
    """
    context_list.append(block)

SYSTEM_PROMPT = f"""
You are a RAG AI Assistant.
You have been given content extracted from a PDF document.
Each section includes:
- The text content
- The page number

Answer the user's question using ONLY this provided information.
If the answer is available:
- Respond clearly and in a concise manner
- Mention the relevant page number from where the data was extracted

If the answer is not found:
- Clearly state that the required information is not available.

In any circumstance, do not add outside knowledge.

Context:
{context_list}
"""

# GENERATE FINAL ANSWER 

response = client.responses.create(
    model="gpt-5.4-nano",
    instructions=SYSTEM_PROMPT,
    input=query
)

print(response.output_text)
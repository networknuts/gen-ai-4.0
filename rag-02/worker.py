import redis
import ast 
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI 

# SETUP VECTOR DB ENV

load_dotenv()
client = OpenAI()
COLLECTION_NAME="networknuts_c1"

EMBEDDING_MODEL = "text-embedding-3-large"
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    url="http://localhost:6333",
)

# SETUP THE REDIS CONNECTION

redis_client = redis.Redis(host='localhost',
    port=6379,
    decode_responses=True)

while True:
    queue_name, raw_payload = redis_client.blpop("rag:requests")

    payload = ast.literal_eval(raw_payload)
    job_id = payload["job_id"]
    query = payload["query"]
    print(f"PROCESSING JOB: {job_id}")

    search_results = qdrant.similarity_search(query)
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
    response = client.responses.create(
    model="gpt-5.4-nano",
    instructions=SYSTEM_PROMPT,
    input=query
    )
    answer = response.output_text
    
    redis_client.set(
        f"rag:response:{job_id}",
        answer,
        ex=86400
    )
    print(f"Job {job_id} SUCCESSFULLY COMPLETED")
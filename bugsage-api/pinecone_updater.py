import os
import requests
from pinecone import Pinecone
from pinecone import ServerlessSpec
from time import sleep
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# Initialize Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

client = Pinecone(api_key=pinecone_api_key)
index = client.Index(pinecone_index_name)

# Initialize HuggingFace embeddings
hf_embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# === Embedding Function ===
def get_embedding(text):
    try:
        return hf_embed.embed_query(text)
    except Exception as e:
        print(f"[EMBED ERROR] {e}")
        return None

# === StackOverflow API Search ===
def search_stackoverflow(query, tag="java", max_results=100):
    url = "https://api.stackexchange.com/2.3/search/advanced"
    all_items = []
    page = 1
    while len(all_items) < max_results:
        remaining = max_results - len(all_items)
        page_size = min(100, remaining)  # Max allowed by API
        params = {
            "order": "desc",
            "sort": "relevance",
            "tagged": tag,
            "q": query,
            "site": "stackoverflow",
            "filter": "withbody",
            "pagesize": page_size,
            "page": page
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            items = data.get("items", [])
            all_items.extend(items)
            if not data.get("has_more", False):
                break  # No more pages
            page += 1
        except Exception as e:
            print(f"[SO ERROR] {e}")
            break
    return all_items



# === Get all existing IDs in index ===
def get_existing_ids(index, ids):
    try:
        response = index.fetch(ids=ids)
        return set(response.vectors.keys())
    except Exception as e:
        print(f"[FETCH ERROR] {e}")
        return set()

# === Upsert Each Item into Pinecone ===
def upsert_to_pinecone(items, keyword, tag):
    id_list = [f"so-{tag}-{item['question_id']}" for item in items]
    existing_ids = get_existing_ids(index, id_list)

    for item in items:
        q_id = item["question_id"]
        vector_id = f"so-{tag}-{q_id}"
        if vector_id in existing_ids:
            print(f"[SKIPPED] Already exists: {vector_id}")
            continue

        title = item["title"]
        link = item["link"]
        body = item["body"]
        full_text = f"Keyword: {keyword}\nTag: {tag}\nTitle: {title}\nLink: {link}\n\n{body[:800]}"

        emb = get_embedding(full_text)
        if emb:
            try:
                index.upsert([
                    (vector_id, emb, {"text": full_text})
                ])
                print(f"[UPLOADED] {title[:60]}... ✅")
            except Exception as up_e:
                print(f"[PINECONE UPSERT ERROR] {up_e}")
        sleep(1.5)  # To avoid StackOverflow rate limits

# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    keywords = [
    # General Debugging & Logging
    "java",

    #   "how to read flutter logs", "analyze java logs"

    # "logcat crash flutter", "spring boot debug mode", "application log error",
    # "troubleshooting backend issues", "how to trace API errors",

    # Java Specific
    # "java null pointer exception", "java out of memory error", "java memory leak",
    # "java class not found", "java.lang.IllegalArgumentException", 
    # "java file not found exception", "java heap space error",
    # "java.lang.ArrayIndexOutOfBoundsException", "java method not found error",

#     # Spring Boot / Backend
#     "spring boot failed to start", "spring boot bean creation error",
#     "spring boot circular dependency", "spring boot no such bean definition",
#     "spring boot server not starting", "spring boot application context error",
#     "spring boot REST API error", "spring boot actuator debugging",

#     # Flutter / Mobile
#     "flutter app crash", "flutter null check operator error", "flutter widget build failed",
#     "flutter renderflex overflow", "flutter late initialization error",
#     "flutter api call error", "flutter error red screen", "flutter build failed",
#     "flutter network error", "flutter json decode error", "flutter null safety bug",

#     # API & Network
#     "http request failed", "api response 500", "api response 404",
#     "api gateway timeout", "rest API error", "postman error response",
#     "connection refused backend", "timeout error http client",
#     "axios request failed", "java okhttp error", "spring webclient error",

#     # Build / Gradle / Dependency Issues
#     "gradle build failed", "gradle sync failed", "flutter pub get error",
#     "maven dependency error", "dependency resolution failed", 
#     "module not found error java", "android build failed", "java classpath error",

#     # Test Failures
#     "unit test failed java", "junit test error", "flutter test case failed",
#     "mocking dependency failed", "test class not found", "assertion failed",

#     # Miscellaneous
#     "stackoverflowerror java", "recursion depth exceeded java", "thread deadlock java",
#     "flutter emulator error", "java sql connection failed", "spring boot db error",
#     "hibernate session error", "java socket timeout", "flutter firebase error"
]

    for keyword in keywords:
        print(f"\n🔄 Fetching and updating Pinecone for keyword: {keyword}")
        results = search_stackoverflow(keyword, tag=keyword)
        if results:
            upsert_to_pinecone(results, keyword, tag=keyword)
        else:
            print(f"No results found for {keyword}")

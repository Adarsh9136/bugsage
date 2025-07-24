#phase 2 llm_chain

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

# Initialize Hugging Face embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # 384-dimension

# Initialize Pinecone
client = Pinecone(api_key=pinecone_api_key)
index = client.Index(pinecone_index_name)

# === Get Embedding using Hugging Face ===
def get_embedding(text):
    try:
        return embedding_model.encode(text).tolist()
    except Exception as e:
        print(f"[EMBED ERROR] {e}")
        return None

# === Build Prompt for GPT ===
def build_prompt(log, lang="en", context=None, from_search=False):
    if lang == "fr":
        system_msg = "Vous êtes un expert en débogage logiciel..."
    elif lang == "hi":
        system_msg = "आप एक विशेषज्ञ सॉफ़्टवेयर डिबगिंग विशेषज्ञ हैं..."
    else:
        system_msg = "You are an expert software debugger."

    messages = [{"role": "system", "content": system_msg}]

    if context and from_search:
        messages.append({"role": "user", "content": f"Here is what I found from a prior search:\n{context}"})
        messages.append({"role": "user", "content": f"Now explain this error based on the context:\n{log}"})
    elif context:
        messages.append({"role": "user", "content": f"Context from similar previous error:\n{context}"})
        messages.append({"role": "user", "content": f"Now explain this:\n{log}"})
    else:
        messages.append({"role": "user", "content": log})

    return messages

# === Main Function ===
def explain_bug2(log: str, lang: str = "en") -> str:
    print(f"[DEBUG] Log received for language: {lang}")

    try:
        query_embedding = get_embedding(log)
        if not query_embedding:
            raise RuntimeError("Embedding generation failed")

        # Step 1: Try Pinecone vector search
        print("[INFO] Searching Pinecone vector DB...")
        res = index.query(vector=query_embedding, top_k=3, include_metadata=True)

        context = None
        from_search = False

        if res['matches'] and res['matches'][0]['score'] > 0.82:
            context = "\n\n".join([match['metadata']['text'] for match in res['matches']])
            print("[RAG] Pinecone context found and will be used.")
        else:
            print("[RAG] No Pinecone match. Asking GPT to 'search'...")

            # Simulated search fallback using GPT
            search_prompt = [
                {"role": "system", "content": "You are a developer assistant who helps debug errors by finding similar public knowledge or documentation."},
                {"role": "user", "content": f"Please find relevant background info or solutions for this error:\n{log}"}
            ]
            search_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=search_prompt,
                temperature=0.4
            )
            context = search_response.choices[0].message.content.strip()
            from_search = True
            print("[GPT] GPT provided search-based context.")

        # Final GPT explanation step
        messages = build_prompt(log=log, lang=lang, context=context, from_search=from_search)
        final_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2
        )

        explanation = final_response.choices[0].message.content.strip()

        # Optional: Save into Pinecone
        try:
            index.upsert([
                (f"log-{hash(log)}", query_embedding, {"text": explanation})
            ])
            print("[PINECONE] Stored log and explanation.")
        except Exception as up_e:
            print(f"[UPSERT ERROR] {up_e}")

        return explanation

    except Exception as e:
        print(f"[LLM ERROR] {e}")
        raise RuntimeError("LLM processing failed.")

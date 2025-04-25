import google.generativeai as genai
import chromadb
from chromadb.config import Settings

#  Gemini API
genai.configure(api_key="API_KEY")  

# Ensure Chroma 
chroma_client = chromadb.Client(Settings(persist_directory="./chroma_db"))
collection = chroma_client.get_or_create_collection(name="web_content")

# Function to summarize a single document using Gemini
def summarize_with_gemini(query, full_text):
    model = genai.GenerativeModel("models/gemini-1.5-flash")

    prompt = (
            f"You are an elite research assistant with unparalleled expertise in synthesizing complex web content into sophisticated, yet clear, analyses.\n\n"
            f"User's original inquiry: \"{query}\"\n\n"
            f"Here is a comprehensive overview of the content:\n\n"
            f"{full_text[:3000]}\n\n" 
            f"Your objective is to craft a response that addresses the user's question with the utmost precision, rigor, and clarity. Please adhere to the following instructions:\n\n"
            f"1. **Directly engage with the user's question** by drawing insights from the provided summary while offering a detailed, multi-layered answer.\n"
            f"2. **Structure your response logically**, maintaining a fluid narrative that flows seamlessly from introduction to conclusion. Ensure that each segment builds upon the last.\n"
            f"3. **Incorporate advanced analysis and insights**. The response should provide not only the answers but also the deeper implications, subtleties, or nuances that are important for a comprehensive understanding of the topic.\n"
            f"4. **Use authoritative, precise language**. The tone should be confident and professional, avoiding redundancy while ensuring clarity. Aim to elevate the discourse by introducing thoughtful nuances where applicable.\n"
            f"6. **Prioritize conciseness** while avoiding oversimplification. The response should be succinct but sufficiently detailed, with a focus on delivering high-impact insights without unnecessary verbosity.\n"
            f"7. **Conclude with actionable insights** or recommendations, where relevant, based on the summary's findings and the context of the query."
        )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini Error:", e)
        return "Summary generation failed."

# Function to summarize all documents from ChromaDB
def summarize_all_from_chromadb(query):
    try:
        
        results = collection.get(include=["documents", "metadatas"])

        summaries = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            summary = summarize_with_gemini(query, doc)
            summaries.append({
                "title": meta.get("title", "Untitled"),
                "link": meta.get("link", ""),
                "summary": summary
            })
        return summaries
    except Exception as e:
        print("ChromaDB Fetch Error:", e)
        return []

import os
import chromadb
from dotenv import load_dotenv
from app.service.config import get_openai_client

class RAGPipeline:
    def __init__(self):
        load_dotenv()
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="rag_documents")
        self.DEFAULT_OPENAI_MODEL = "notispace-v1"
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", self.DEFAULT_OPENAI_MODEL)
        self.embeddings_model = os.getenv("EMBEDDING_MODEL_NAME", "notispace/ns-embed")
        self.notispace_client = get_openai_client()

    def retrieve_context(self, query: str, top_k: int) -> list:
        try:
            response = self.notispace_client.embeddings.create(
                model=self.embeddings_model,
                input=[query],
            )

            query_vector = response.data[0].embedding
            results = self.collection.query(
                query_embeddings=[query_vector], 
                n_results=top_k,
                where={'is_active': True}
            )
            
            formatted_results = []
            
            if not results or not results.get('documents') or len(results['documents'][0]) == 0:
                return formatted_results
        
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "distance": results['distances'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
            return formatted_results
        except Exception as e:
            print(f"Error di retrieve_context: {e}")
            raise

    def generate_answer(self, query: str, context: str) -> str:
        try:
            if not self.is_safe_input(query):
                return "query mengandung prompt injection"
            system_prompt = """Anda adalah sistem yang berfungsi untuk membantu menjawab pertanyaan karyawan mengenai SOP yang berlaku.
                            Tugas Anda menjawab pertanyaan HANYA berdasarkan KONTEKS yang disediakan.
                            Aturan yang bersifat mutlak:
                            1. JAWAB HANYA dari teks yang ada di dalam KONTEKS.
                            2. Jika jawabannya tidak ada di dalam konteks, Anda WAJIB menjawab: "Maaf, informasi tidak ditemukan dalam dokumen resmi."
                            3. Jangan berasumsi sendiri, jangan menyimpulkan di luar konteks yang diberikan, dan jangan gunakan pengetahuan luar Anda.
                            4. Jika konteks memuat informasi yang berbeda atau bertolak belakang, jelaskan perbedaannya.
                            """

            client = get_openai_client()
            response = client.chat.completions.create(
                    model=self.OPENAI_MODEL,
                    messages=[
                        {'role': 'developer', 'content': system_prompt},
                        {'role': 'user', 'content': f"KONTEKS:\n{context}\n\nPERTANYAAN:\n{query}"}
                    ],
                    temperature=0.0
                )
            
            llm_output = response.choices[0].message.content
            return llm_output or ""
        except Exception as e:
            print(f"terjadi Error di generate_answer: {e}")
            raise
    
    def is_safe_input(self, user_query: str) -> bool:
        blacklist = ["abaikan perintah", "ignore previous", "lupakan aturan", "batalkan perintah",
                     "kamu sekarang adalah", "jailbreak","ignore","forget", "forget the rule", "abaikan aturan"]
        
        query_lower = user_query.lower()
        for word in blacklist:
            if word in query_lower:
                return False
        return True

rag_pipeline = RAGPipeline()
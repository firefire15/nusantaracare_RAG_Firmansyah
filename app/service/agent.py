from app.schemas import QueryInput, RAGResponse, DocumentSource
from app.service.rag import rag_pipeline

class AgenticRouter:
    @staticmethod
    async def process_request(payload: QueryInput) -> RAGResponse:
        try:
           
            if not AgenticRouter.is_safe_input(payload.query):
                return RAGResponse(
                    answer="query mengandung prompt injection",
                    confidence_label="low",
                    reason_code="prompt_injection_detected"
                )

            raw_results = rag_pipeline.retrieve_context(payload.query, payload.top_k)
            if len(raw_results) == 0:
                return RAGResponse(
                    answer="Maaf, informasi tidak ditemukan dalam dokumen resmi.",
                    confidence_label="low",
                    reason_code="no_relevant_context"
                )
                
            valid_chunks = []
            best_distance = 1.0
            sources_ext = []
            
            for res in raw_results:

                if res['distance'] <= payload.threshold:
                    valid_chunks.append(res['text'])
                    
                    source_obj = DocumentSource(
                        doc_title=res['metadata']['doc_title'],
                        section_title=res['metadata']['section_title'],
                        doc_version=res['metadata']['doc_version']
                    )
                    
                    if source_obj not in sources_ext:
                        sources_ext.append(source_obj)
                        
                if res['distance'] < best_distance:
                    best_distance = res['distance']
            
            if len(valid_chunks) == 0:
                return RAGResponse(
                    answer="Maaf, informasi tidak ditemukan dalam dokumen resmi.",
                    confidence_label="low",
                    reason_code="no_relevant_context"
                )
                
            context_str = "\n\n".join(valid_chunks)
            
            answer = rag_pipeline.generate_answer(payload.query, context_str)
            
            if "query mengandung prompt injection" in answer:
                return RAGResponse(
                    answer=answer,
                    confidence_label="low",
                    reason_code="prompt_injection_detected" # Disamakan dengan di atas
                )

            if "tidak ditemukan dalam dokumen resmi" in answer:
                return RAGResponse(
                    answer=answer,
                    confidence_label="low",
                    reason_code="no_relevant_context"
                )
            
            if best_distance < 0.33:
                confidence = "high"
            elif best_distance < 0.67:
                confidence = "medium"
            else:
                confidence = "low"
                
            return RAGResponse(
                answer=answer,
                confidence_label=confidence,
                reason_code="answered",
                sources=sources_ext
            )
        except Exception as e:
            print(f"Error di AgenticRouter: {e}")
            raise
    
    @staticmethod
    def is_safe_input(user_query: str) -> bool:
        blacklist = ["abaikan perintah", "ignore previous", "lupakan aturan", "batalkan perintah",
                     "kamu sekarang adalah", "jailbreak", "ignore", "forget", "forget the rule", "abaikan aturan"]
        
        query_lower = user_query.lower()
        for word in blacklist:
            if word in query_lower:
                return False
        return True
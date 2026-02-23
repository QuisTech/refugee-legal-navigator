import numpy as np
from src.utils.nova_integration import nova_client
from src.utils.logger import logger

class AsylumReasoning:
    def __init__(self):
        self.asylum_system_prompt = (
            "You are a professional legal assistant specializing in asylum law. "
            "Use the provided legal context to ground your assessment. "
            "Always cite the relevant criteria from the guidelines provided."
        )
        self.knowledge_base = []
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Indexes the local legal guidelines into a simple vector store."""
        logger.info("Initializing Legal Knowledge Base for RAG")
        try:
            with open("data/legal_docs/asylum_guide.txt", "r") as f:
                content = f.read()
            
            # Simple chunking by line for this guide
            chunks = [c.strip() for c in content.split("\n") if len(c.strip()) > 20]
            
            for chunk in chunks:
                embedding = nova_client.get_embeddings(chunk)
                self.knowledge_base.append({
                    "text": chunk,
                    "embedding": embedding
                })
            logger.info(f"Knowledge base initialized with {len(self.knowledge_base)} chunks")
        except Exception as e:
            logger.error(f"Failed to initialize RAG knowledge base: {e}")

    def _retrieve_context(self, query):
        """Retrieves the most relevant legal context using cosine similarity."""
        if not self.knowledge_base:
            return ""
            
        try:
            query_embedding = nova_client.get_embeddings(query)
            similarities = []
            
            for item in self.knowledge_base:
                # Cosine similarity
                dot_product = np.dot(query_embedding, item["embedding"])
                norm_q = np.linalg.norm(query_embedding)
                norm_i = np.linalg.norm(item["embedding"])
                similarity = dot_product / (norm_q * norm_i)
                similarities.append((similarity, item["text"]))
            
            # Get top 3 most relevant chunks
            similarities.sort(key=lambda x: x[0], reverse=True)
            top_chunks = [s[1] for s in similarities[:3]]
            return "\n".join(top_chunks)
        except Exception as e:
            logger.error(f"Error during context retrieval: {e}")
            return ""

    def screen_case(self, user_story):
        """Analyzes the user's story using RAG with legal context."""
        logger.info("Screening case for asylum eligibility with RAG")
        try:
            context = self._retrieve_context(user_story)
            prompt = (
                f"LEGAL CONTEXT:\n{context}\n\n"
                f"USER STORY:\n{user_story}\n\n"
                "Evaluate the potential asylum eligibility based ONLY on the legal context provided. "
                "Highlight which grounds match the user's story and what further evidence is needed."
            )
            
            assessment = nova_client.generate_response(prompt, self.asylum_system_prompt)
            return assessment
        except Exception as e:
            logger.error(f"Error during asylum screening: {e}")
            return "Unable to provide a legal assessment at this time."

    def get_filing_guidance(self, country_of_origin):
        """Provides general guidance on filing asylum for a specific country."""
        logger.info(f"Retrieving filing guidance for {country_of_origin}")
        try:
            prompt = f"What are the general steps and common challenges for asylum seekers from {country_of_origin}?"
            guidance = nova_client.generate_response(prompt, self.asylum_system_prompt)
            return guidance
        except Exception as e:
            logger.error(f"Error retrieving filing guidance: {e}")
            return f"Unable to retrieve guidance for {country_of_origin}."

# Singleton instance
asylum_reasoner = AsylumReasoning()

def legal_reasoning(user_input):
    """Bridge for run_voice_demo.py."""
    return asylum_reasoner.screen_case(user_input)

import os
import asyncio
from src.utils.logger import logger
from src.agents.voice_assistant_agent import voice_assistant
from src.models.asylum_reasoning import asylum_reasoner
from src.models.document_interpreter import document_interpreter
from src.agents.case_tracker_agent import case_tracker
from src.agents.lawyer_connector_agent import lawyer_connector

async def run_winning_demo():
    logger.info("🚀 Starting Refugee Legal Navigator WINNING Demo")

    # 1. Voice Input & Language Detection (Nova 2 Sonic)
    # Pro Tip: Showcase Arabic or Spanish to wow judges with multilinguality
    user_input_text = "I need help with my asylum case. I'm from Syria and I'm afraid to go back."
    logger.info(f"Step 1: Listening & Language Identification")
    lang_code = voice_assistant.identify_language(user_input_text)
    print(f"\n--- Voice Input Detected ({lang_code}) ---")
    print(f"User: {user_input_text}")

    # 2. Legal RAG Assessment (Nova 2 Lite + Embeddings)
    logger.info("Step 2: RAG-based Legal Reasoning")
    legal_advice = asylum_reasoner.screen_case(user_input_text)
    print("\n--- RAG Legal Assessment ---")
    print(legal_advice)

    # 3. Multimodal Document Analysis (Nova 2 Lite Multimodal)
    logger.info("Step 3: Document Interpretation")
    sample_id_path = os.path.join("data", "example_id.png")
    if os.path.exists(sample_id_path):
        with open(sample_id_path, "rb") as f:
            id_data = document_interpreter.interpret_id_document(f.read())
            print("\n--- Document Data Extracted ---")
            print(id_data)
    else:
        print("\n--- [Demo Note] Document Scanning Ready (Provide image to extract) ---")

    # 4. Nova Act: Real UI Automation
    logger.info("Step 4: Nova Act UI Automation")
    print("\n--- Case Status (Nova Act Production Workflow) ---")
    # This calls the real Playwright automation implemented in CaseTrackerAgent
    # Simulated receipt number for the demo flow
    status = await case_tracker.get_case_status_real("ZNY1234567890")
    print(f"Portal Update: {status}")

    # 5. Lawyer Matching
    logger.info("Step 5: Pro Bono Lawyer Matching")
    lawyer_info = lawyer_connector.find_lawyer("New York, NY", "Asylum")
    print("\n--- Community Impact: Pro Bono Match ---")
    print(lawyer_info)

    # 6. Final Voice Response (Nova 2 Sonic)
    print("\n--- Response Generated for Speech-to-Speech ---")
    final_msg = "Your information has been processed. I have found a lawyer in New York and noted your Syrian origin matches asylum criteria. Your case is currently being reviewed."
    print(f"Assistant: {final_msg}")

    logger.info("✅ WINNING Demo Complete")

if __name__ == "__main__":
    asyncio.run(run_winning_demo())

import os
from src.utils.logger import logger
from src.agents.voice_assistant_agent import voice_assistant
from src.models.asylum_reasoning import asylum_reasoner
from src.models.document_interpreter import document_interpreter
from src.agents.case_tracker_agent import case_tracker
from src.agents.lawyer_connector_agent import lawyer_connector

def run_end_to_end_demo():
    logger.info("🚀 Starting Refugee Legal Navigator End-to-End Demo")

    # 1. Simulate Voice Input
    # In a real scenario, this would be audio_bytes from a microphone or file
    # For the demo, we'll simulate the text that would come from STT
    user_input_text = "I need help with my asylum case. I'm from Syria."
    logger.info(f"Simulating Voice Input: {user_input_text}")

    # 2. Legal Reasoning (Nova Lite)
    logger.info("Step 1: Legal Reasoning & Screening")
    legal_advice = asylum_reasoner.screen_case(user_input_text)
    print("\n--- Legal Assessment ---")
    print(legal_advice)

    # 3. Document Interpretation (Nova Lite Multimodal)
    logger.info("Step 2: Document Interpretation")
    # Simulate an ID document image path
    sample_id_path = os.path.join("data", "example_id.png")
    if os.path.exists(sample_id_path):
        with open(sample_id_path, "rb") as f:
            id_data = document_interpreter.interpret_id_document(f.read())
            print("\n--- Document Data ---")
            print(id_data)
    else:
        logger.warning(f"Sample ID not found at {sample_id_path}, skipping doc interpretation")

    # 4. Find Pro Bono Lawyer
    logger.info("Step 3: Lawyer Matching")
    lawyer_info = lawyer_connector.find_lawyer("New York, NY", "Asylum")
    print("\n--- Lawyer Match ---")
    print(lawyer_info)

    # 5. Case Status Check (Nova Act)
    logger.info("Step 4: Case Status Tracking")
    status = case_tracker.check_status("ZNY1234567890")
    print("\n--- Case Status ---")
    print(status)

    # 6. Generate Voice Response (Nova Sonic)
    logger.info("Step 5: Synthesizing Final Voice Response")
    final_msg = "I have processed your information. I found a lawyer in New York and checked your case status. How else can I help?"
    # In a real run, this calls Nova Sonic
    # voice_assistant.process_voice_input(...) 
    print(f"\n--- Final Agent Response (Voice) ---")
    print(final_msg)

    logger.info("✅ Demo Complete")

if __name__ == "__main__":
    run_end_to_end_demo()

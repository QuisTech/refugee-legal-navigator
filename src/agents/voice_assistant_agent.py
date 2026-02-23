import os
from src.utils.nova_integration import nova_client
from src.utils.logger import logger

class VoiceAssistantAgent:
    def __init__(self):
        self.system_prompt = (
            "You are a helpful and empathetic AI assistant for refugee families. "
            "Your goal is to help them navigate asylum applications, find pro bono lawyers, "
            "and track their case status. Speak clearly and simply. "
            "Identify the user's needs and provide actionable advice based on their situation. "
            "If the user speaks a language other than English, identify the language and "
            "respond in that same language while maintaining a helpful tone."
        )

    def identify_language(self, text):
        """Uses Nova Lite to identify the language of the prompt."""
        logger.info("Identifying language of transcribed text")
        try:
            prompt = f"Identify the ISO 639-1 language code for the following text: '{text}'. Respond ONLY with the code (e.g., 'en', 'es', 'ar')."
            lang_code = nova_client.generate_response(prompt, "You are a language detection expert.")
            logger.info(f"Language identified: {lang_code}")
            return lang_code.strip().lower()
        except Exception as e:
            logger.error(f"Error identifying language: {e}")
            return "en"

    def process_voice_input(self, audio_bytes, content_type="audio/wav"):
        """
        Full pipeline: Audio -> Text -> Reasoning -> Response Text -> Audio Response
        """
        logger.info("Starting voice processing pipeline")
        
        try:
            # 1. Speech to Text
            transcribed_text = nova_client.transcribe_audio(audio_bytes, content_type)
            if not transcribed_text:
                logger.warning("No transcription obtained")
                return None, "I'm sorry, I couldn't hear you clearly. Could you please repeat that?"

            logger.info(f"User said: {transcribed_text}")

            # 1.5 Identify Language
            lang_code = self.identify_language(transcribed_text)
            
            # 2. Reasoning / Response Generation
            response_text = nova_client.generate_response(transcribed_text, self.system_prompt)
            logger.info(f"Agent response: {response_text}")

            # 3. Text to Speech
            # In a real Nova 2 Sonic implementation, the lang_code helps tune the accent/voice.
            audio_response = nova_client.text_to_speech(response_text)
            
            return audio_response, response_text

        except Exception as e:
            logger.error(f"Error in voice assistant pipeline: {e}")
            return None, "I encountered an error while processing your request. Please try again later."

    def save_audio_response(self, audio_bytes, filename="response.wav"):
        """Utility to save the generated audio to a file."""
        if audio_bytes:
            output_path = os.path.join("data", filename)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            logger.info(f"Saved audio response to {output_path}")
            return output_path
        return None

# Singleton instance
voice_assistant = VoiceAssistantAgent()

def process_voice_input(transcribed_text):
    """Fallback for the simplified run_voice_demo.py."""
    # Note: The simplified version in the walkthrough used text directly.
    # Here we bridge it to Nova Lite.
    return nova_client.generate_response(transcribed_text)

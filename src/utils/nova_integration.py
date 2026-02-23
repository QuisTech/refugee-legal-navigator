import boto3
import json
import base64
from src.utils.logger import logger

# Model IDs
NOVA_SONIC_V1 = "amzn.nova-2-sonic.v1"
NOVA_LITE_V1 = "amzn.nova-2-lite.v1"
EMBEDDING_V1 = "amazon.titan-embed-text-v1" # Adjust if Nova embeddings are specified differently

class NovaClient:
    def __init__(self, region_name="us-east-1"):
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )

    def transcribe_audio(self, audio_bytes, content_type="audio/wav"):
        """
        Uses Nova 2 Sonic for Speech-to-Text.
        Note: The actual Bedrock API for Nova Sonic might involve streaming or 
        specific body formats. This implementation follows the standard Bedrock invoke_model pattern.
        """
        logger.info(f"Transcribing audio with {NOVA_SONIC_V1}")
        try:
            # Prepare the request body for Nova Sonic transcription
            # Note: The exact schema for Nova Sonic might require tuning based on latest AWS docs.
            body = json.dumps({
                "audio": base64.b64encode(audio_bytes).decode("utf-8"),
                "contentType": content_type
            })

            response = self.bedrock_runtime.invoke_model(
                modelId=NOVA_SONIC_V1,
                body=body
            )

            response_body = json.loads(response.get("body").read())
            transcription = response_body.get("text", "")
            logger.info("Transcription successful")
            return transcription
        except Exception as e:
            logger.error(f"Error during audio transcription: {e}")
            raise

    def generate_response(self, prompt, system_prompt="You are a helpful assistant for refugees."):
        """
        Uses Nova 2 Lite for text generation/reasoning.
        """
        logger.info(f"Generating response with {NOVA_LITE_V1}")
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31", # Nova Lite often uses Converse or standard schemas
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            })

            response = self.bedrock_runtime.invoke_model(
                modelId=NOVA_LITE_V1,
                body=body
            )

            response_body = json.loads(response.get("body").read())
            # Handle different response formats if needed
            content = response_body.get("content", [])
            text = ""
            if content:
                text = content[0].get("text", "")
            
            logger.info("Response generation successful")
            return text
        except Exception as e:
            logger.error(f"Error during response generation: {e}")
            raise

    def text_to_speech(self, text):
        """
        Uses Nova 2 Sonic for Text-to-Speech.
        """
        logger.info(f"Synthesizing speech with {NOVA_SONIC_V1}")
        try:
            body = json.dumps({
                "text": text
            })

            response = self.bedrock_runtime.invoke_model(
                modelId=NOVA_SONIC_V1,
                body=body
            )

            response_body = response.get("body").read()
            # Nova Sonic TTS returns audio bytes directly or in a JSON field
            # Assuming bytes for now as per typical TTS outputs
            logger.info("Speech synthesis successful")
            return response_body
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")
            raise

# Singleton instance
nova_client = NovaClient()

def invoke_nova_model(model_id, prompt):
    """Fallback utility for simple text calls."""
    if model_id == NOVA_LITE_V1:
        return nova_client.generate_response(prompt)
    return "Unsupported model for simple invocation."

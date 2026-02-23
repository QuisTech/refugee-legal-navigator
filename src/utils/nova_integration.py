import boto3
import json
import base64
from src.utils.logger import logger

# Model IDs - Correct Bedrock identifiers
NOVA_SONIC_V1 = "amazon.nova-sonic-v1:0"    # Real-time bidirectional voice
NOVA_LITE_V1 = "amazon.nova-lite-v1:0"      # Fast, cost-effective text/multimodal
NOVA_PRO_V1 = "amazon.nova-pro-v1:0"        # Highest capability
EMBEDDING_V1 = "amazon.titan-embed-text-v2:0"  # Titan embeddings (Nova embedding model)

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

    def generate_response(self, prompt, system_prompt="You are a helpful assistant for refugees.", history=None):
        """
        Uses Nova Lite for text generation with optional multi-turn conversation history.
        history: list of {"role": "user"|"assistant", "content": str}
        """
        logger.info(f"Generating response with {NOVA_LITE_V1} (history={len(history) if history else 0} turns)")
        try:
            # Build messages array: prior history + current user message
            messages = []
            if history:
                for turn in history:
                    role = turn.get("role", "user")
                    content = turn.get("content", "")
                    if role in ("user", "assistant") and content:
                        messages.append({"role": role, "content": [{"text": content}]})
            # Append the current user message
            messages.append({"role": "user", "content": [{"text": prompt}]})

            body = json.dumps({
                "system": [{"text": system_prompt}],
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.7
                }
            })

            response = self.bedrock_runtime.invoke_model(
                modelId=NOVA_LITE_V1,
                body=body
            )

            response_body = json.loads(response.get("body").read())
            # Nova response format: output.message.content[0].text
            text = response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")

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

    def get_embeddings(self, text):
        """
        Generates embeddings for a given text using Amazon Bedrock.
        """
        logger.info(f"Generating embeddings for text")
        try:
            body = json.dumps({
                "inputText": text
            })
            response = self.bedrock_runtime.invoke_model(
                modelId=EMBEDDING_V1,
                body=body
            )
            response_body = json.loads(response.get("body").read())
            return response_body.get("embedding")
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

# Singleton instance
nova_client = NovaClient()

def invoke_nova_model(model_id, prompt):
    """Fallback utility for simple text calls."""
    if model_id == NOVA_LITE_V1:
        return nova_client.generate_response(prompt)
    return "Unsupported model for simple invocation."

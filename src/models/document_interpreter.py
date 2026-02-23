import base64
import json
import boto3
from src.utils.logger import logger

class DocumentInterpreter:
    def __init__(self, region_name="us-east-1"):
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        # Using Nova Lite which is multimodal
        self.model_id = "amzn.nova-2-lite.v1"

    def interpret_id_document(self, image_bytes, image_format="png"):
        """
        Interprets an ID document (passport, visa, etc.) from an image.
        Uses Nova Lite's multimodal capability.
        """
        logger.info(f"Interpreting document with {self.model_id}")
        try:
            # Nova models take a multimodal prompt
            # This is a general schema, adjust as per exact Nova multimodal input requirements
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{image_format}",
                                    "data": base64.b64encode(image_bytes).decode("utf-8")
                                }
                            },
                            {
                                "type": "text",
                                "text": "Extract all relevant information from this ID document, including name, date of birth, document number, and nationality."
                            }
                        ]
                    }
                ]
            })

            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body
            )

            response_body = json.loads(response.get("body").read())
            # Handle text content extraction
            content = response_body.get("content", [])
            text = ""
            if content:
                text = content[0].get("text", "")
            
            logger.info("Document interpretation successful")
            return text
        except Exception as e:
            logger.error(f"Error during document interpretation: {e}")
            return "Unable to interpret the document."

# Singleton instance
document_interpreter = DocumentInterpreter()

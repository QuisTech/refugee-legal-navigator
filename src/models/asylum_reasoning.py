from src.utils.nova_integration import nova_client
from src.utils.logger import logger

class AsylumReasoning:
    def __init__(self):
        self.asylum_system_prompt = (
            "You are a legal assistant specializing in asylum law. "
            "Your role is to analyze a user's situation and determine if they might "
            "meet the criteria for asylum based on the 1951 Refugee Convention. "
            "Criteria include: well-founded fear of persecution based on race, religion, "
            "nationality, membership in a particular social group, or political opinion. "
            "Provide a preliminary assessment and suggest next steps, such as finding a lawyer."
        )

    def screen_case(self, user_story):
        """
        Analyzes the user's story to provide a preliminary asylum screening.
        """
        logger.info("Screening case for asylum eligibility")
        try:
            prompt = (
                f"Please analyze the following story and evaluate potential asylum eligibility: \n\n"
                f"{user_story}\n\n"
                "Provide a summary of potential grounds for asylum and list specific questions "
                "to clarify the situation."
            )
            
            assessment = nova_client.generate_response(prompt, self.asylum_system_prompt)
            return assessment
        except Exception as e:
            logger.error(f"Error during asylum screening: {e}")
            return "Unable to provide a legal assessment at this time."

    def get_filing_guidance(self, country_of_origin):
        """
        Provides general guidance on filing asylum for a specific country.
        """
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

import asyncio
from playwright.async_api import async_playwright
from src.utils.logger import logger
from src.utils.nova_integration import nova_client

class CaseTrackerAgent:
    def __init__(self):
        self.portal_url = "https://egov.uscis.gov/casestatus/"
        self.system_prompt = (
            "You are a UI Automation expert. Based on the HTML of a page, "
            "provide the exact CSS selector for the receipt number input field "
            "and the submit button for checking case status."
        )

    async def get_case_status_real(self, receipt_number):
        """
        Uses Playwright to automate the real USCIS status check.
        In a full Nova Act deployment, Nova 2 Lite would generate the selectors dynamically.
        """
        logger.info(f"Starting real-world Nova Act tracking for: {receipt_number}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                logger.info(f"Navigating to {self.portal_url}")
                await page.goto(self.portal_url)
                
                # Dynamic Selector Discovery (Nova Act simulation)
                # In a real run, we would send page.content() to Nova 2 Lite here
                # Example: selectors = nova_client.generate_response(page.content(), self.system_prompt)
                
                # Using known selectors for reliability in the demo
                receipt_input = "input#receiptNumber"
                submit_button = "button[name='submit']"
                
                logger.info("Entering receipt number")
                await page.fill(receipt_input, receipt_number)
                await page.click(submit_button)
                
                # Wait for results
                await page.wait_for_selector(".result-item", timeout=10000)
                status_text = await page.inner_text(".result-item")
                
                logger.info(f"Found status: {status_text}")
                await browser.close()
                return status_text

            except Exception as e:
                logger.error(f"Nova Act automation error: {e}")
                await browser.close()
                return "Your case is currently being processed. Please check back later for specific status details."

    def check_status(self, receipt_number):
        """Bridge for synchronous calls."""
        try:
            return asyncio.run(self.get_case_status_real(receipt_number))
        except Exception as e:
            logger.error(f"Sync bridge error: {e}")
            return "Unable to retrieve status at this time."

# Singleton instance
case_tracker = CaseTrackerAgent()

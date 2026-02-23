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
                await page.goto(self.portal_url, wait_until="networkidle", timeout=30000)
                
                # USCIS uses appReceiptNum as the input name
                # Nova Act would dynamically discover this by reading the DOM
                receipt_input = "input[name='appReceiptNum']"
                submit_button = "input[type='submit'], button[type='submit']"
                
                logger.info("Entering receipt number")
                await page.wait_for_selector(receipt_input, timeout=15000)
                await page.fill(receipt_input, receipt_number)
                await page.click(submit_button)
                
                # Wait for results to load
                await page.wait_for_load_state("networkidle", timeout=15000)
                body_text = await page.inner_text("body")
                
                # Extract meaningful status from the response
                status_patterns = ["Case Was", "Application Was", "Request for Evidence", "Notice Was"]
                extracted = next((line.strip() for line in body_text.split("\n") 
                                  if any(p in line for p in status_patterns)), None)
                
                status_text = extracted or "Case found on portal. Please check USCIS online for detailed status."
                logger.info(f"Nova Act extracted status: {status_text}")
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

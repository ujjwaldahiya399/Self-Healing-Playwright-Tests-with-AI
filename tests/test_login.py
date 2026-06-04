# This is the main Playwright test file.
# It tests the login functionality on a demo website.
# When a selector breaks, it automatically calls the AI healer
# to find the correct selector and retry — without crashing.

import sys
import os
# Add the project root to the Python path so we can import healer.py
# from the utils folder regardless of where the test is run from.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
from utils.healer import heal_selector

# The website we are testing against.
# This is a public demo site specifically built for testing practice.
TEST_URL = "https://the-internet.herokuapp.com/login"

# Valid credentials for this demo site.
# These are publicly available on the site itself.
USERNAME = "tomsmith"
PASSWORD = "SuperSecretPassword!"

# This selector is intentionally wrong to simulate
# what happens when a developer renames an element in a UI update.
# The real button ID is "login-button" but we are using a broken one
# to demonstrate the self-healing capability.
BROKEN_LOGIN_BUTTON_SELECTOR = "#broken-login-btn"

def find_element_with_healing(page, selector):
    # This function tries to find an element using the given selector.
    # If the element is not found, it captures the page HTML,
    # sends it to the AI healer, and retries with the healed selector.
    # This is the core of the self-healing mechanism.

    # Step 1: Try finding the element with the original selector.
    print(f"\n[TEST] Looking for element: '{selector}'")
    element = page.query_selector(selector)

    if element:
        # Element found — no healing needed.
        print(f"[TEST] Element found with original selector.")
        return element, selector
    
    # Step 2: Element not found — self-healing kicks in.
    print(f"[TEST] Element NOT found. Starting self-healing process...")

    # Capture the full HTML of the current page.
    # This gives the AI enough context to find the correct element.
    page_html = page.content()

    # Send the broken selector and page HTML to the AI healer.
    # The healer returns the correct selector.
    healed_selector = heal_selector(selector, page_html)

    # Step 3: Retry finding the element with the healed selector.
    print(f"[TEST] Retrying with healed selector: '{healed_selector}'")
    element = page.query_selector(healed_selector)

    if element:
        print(f"[TEST] Element found after healing.")
        return element, healed_selector
    
    # Step 4: If still not found even after healing, raise an error.
    raise Exception(f"[TEST] Could not find element even after healing. Selector tried: '{healed_selector}'")

def test_login():
    # Main test function that runs the full login flow
    # with self-healing built in.

    # sync_playwright() starts the Playwright browser engine.
    with sync_playwright() as p:

        # Launch Chromium browser.
        # headless=False means the browser window is VISIBLE so you can watch it run.
        # Change to headless=True if you want it to run silently in the background.
        browser = p.chromium.launch(headless=True)

        # Open a new browser page (tab).
        page = browser.new_page()

        # Navigate to the login page of our demo site.
        print(f"\n[TEST] Navigating to {TEST_URL}")
        page.goto(TEST_URL)

        # Fill in the username field.
        # This selector is correct and will work fine.
        print("[TEST] Filling in username...")
        page.fill("#username", USERNAME)

        # Fill in the password field.
        # This selector is also correct.
        print("[TEST] Filling in password...")
        page.fill("#password", PASSWORD)

        # Try to find the login button using our intentionally broken selector.
        # The self-healing function will detect the failure and fix it automatically.
        login_button, used_selector = find_element_with_healing(
            page,
            BROKEN_LOGIN_BUTTON_SELECTOR
        )

        # Click the login button using whichever selector worked.
        print(f"[TEST] Clicking login button using selector: '{used_selector}'")
        login_button.click()

        # Wait for the page to load after clicking login.
        page.wait_for_load_state("networkidle")

        # Verify the login was successful by checking the URL.
        # After a successful login this site redirects to /secure.
        current_url = page.url
        print(f"[TEST] Current URL after login: {current_url}")

        if "/secure" in current_url:
            print("\n[TEST] LOGIN SUCCESSFUL - Test Passed.")
        else:
            raise Exception("[TEST] Login failed - did not reach the secure page.")

        # Close the browser cleanly.
        browser.close()


# Entry point — run the test when this file is executed directly.
if __name__ == "__main__":
    test_login()

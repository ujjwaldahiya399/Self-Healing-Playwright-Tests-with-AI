# This file contains the AI-powered self-healing logic.
# When a Playwright test cannot find an element on the page,
# this module takes over, sends the page HTML to an AI,
# and asks it to find the correct selector.

from groq import Groq
import os
import json

# The file where we store previously healed selectors.
# This acts as a cache so we don't call the AI repeatedly
# for the same broken selector.
HEALED_SELECTORS_FILE = "healed_selectors.json"

def load_healed_selectors():
    # Load the cache file if it exists.
    # If it doesn't exist yet, return an empty dictionary.
    if os.path.exists(HEALED_SELECTORS_FILE):
        with open(HEALED_SELECTORS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_healed_selector(broken_selector, healed_selector):
    # Save a newly discovered working selector into the cache file.
    # Next time the same broken selector is encountered,
    # we return the fix immediately without calling the AI.
    selectors = load_healed_selectors()
    selectors[broken_selector] = healed_selector
    with open(HEALED_SELECTORS_FILE, "w") as f:
        json.dump(selectors, f, indent=2)


def heal_selector(broken_selector, page_html):
    # This is the main healing function.
    # It takes the broken selector and the current page HTML,
    # checks the cache first, and if not found,
    # asks the AI to find the correct selector.

    # Step 1: Check if we have already healed this selector before.
    # If yes, return the cached fix without calling the AI.
    healed_selectors = load_healed_selectors()
    if broken_selector in healed_selectors:
        print(f"[HEALER] Found cached fix for '{broken_selector}' -> '{healed_selectors[broken_selector]}'")
        return healed_selectors[broken_selector]

    # Step 2: No cached fix found, so we need to ask the AI.
    print(f"[HEALER] No cache found for '{broken_selector}'. Asking AI...")

    # Connect to Groq using the API key stored in environment variables.
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Step 3: Build the prompt.
    # We give the AI the broken selector and the full page HTML,
    # and ask it to return only the correct CSS selector — nothing else.
    prompt = f"""
You are an expert QA automation engineer specializing in Playwright and CSS selectors.

A Playwright test tried to find an element using this selector:
"{broken_selector}"

But the element was not found on the page. The page HTML is below.

Your job is to:
1. Analyze the HTML carefully
2. Find the element that best matches what the original selector was trying to target
3. Return ONLY the correct CSS selector as a plain string
4. Do not include any explanation, markdown, or extra text — just the selector

Page HTML:
{page_html[:8000]}
"""
    # Note: We slice the HTML to 8000 characters to stay within
    # the AI model's token limit while still giving it enough context.

    # Step 4: Send the prompt to the AI model via Groq.
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    # Step 5: Extract the selector from the AI response.
    # Strip whitespace to make sure there are no accidental spaces.
    healed_selector = response.choices[0].message.content.strip()
    print(f"[HEALER] AI returned new selector: '{healed_selector}'")

    # Step 6: Save the healed selector to cache so we don't
    # need to call the AI again for the same broken selector.
    save_healed_selector(broken_selector, healed_selector)

    return healed_selector

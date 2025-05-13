import asyncio
import config
import aiohttp
import random
import string
import re
import time
import requests
import json
from playwright.async_api import async_playwright
from mailslurp_client import Configuration, ApiClient, WaitForControllerApi
from bs4 import BeautifulSoup


browser = None
page = None
playwright = None
credential_data = None


async def automate_password_reset(email):  # Just Sends Code
    global browser, page, playwright, credential_data

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    credential_data = None

    async def log_request(route, request):
        global request_payload
        print(f"Intercepted request URL: {request.url}")
        
        if "https://login.live.com/GetCredentialType.srf" in request.url:
            try:
                # Capture the POST data (payload) from the request
                if request.method == 'POST':  # Check if it's a POST request
                    request_payload = await request.post_data()
                    print(f"Captured Request Payload: {request_payload}")
                else:
                    print("Non-POST request, no payload.")
            except Exception as e:
                print(f"Error capturing request payload: {e}")
        await route.continue_()  # Continue the request, otherwise it will be blocked
    


    async def log_response(response):
        global credential_data
        if "https://login.live.com/GetCredentialType.srf" in response.url:
            try:
                
                response_text = await response.text()
                response_json = json.loads(response_text)
                proofs = response_json.get("Credentials", {}).get("OtcLoginEligibleProofs", [])
                if proofs and "data" in proofs[0]:
                    credential_data = proofs[0]["data"]
                    print(f"Credential Data Captured: {credential_data}")
            except Exception as e:
                print(f"Error parsing response: {e}")

    page.on("response", log_response)
    page.on("route", log_request)

    while True:
        try:
            await page.goto("https://login.live.com")
            await page.get_by_role("textbox", name="Email or phone number").wait_for(timeout=1000)
            break
        except Exception:
            print("Textbox not found, refreshing...")
            await page.reload()
    await page.get_by_role("textbox", name="Email or phone number").fill(email)
    await page.get_by_test_id("primaryButton").click()
    await page.wait_for_timeout(3000)

    if credential_data:
        print(f"Code sent to: {credential_data}")
        send_code(credential_data, email)
        try:
            other_ways_button = page.get_by_role("button", name="Other ways to sign in")
            if await other_ways_button.is_visible():
                await other_ways_button.click()
                await page.get_by_role("button", name="Send a code").click()
                await page.get_by_role("button", name="Already received a code?").click()
                return True
        except TimeoutError:
            pass
        try:
            received_code_button = page.get_by_role("button", name="Already received a code?")
            if await received_code_button.is_visible():
                await received_code_button.click()
                return True
        except TimeoutError:
            pass 
        try:
            await page.get_by_test_id("primaryButton").click()
            return True
        except TimeoutError:
            pass
            return False
    else:
        print("No 2FA Email")
        return False


async def automate_auto_change(email, code, newemail, newpass):  # Continue After Getting Code
    global browser, page, playwright

    if not page:
        print("No active session found. Run automate_password_reset first.")
        return

    try:
        for i, digit in enumerate(code, start=1):
            await page.get_by_role("textbox", name=f"Enter code digit {i}").fill(digit)

        await page.keyboard.press("Enter")
        await asyncio.sleep(2)

        try:
            ok_button = await page.wait_for_selector(
                'button.ms-Button.ms-Button--primary:has-text("OK")', timeout=5000
            )
            await ok_button.click()
        except Exception:
            pass

        ok_button = await page.query_selector("button[name='OK']")
        if ok_button:
                await ok_button.click()
        secondary_button = await page.query_selector("[data-testid='primaryButton']")
        if secondary_button:
            await secondary_button.click()

        await page.wait_for_load_state('load')
        context = page.context
        cookies = await context.cookies()
        for cookie in cookies:
            if cookie['name'] == '__Host-MSAAUTHP':
                print(f"Cookie __Host-MSAAUTHP: {cookie['value']}")
                config.LastCookie= {cookie['value']}
        await asyncio.sleep(15)
        try:
            await page.locator('[aria-label="Close"]').click()
        except:
            pass

        security_drawer_locator = page.locator("[id=\"home\\.drawers\\.security\"] > div > div > div > div > div > div > div > div")
        await security_drawer_locator.wait_for(state="visible", timeout=5000)
        await security_drawer_locator.click()

        additional_security_text_locator = page.locator("text=Additional security options")
        await additional_security_text_locator.nth(1).wait_for(state="visible", timeout=10000)
        await additional_security_text_locator.nth(1).scroll_into_view_if_needed()
        await additional_security_text_locator.nth(1).click()


        await handle_recovery_code(page)

        # Add new email
        await page.get_by_role("button", name="Add a new way to sign in or").click()
        await page.get_by_role("button", name="Show more options").click()
        await page.get_by_role("button", name="Email a code Get an email and").click()
        await page.get_by_placeholder("someone@example.com").fill(newemail)
        await page.click('input.btn.btn-block.btn-primary#iNext')
        security_code = get_security_code_by_email(config.MAILSLURP_API_KEY, newemail)
        await page.fill("#iOttText", security_code)
        await page.click("#iNext")

        # Demote/remove old email
        await page.wait_for_selector('div#Email0 .pullout-link-text:has-text("Email a code")', timeout=10000)
        await page.click('div#Email0 .pullout-link-text:has-text("Email a code")')
        await page.click('button#Remove')
        await page.click('button#iBtn_action')

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        await asyncio.sleep(5)
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()


async def handle_recovery_code(page):
    """Handle recovery code generation and extraction."""
    if await page.is_visible("#RecoveryCodeLink"):
        print("Found 'Generate a new code' link. Clicking it...")
        await page.click("#RecoveryCodeLink")
        await page.wait_for_selector("#ModalContent", timeout=5000)
        modal_content = await page.query_selector("#ModalContent")
        if modal_content:
            modal_html = await modal_content.inner_html()
            match = re.search(r'<strong>([A-Z0-9\-]+)</strong>', modal_html)
            if match:
                recovery_code = match.group(1)
                config.LastRecoveryCode = recovery_code
                print(f"New recovery code set: {config.LastRecoveryCode}")
            else:
                print("Failed to extract recovery code from modal content.")
        else:
            print("Modal content not found.")
        await page.get_by_role("button", name="Got it").click()


def get_security_code_by_email(api_key, email_address, timeout=90000):
    if not email_address.endswith("@mailslurp.biz"):
        print("Invalid email address. It must end with '@mailslurp.biz'.")
        return None
    
    inbox_id = email_address.replace("@mailslurp.biz", "")
    
    config = Configuration()
    config.api_key['x-api-key'] = api_key
    
    with ApiClient(config) as api_client:
        wait_api = WaitForControllerApi(api_client)
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:  # Convert timeout to seconds
            try:
                email = wait_api.wait_for_latest_email(inbox_id=inbox_id, timeout=5000)
                if email:
                    # Parse the HTML email body
                    soup = BeautifulSoup(email.body, "html.parser")
                    
                    # Look for text containing "Security code:" and get the next span element
                    security_text = soup.find(text=lambda text: text and "Security code:" in text)
                    if security_text:
                        # Get the next span element which contains the code
                        code_span = security_text.find_next('span')
                        if code_span:
                            security_code = code_span.get_text().strip()
                            print(f"Found security code: {security_code}")
                            return security_code
                    
                    print("Security code pattern not found in email")
                    return None
                    
            except Exception as e:
                if "No emails found" in str(e):
                    print("No new email found. Retrying...")
                    time.sleep(5)
                else:
                    print(f"An error occurred: {e}")
                    return None
        
        print("Timeout reached without finding a security code.")
        return None
    


def generate_password(length=16):
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"
    
    password = [
        random.choice(uppercase),
        random.choice(lowercase),
        random.choice(digits),
        random.choice(symbols)
    ]
    
    all_characters = uppercase + lowercase + digits + symbols
    password += random.choices(all_characters, k=length - 4)
    random.shuffle(password)
    
    return ''.join(password)


async def CreateRandomEmail():
    BASE_URL = "https://api.mailslurp.com"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": config.MAILSLURP_API_KEY
    }
    url = f"{BASE_URL}/inboxes"

    # Use aiohttp with SSL verification bypassed
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(url, headers=headers) as response:
            if response.status == 201:
                inbox = await response.json()
                print(f"Email Address Generated: {inbox['emailAddress']}")
                return inbox['emailAddress']
            else:
                error_text = await response.text()
                raise Exception(f"Failed to create inbox: {response.status} - {error_text}")
                

def send_code(sec_id, email):
    try:
        url = "https://login.live.com/GetOneTimeCode.srf"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": ("MSPRequ=id=N&lt=1710339166&co=1; uaid=c91a322ee1b4429680b0ea8f66c093a0; "
                       "MSCC=197.120.88.59-EG; MSPOK=$uuid-146ab8a8-c9d0-4bb1-aa27-547da7d29c2e; "
                       "OParams=11O.DtGQ6hN13OJzMvlgcsbk3K1MJr*X68!Ot3yO3k6RSI06blohFE2hyzV47ZO5tLXE6D0m99QK34YAxLCQDz3U1Nwyqy2Ov*hJkMvLwJXKbYUIjSGgHieTerUPAdR6FgtL0BzQq8XqFSgSdvzmclJqKpzC0GvHtf*jA5WjBZyVV5OSII6OIjJzM8v256KIa95Jzj14D1QDiteTtl5yjezcl!ntryM4c*L*FOCgYxrA8MD9oya8pFHntdG4l5NgaUHkKencTODUnk6EbqD0Scud3qYyArpTBs7ryxY7AUWiqHf1tEwSAEzpGdVVlnooi!h0*w$$; "
                       "MicrosoftApplicationsTelemetryDeviceId=8d42cd67-e191-4485-b99f-61acde87e85c; "
                       "ai_session=xgIvNnBy7/HaB8dU2XGZWs|1710339167277|1710339167277; "
                       "MSFPC=GUID=254359f779a247ddb178d133b367ad82&HASH=2543&LV=202403&V=4&LU=1710339171328")
        }
        data = f"login={email}&flowtoken=-DvTDvmRgphmpW9oJRrYLB1YGD*aPHnUeOf3zvwQABaxrG8WwdFr6jD12imzrE3D2AhdfsKbazoW5G0AvCvO9Thz!9VzxnGUlAbtWqwft34nll3cx2ge2pRYsrK5Sq6BtZbObPlJ2tDiwu3gRDgBjzFldYn*rt9By5D!6QUKFoC8pFtKS949tDFokpG0BpT07ig$$&purpose=eOTT_OtcLogin&channel=Email&AltEmailE={sec_id}"
        
        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()

        if response_data.get("State") == 201:
            print("Sent Code!")
        else:
            print("Failed to send the code!")  # Need to update every time with the new secID
    except Exception as error:
        print(f"An error occurred: {error}")


async def fill_and_press(page, selector, text):
    """Helper function to fill input and press Enter."""
    await page.fill(selector, text)
    await page.press(selector, "Enter")
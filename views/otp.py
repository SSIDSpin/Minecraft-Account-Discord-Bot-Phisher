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

import asyncio
from playwright.async_api import async_playwright

async def automate_password_reset(email):  # Just Sends Code
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set `headless=True` to run in headless mode
        page = await browser.new_page()

        # Variable to store the data field from the response
        credential_data = None

        

        # Event listener to intercept the specific network response
        async def log_response(response):
            nonlocal credential_data
            if "https://login.live.com/GetCredentialType.srf" in response.url:
                try:
                    response_text = await response.text()
                    response_json = json.loads(response_text)  # Parse response as JSON
                    proofs = response_json.get("Credentials", {}).get("OtcLoginEligibleProofs", [])
                    if proofs and "data" in proofs[0]:
                        credential_data = proofs[0]["data"]
                except Exception as e:
                    print(f"Error parsing response: {e}")

        # Add event listener for responses
        page.on("response", log_response)

        # Navigate to the login page
        await page.goto("https://login.live.com/")
        await page.fill("input#i0116", email)
        await page.press("input#i0116", "Enter")
        await asyncio.sleep(2)

        try:
            if await page.is_visible("#otcLoginLink"):
                link_text = await page.inner_text("#otcLoginLink")
                if re.search(r"\*", link_text):
                    await browser.close()
                    send_code(credential_data,email)
                else:   
                    await page.click("#otcLoginLink")
                    await asyncio.sleep(4)
                    await browser.close()
            else:
                await page.click("#idA_PWD_SwitchToCredPicker")
                await browser.close()
                await asyncio.sleep(2)
                send_code(credential_data,email)
        except Exception as e:
            print(f"Error: {e}")

        if credential_data:
            print("Extracted 'data' field from OtcLoginEligibleProofs:")
            print(credential_data)
        else:
            print("No Email A Code Turned On")
            return False

async def fill_and_press(page, selector, text):
    """Helper function to fill input and press Enter."""
    await page.fill(selector, text)
    await page.press(selector, "Enter")

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

async def automate_auto_change(email, code, newemail, newpass):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            await page.goto("https://login.live.com/")
            await fill_and_press(page, "input#i0116", email)
            await asyncio.sleep(2)  # Replace with better wait if possible

            # Handle 2FA or OTC flow
            if await page.is_visible("#idA_PWD_SwitchToCredPicker"):
                await page.click("#idA_PWD_SwitchToCredPicker")
                await asyncio.sleep(5)
                email_locator = page.locator('div[data-testid="mainText"]', has_text="Email")
                await email_locator.click()
                try:
                    await page.wait_for_selector("#proofConfirmationToggle", timeout=15000)  # Wait for up to 15 seconds
                    await page.click("#proofConfirmationToggle")
                except Exception:
                    pass
                await page.fill('[data-testid="idTxtBx_OTC_Password"]', code)
                await page.press('[data-testid="idTxtBx_OTC_Password"]', "Enter")
                await page.check("#checkboxField")
                await page.click("#acceptButton")
                #Get Cookies
                context = page.context
                cookies = await context.cookies()
                for cookie in cookies:
                    if cookie['name'] == '__Host-MSAAUTHP':
                        print(f"Cookie __Host-MSAAUTHP: {cookie['value']}")
                        config.LastCookie= {cookie['value']}

                print("Cookie __Host-MSAAUTHP not found.")

                #May Need To Add Some Try Catch Statements As There Are Some Odd Pop Ups I Cant Remember About

                try: #Checks For Phone Pop Up
                    popup_locator = page.locator(".ms-Stack.dialogBody.css-191").nth(0)
                    await popup_locator.wait_for(timeout=20000)
                    close_button = page.locator("button#landing-page-dialog\\.close")
                    await close_button.click()
                except Exception:
                    pass
                await page.locator("#home\\.drawers\\.security").click()
                await page.get_by_text("Additional security options").nth(1).click()
                await asyncio.sleep(4)
                await handle_recovery_code(page)



                # Add a new email for account
                await page.get_by_role("button", name="Add a new way to sign in or").click()
                await page.get_by_role("button", name="Show more options").click()
                await page.get_by_role("button", name="Email a code Get an email and").click()
                await page.get_by_placeholder("someone@example.com").fill(newemail)
                await page.click('input.btn.btn-block.btn-primary#iNext')

                # Retrieve and fill security code
                security_code = get_security_code_by_email(config.MAILSLURP_API_KEY, newemail)
                await page.fill("#iOttText", security_code)
                await page.click("#iNext")

                # Demote old email
                await page.wait_for_selector('div#Email0 .pullout-link-text:has-text("Email a code")', timeout=10000)
                await page.click('div#Email0 .pullout-link-text:has-text("Email a code")')
                await page.click('button#Remove')
                await page.click('button#iBtn_action')

            else:
                print("Unexpected flow encountered. Adjust the logic accordingly.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await asyncio.sleep(5)
            await browser.close()


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
                
async def ForgotPasswordCode(newpassword,oldemail,newemail):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set `headless=True` to run in headless mode
        page = await browser.new_page()
        await page.goto("https://login.live.com/")
        await page.fill("input#i0116", oldemail)
        await page.press("input#i0116", "Enter")
        await asyncio.sleep(2)
        try:
            is_visible = await page.is_visible('span#idA_PWD_SwitchToPassword:has-text("Use your password instead")')
            if is_visible:
                await page.click('span#idA_PWD_SwitchToPassword:has-text("Use your password instead")')
            else:
                await page.wait_for_selector('span#idA_PWD_ForgotPassword', timeout=5000)  # Wait for it to be visible
                await page.click('span#idA_PWD_ForgotPassword')  # Click the Forgot Password span
                radio_button_id = 'textproofOption0'  # The id of the radio button
                await page.wait_for_selector(f'input#{radio_button_id}', timeout=5000)
                await page.click(f'input#{radio_button_id}')
                await page.wait_for_selector('input#proofInput0', timeout=5000)
                newemailid = newemail.replace("@mailslurp.biz", "")
                print(newemailid)
                await page.fill('input#proofInput0', newemailid)
                print("Entered Email Fine")
            await page.click('button#iSelectProofAction[aria-describedby="iSelectProofTitle"]')
            print("Selected IProofAction")
            newsecurity_code = get_here_code_by_email(config.MAILSLURP_API_KEY, newemail)
            print("new scruity Code" + newsecurity_code)
            await page.wait_for_selector('input#iVerifyText', timeout=5000)
            await page.fill('input#iVerifyText', newsecurity_code)
            await page.click('button#iVerifyIdentityAction[aria-describedby="iVerifyIdentityTitle"]')
            await page.wait_for_selector('input#iPassword', timeout=5000)  # Wait for the password field to be visible
            await page.fill('input#iPassword', newpassword)
            await page.wait_for_selector('input#iRetypePassword', timeout=5000)  # Wait for the retype password field to be visible
            await page.fill('input#iRetypePassword', newpassword)
            await page.click('button#iResetPasswordAction[aria-labelledby="UpdatePasswordTitle"]')
            await asyncio.sleep(5)

        except Exception as e:
            print(f"{e}")
        await asyncio.sleep(5)

def get_here_code_by_email(api_key, email_address, timeout=90000):
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
                    
                    # Look specifically for "Here is your code:"
                    security_text = soup.find(text=lambda text: text and "Here is your code:" in text)
                    if security_text:
                        # Get the next span element which contains the code
                        code_span = security_text.find_next('span') if hasattr(security_text, 'find_next') else None
                        if code_span:
                            security_code = code_span.get_text().strip()
                            print(f"Found security code: {security_code}")
                            return security_code
                        else:
                            print("Code span not found.")
                    else:
                        print("Security code pattern not found in email.")
            except Exception as e:
                if "No emails found" in str(e):
                    print("No new email found. Retrying...")
                    time.sleep(5)
                else:
                    print(f"An error occurred: {e}")
                    return None
        
        print("Timeout reached without finding a security code.")
        return None



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

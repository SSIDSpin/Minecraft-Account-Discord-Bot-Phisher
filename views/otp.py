import asyncio
import config
import aiohttp
import random
import string
import re
import time
from playwright.async_api import async_playwright
from mailslurp_client import Configuration, ApiClient, WaitForControllerApi
from bs4 import BeautifulSoup

async def automate_password_reset(email): #Just Sends Code
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set `headless=True` to run in headless mode
        page = await browser.new_page()
        await page.goto("https://login.live.com/")
        await page.fill("input#i0116", email)
        await page.press("input#i0116", "Enter")
        await asyncio.sleep(2)

        try:
            if await page.is_visible("#otcLoginLink"):
                await page.click("#otcLoginLink")
                await asyncio.sleep(4)
            else:
                await page.click("#idA_PWD_SwitchToCredPicker")
                await asyncio.sleep(4)
                # Need To Fix This So That Incase They Have Multiple Verification Methods
                # And If They Do Error Checking And Responses
        except Exception as e:
            pass

        await browser.close()


async def automate_auto_change(email, code, newemail, newpass):
    async with async_playwright() as p:
        browser2 = await p.chromium.launch(headless=True)
        page = await browser2.new_page()
        await page.goto("https://login.live.com/")
        await page.fill("input#i0116", email)
        await page.press("input#i0116", "Enter")
        await page.wait_for_timeout(2000)
        try:
            if await page.is_visible("#otcLoginLink"):
                await page.click("#otcLoginLink")
                await asyncio.sleep(4)
                await page.wait_for_selector('[data-testid="idTxtBx_OTC_Password"]', timeout=5000)
                await page.get_by_test_id("idTxtBx_OTC_Password").fill(code)  
                await page.get_by_test_id("idTxtBx_OTC_Password").press("Enter")
                await page.get_by_test_id("checkboxField").check()
                await page.wait_for_selector("#acceptButton", timeout=5000)
                await page.click("#acceptButton")
                await asyncio.sleep(5)
                popup_locator = page.locator(".ms-Stack.dialogBody.css-191").nth(0)
                await popup_locator.wait_for(timeout=20000)  # If it crashes saying something along the lines of ms-Stack not found/not visible change this number to higher
                print("Phone Number Request Pop Up")
                close_button = page.locator("button#landing-page-dialog\\.close")
                await close_button.click()
                await page.locator("#home\\.drawers\\.security").click()
                await page.get_by_text("Additional security options").nth(1).click()
                await asyncio.sleep(4)
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
                    await page.get_by_role("button", name="Add a new way to sign in or").click()
                    await page.get_by_role("button", name="Show more options").click()
                    await page.get_by_role("button", name="Email a code Get an email and").click()
                    await page.get_by_placeholder("someone@example.com").fill(newemail)
                    await page.click('input.btn.btn-block.btn-primary#iNext')
                    security_code = get_security_code_by_email(config.MAILSLURP_API_KEY, newemail)
                    print(security_code)
                    await page.fill("#iOttText", security_code)
                    await page.click("#iNext")
                    #Make The Email The Main Email And Change Demote the other
                    await page.wait_for_selector('div#Email0 .pullout-link-text:has-text("Email a code")', timeout=10000)
                    await page.click('div#Email0 .pullout-link-text:has-text("Email a code")')
                    await page.click('button#Remove')
                    await page.wait_for_selector('button#iBtn_action', timeout=5000)
                    await page.click('button#iBtn_action')





                elif await page.is_visible('text=I have a code'):
                    await page.get_by_role("button", name="I have a code").click()
                    await page.get_by_test_id("otc-confirmation-input").fill(code) 
                    await page.get_by_label("Verify").click()
                else:
                    await page.get_by_label("Close").click()
                    print("Neither 'Generate a new code' nor 'I have a code' options are available.")


            else: # Incase it auto asks for code
                await page.wait_for_selector('[data-testid="idTxtBx_OTC_Password"]', timeout=5000)
                await page.get_by_test_id("idTxtBx_OTC_Password").fill(code)  
                await page.get_by_test_id("idTxtBx_OTC_Password").press("Enter")
                await page.get_by_test_id("checkboxField").check()
                await page.wait_for_selector("#acceptButton", timeout=5000)
                await page.click("#acceptButton")
                await asyncio.sleep(5)
                popup_locator = page.locator(".ms-Stack.dialogBody.css-191").nth(0)
                await popup_locator.wait_for(timeout=10000)  # Wait for up to 10 seconds
                print("Phone Number Request Pop Up")
                close_button = page.locator("button#landing-page-dialog\\.close")
                await close_button.click()
                await page.locator("#home\\.drawers\\.security").click()
                await page.get_by_text("Additional security options").nth(1).click()
                await asyncio.sleep(4)
                if await page.is_visible("#RecoveryCodeLink"):
                    print("Found 'Generate a new code' link. Clicking it...")
                    await page.click("#RecoveryCodeLink")
                    await page.wait_for_selector("#ModalContent", timeout=5000)  # Wait for the modal to load
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
                    await page.get_by_role("button", name="Add a new way to sign in or").click()
                    await page.get_by_role("button", name="Show more options").click()
                    await page.get_by_role("button", name="Email a code Get an email and").click()
                    await page.get_by_placeholder("someone@example.com").fill(newemail)
                    await page.click('input.btn.btn-block.btn-primary#iNext')
                    await asyncio.sleep(10)
                    security_code = get_security_code_by_email(config.MAILSLURP_API_KEY, newemail)
                    print(security_code)
                    await page.fill("#iOttText", security_code)
                    await page.click("#iNext")
                    #Make The Email The Main Email And Change Demote the other
                    await page.wait_for_selector('div#Email0 .pullout-link-text:has-text("Email a code")', timeout=10000)
                    await page.click('div#Email0 .pullout-link-text:has-text("Email a code")')
                    await page.click('button#Remove')
                    await page.wait_for_selector('button#iBtn_action', timeout=5000)
                    await page.click('button#iBtn_action')





                elif await page.is_visible('text=I have a code'):
                    await page.get_by_role("button", name="I have a code").click()
                    await page.get_by_test_id("otc-confirmation-input").fill(code) 
                    await page.get_by_label("Verify").click()
                else:
                    await page.get_by_label("Close").click()
                    print("Neither 'Generate a new code' nor 'I have a code' options are available.")

        except Exception as e:
            print("OTC password field not found or other issue:", e)
        await asyncio.sleep(5)
        await browser2.close()


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

    # Perform the asynchronous API request
    async with aiohttp.ClientSession() as session:
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

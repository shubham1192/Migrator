from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright, TimeoutError
import re

app = Flask(__name__)
CORS(app)  # allow frontend on another port to call backend

# Temporary store session info (for demo; in prod, use proper session management)
sessions = {}

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    apple_id = data.get("apple_id")
    password = data.get("password")



    print(apple_id, password)

    if not apple_id or not password:
        return jsonify({"status": "error", "message": "Missing Apple ID or password"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto("https://music.apple.com/us/new")


            page.wait_for_timeout(5000)    
            
            page.get_by_role("button", name="Sign In").click()
            # page.pause()
            
            page.wait_for_timeout(5000)     

            apple_frame = None
            for f in page.frames:
                try:
                    el = f.query_selector("[data-test='accountName-input']")
                    if el:
                        apple_frame = f
                        # print(f"Found Apple login frame: {f}")
                        break
                except:
                    continue

            # print(apple_frame.name)
            x=str(apple_frame)
            print("print",x)



            import re

            match = re.search(r"name=([^ ]+)", x)   #biffurcating step
            if match:
                name_part = match.group(1)
                print(name_part)

            # for f in page.frames():
            #     print("Frame URL:", f.url)

            # page.pause()
            apple_input = page.locator(
    f'iframe[name="{name_part}"]'
).content_frame.locator("[data-test='accountName-input']")
            print(apple_input)
            apple_input.fill(apple_id)
            
            page.wait_for_timeout(5000)     

            continue_btn = page.locator(
    f'iframe[name="{name_part}"]'
).content_frame.locator("[data-test='layout-onboarding-auth-button']")

            continue_btn.wait_for(state="visible", timeout=5000)
            continue_btn.click()
            print("Continue clicked")
            # page.pause()
            page.wait_for_timeout(5000)     


            outer_frame = page.locator(
    f'iframe[name="{name_part}"]'
).content_frame

# select innervrame
            inner_frame = outer_frame.locator('iframe[name="aid-auth-widget"]').content_frame

            # fill pswd
            inner_frame.get_by_role("textbox", name="Password").fill(password)
            # page.pause()
            page.wait_for_timeout(5000)     
            
            inner_frame.get_by_role("button", name="Sign In").click()
            # page.pause()
            page.wait_for_timeout(5000)     


            
            page.pause()


    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# @app.route("/verify-otp", methods=["POST"])
# def verify_otp():
#     data = request.json
#     session_id = data.get("session_id")
#     otp = data.get("otp")

#     if session_id not in sessions:
#         return jsonify({"status": "error", "message": "Invalid session"}), 400

#     session = sessions[session_id]
#     page = session["page"]
#     browser = session["browser"]

#     try:
#         # Enter OTP
#         page.fill("input[name='verificationCode']", otp)
#         page.click("button[type='submit']")

#         # Wait for login success confirmation
#         try:
#             page.wait_for_selector("text=Account Summary", timeout=5000)
#             browser.close()
#             del sessions[session_id]
#             return jsonify({"status": "login_success"})
#         except TimeoutError:
#             browser.close()
#             del sessions[session_id]
#             return jsonify({"status": "otp_failed"})

#     except Exception as e:
#         browser.close()
#         del sessions[session_id]
#         return jsonify({"status": "error", "message": str(e)})
        

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

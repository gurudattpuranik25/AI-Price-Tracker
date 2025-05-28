from playwright.sync_api import sync_playwright
import time
import threading
import pywhatkit
from bson import ObjectId
from app import mongo

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_price(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=60000)
            if "flipkart.com" in url:
                title = page.locator("span.VU-ZEz").text_content()
                price_text = page.locator("div.Nx9bqj.CxhGGd").text_content()
                price = int(price_text.replace("₹", "").replace(",", "").strip())
                # image = page.locator("img#landingImage.a-dynamic-image.a-stretch-vertical").get_attribute("src")
            elif "amazon." in url:
                title = page.locator("#productTitle.a-size-large.product-title-word-break").text_content().strip()
                price_text = page.locator("span.a-price-whole").first.text_content().strip()
                price = int(price_text.replace("₹", "").replace(",", "").replace(".", ""))
                # image = page.locator("img.DByuf4.IZexXJ.jLEJ7H").get_attribute("src")
            else:
                title = None
                price = None
        except Exception as e:
            print("Error checking price:", e)
            title = price = None
        browser.close()
        return title, price

def price_check_worker():
    print("🔁 Background price checker started")
    try:
        while True:
            products = list(mongo.db.products.find())
            print(f"🔎 Found {len(products)} products")
            for product in products:
                try:
                    url = product["url"]
                    target_price = product["target_price"]
                    phone = product["phone_number"]
                    user_id = product.get("user_id")
                    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
                    receiver = user["email"]
                    title, current_price = get_price(url)
                    if title and current_price:
                        print(f"Checked: {title} | Current: ₹{current_price} | Target: ₹{target_price}")
                        if current_price <= int(target_price):
                            message = f"✅ Price dropped for {title}! ₹{current_price}. {url}"
                            try:
                                sender = "guruhp999@gmail.com"
                                app_password = "riwk imjq pytk ckop"
                                subject = f"Price Drop Alert! Your Target Price Hit for {title}!"
                                body = f"""\
                                Hi there,

                                Great news! The price for **{title}** has just dropped to **{current_price}**. That's below your target price!

                                Don't miss out – grab it before it's gone!

                                {url}

                                Happy shopping,
                                DropWatch
                                """
                                #pywhatkit.sendwhatmsg_instantly(phone, message)
                                send_email(sender, app_password, receiver, subject, body, is_html=False)
                                mongo.db.products.delete_one({"_id": ObjectId(product["_id"])})
                                print(f"🟢 Notification sent and product removed.")
                            except Exception as e:
                                print("❌ Failed to send WhatsApp:", e)
                        else:
                            print(f"🔴 Price not dropped for {title}.")
                    else:
                        print(f"⚠️ Failed to fetch title/price for URL: {url}")
                except Exception as e:
                    print("❌ Error during product processing:", e)
            time.sleep(10)
    except Exception as e:
        print("❌ price_check_worker crashed:", e)

def send_email(sender_email, sender_password, receiver_email, subject, body, is_html=False):

    # Replace with your SMTP server details
    smtp_server = "smtp.gmail.com"  # For Gmail
    smtp_port = 587  # For TLS

    # Create a multipart message and set headers
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the body (plain text or HTML)
    if is_html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
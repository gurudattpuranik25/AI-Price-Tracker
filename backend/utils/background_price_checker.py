import os
import time
from bson import ObjectId
from playwright.sync_api import sync_playwright
from app import create_app, mongo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


INTERVAL = int(os.environ.get("PRICE_CHECK_INTERVAL", 10))  # default: 1 hour


def get_price(url):
    """Fetch price from Flipkart or Amazon product pages using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=60000)

            if "flipkart.com" in url:
                page.wait_for_selector("span.VU-ZEz", timeout=15000)
                page.wait_for_selector("div.Nx9bqj.CxhGGd", timeout=15000)

                title = page.locator("span.VU-ZEz").text_content()
                price_text = page.locator("div.Nx9bqj.CxhGGd").text_content()
                price = int(price_text.replace("₹", "").replace(",", "").strip())
                return title, price

            elif "amazon." in url:
                page.set_extra_http_headers({
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "accept-language": "en-US,en;q=0.9",
                })
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                if "Enter the characters you see below" in page.content():
                    print("🛑 Amazon bot protection triggered.")
                    return None, None

                title = page.locator("span#productTitle").text_content().strip()
                price_locators = page.locator("span.a-price > span.a-offscreen")
                for price_text in price_locators.all_text_contents():
                    if "₹" in price_text:
                        return title, int(price_text.replace("₹", "").replace(",", "").split(".")[0].strip())

                return title, None

            return None, None

        except Exception as e:
            print("❌ Error fetching price:", e)
            return None, None
        finally:
            browser.close()


def send_email(sender_email, sender_password, receiver_email, subject, body, is_html=False):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"📧 Email sent to {receiver_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def price_check_worker():
    """Loop through products and send alerts if prices drop."""
    app = create_app()
    with app.app_context():
        print("🔁 Background price checker started")

        while True:
            products = list(mongo.db.products.find())
            print(f"🔎 Checking {len(products)} products")

            for product in products:
                try:
                    url = product["url"]
                    target_price = product["target_price"]
                    user_id = product.get("user_id")

                    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
                    if not user:
                        continue

                    receiver = user["email"]
                    title, current_price = get_price(url)

                    if title and current_price:
                        print(f"Checked {title}: ₹{current_price} vs Target ₹{target_price}")
                        if current_price <= int(target_price):
                            subject = f"Price Drop Alert! {title}"
                            body = f"""
                            Hi {user.get("name", "there")},

                            Great news! The price for **{title}** just dropped to ₹{current_price}, 
                            which is below your target price of ₹{target_price}.

                            👉 {url}

                            Happy shopping,
                            DropWatch
                            """

                            send_email(
                                os.environ["EMAIL_USER"],
                                os.environ["EMAIL_PASS"],
                                receiver,
                                subject,
                                body,
                                is_html=False
                            )

                            # remove after notifying
                            mongo.db.products.delete_one({"_id": ObjectId(product["_id"])})
                            print(f"🟢 Alert sent + product removed")
                    else:
                        print(f"⚠️ Failed to fetch {url}")

                except Exception as e:
                    print("❌ Error in product loop:", e)

            time.sleep(INTERVAL)


if __name__ == "__main__":
    price_check_worker()

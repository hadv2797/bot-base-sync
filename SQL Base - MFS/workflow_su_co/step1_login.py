import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://workflow.base.vn/qtxulysuco-12626"
USERNAME = "ha.dv@manfusi.com"
PASSWORD = "RXZZL48Q4C"

def login_and_get_page(playwright_instance):
    print("--- KHỞI TẠO & ĐĂNG NHẬP BASE ---")
    
    # Dùng luôn playwright_instance (biến p) truyền từ ngoài vào
    browser = playwright_instance.chromium.launch(headless=True)
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        permissions=['notifications']
    )
    page = context.new_page()

    print("1. Đang mở trang Base Workflow...")
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)

    # Đăng nhập Email
    if "account.base.vn" in page.url or page.query_selector("input[name='email']"):
        print("2. Nhập Email...")
        page.fill("input[name='email']", USERNAME)
        page.wait_for_timeout(500)

        btn_ok = page.locator("div.ok").first
        if btn_ok.count() > 0 and btn_ok.is_visible():
            btn_ok.click()
        else:
            page.press("input[name='email']", "Enter")

        # Đăng nhập Mật khẩu
        print("3. Nhập Mật khẩu...")
        page.wait_for_selector("input[name='password']", timeout=15000)
        page.fill("input[name='password']", PASSWORD)
        page.wait_for_timeout(500)

        btn_login_ok = page.locator("div.ok").first
        if btn_login_ok.count() > 0 and btn_login_ok.is_visible():
            btn_login_ok.click()
        else:
            page.press("input[name='password']", "Enter")

        page.wait_for_url(lambda url: "workflow.base.vn" in url, timeout=30000)
        print("-> ✅ Đăng nhập thành công!")

    page.wait_for_timeout(3000)

    # Xử lý Popup
    print("4. Xử lý Popup thông báo...")
    popup_btn = page.locator("text='TIẾP TỤC'").first
    if popup_btn.count() > 0 and popup_btn.is_visible():
        popup_btn.click()
        print("-> ✅ Đã tắt Popup!")
    
    # Trả về 2 giá trị đúng khớp với line 21 của bro: browser, page = login_and_get_page(p)
    return browser, page
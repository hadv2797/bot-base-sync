import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://workflow.base.vn/qtxulysuco-12626"
USERNAME = "ha.dv@manfusi.com"
PASSWORD = "RXZZL48Q4C"

def login_and_get_page(playwright_instance):
    print("--- KHỞI TẠO & ĐĂNG NHẬP BASE ---")
    
    browser = playwright_instance.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
            "--disable-render-backgrounding",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-component-extensions-with-background-pages",
        ]
    )
    
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={'width': 1920, 'height': 1080},
        permissions=['notifications']
    )
    page = context.new_page()

    print("1. Đang mở trang Base Workflow...")
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)

    # Nếu bị đẩy về trang Login
    if "account.base.vn" in page.url or page.locator("input[name='email']").is_visible():
        print("2. Nhập Email...")
        page.wait_for_selector("input[name='email']", timeout=15000)
        page.fill("input[name='email']", USERNAME)
        page.wait_for_timeout(500)

        # Click nút Tiếp tục (xử lý cả dạng div.ok lẫn button)
        btn_continue = page.locator("form div.ok, form button[type='submit'], input[type='submit']").first
        if btn_continue.is_visible():
            btn_continue.click()
        else:
            page.press("input[name='email']", "Enter")

        print("3. Nhập Mật khẩu...")
        page.wait_for_selector("input[name='password']", timeout=15000)
        page.fill("input[name='password']", PASSWORD)
        page.wait_for_timeout(500)

        # Force Click nút Đăng nhập
        btn_login = page.locator("form div.ok, form button[type='submit'], input[type='submit']").first
        if btn_login.is_visible():
            btn_login.click(force=True)
        else:
            page.press("input[name='password']", "Enter")

        print("Đang chờ tải dữ liệu Workflow...")
        # Thay vì wait_for_url, ta chờ trực tiếp một element đặc trưng của Base Workflow xuất hiện
        try:
            page.wait_for_selector("body", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            print("Cảnh báo: Network chưa idle nhưng vẫn tiếp tục...")

        print("-> ✅ Đăng nhập & Chuyển trang hoàn tất!")

    page.wait_for_timeout(3000)

    # Xử lý Popup thông báo
    print("4. Xử lý Popup thông báo...")
    try:
        popup_btn = page.locator("text='TIẾP TỤC'").first
        if popup_btn.is_visible(timeout=3000):
            popup_btn.click()
            print("-> ✅ Đã tắt Popup!")
    except Exception:
        pass
    
    return browser, page

if __name__ == "__main__":
    with sync_playwright() as p:
        browser, page = login_and_get_page(p)
        print("Tiêu đề trang:", page.title())
        browser.close()

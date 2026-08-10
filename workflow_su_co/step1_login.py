import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://workflow.base.vn/qtxulysuco-12626"
USERNAME = "ha.dv@manfusi.com"
PASSWORD = "RXZZL48Q4C"

def login_and_get_page(playwright_instance):
    print("--- KHỞI TẠO & ĐĂNG NHẬP BASE ---")
    
    # 1. Khởi tạo Chromium (Đã bỏ --single-process gây crash và sửa định dạng cờ)
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
    
    # 2. Giả dạng User-Agent trình duyệt thật
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={'width': 1920, 'height': 1080},
        permissions=['notifications']
    )
    page = context.new_page()

    print("1. Đang mở trang Base Workflow...")
    try:
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=90000)
    except Exception as e:
        print(f"Lần 1 goto chập chờn, thử lại... Chi tiết: {e}")
        page.goto(BASE_URL, wait_until="commit", timeout=90000)

    page.wait_for_timeout(2000)

    # 3. Đăng nhập Email
    if "account.base.vn" in page.url or page.query_selector("input[name='email']"):
        print("2. Nhập Email...")
        page.wait_for_selector("input[name='email']", timeout=30000)
        page.fill("input[name='email']", USERNAME)
        page.wait_for_timeout(500)

        # Ưu tiên gửi phím Enter trực tiếp để tránh lỗi click trượt nút OK
        page.press("input[name='email']", "Enter")

        # 4. Đăng nhập Mật khẩu
        print("3. Nhập Mật khẩu...")
        page.wait_for_selector("input[name='password']", timeout=30000)
        page.fill("input[name='password']", PASSWORD)
        page.wait_for_timeout(500)

        page.press("input[name='password']", "Enter")

        # FIX LỖI TIMEOUT: Thay lambda bằng chuỗi pattern URL chuẩn của Playwright
        print("Đang chờ chuyển hướng vào Workflow...")
        page.wait_for_url("**/workflow.base.vn/**", timeout=60000, wait_until="domcontentloaded")
        print("-> ✅ Đăng nhập thành công!")

    page.wait_for_timeout(3000)

    # 5. Xử lý Popup thông báo (nếu có)
    print("4. Xử lý Popup thông báo...")
    try:
        popup_btn = page.locator("text='TIẾP TỤC'").first
        if popup_btn.is_visible(timeout=5000):
            popup_btn.click()
            print("-> ✅ Đã tắt Popup!")
    except Exception:
        print("-> Không xuất hiện popup.")
    
    return browser, page


# KHỐI THỰC THI (Giúp bấm Run trên VS Code hoặc chạy lệnh python là hoạt động)
if __name__ == "__main__":
    with sync_playwright() as p:
        browser, page = login_and_get_page(p)
        print("Tiêu đề trang hiện tại:", page.title())
        page.wait_for_timeout(5000) # Giữ 5s để quan sát
        browser.close()

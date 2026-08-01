import os
import sys
import time
import random
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.sync_api import sync_playwright

# Đảm bảo Python nhận đúng các module trong cùng thư mục
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from step1_login import login_and_get_page
from step2_scrape import scrape_nghiem_thu_ban_giao
from step3_push_db import push_jobs_to_supabase

# ==========================================
# 1. DUMMY SERVER CHO RENDER HEALTH CHECK
# (Giải quyết lỗi 'No open ports detected')
# ==========================================
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is healthy and running!")
        def log_message(self, format, *args):
            return  # Tắt log HTTP thừa trên Render console

    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Bật HTTP server chạy ngầm ở luồng riêng ngay khi khởi chạy
threading.Thread(target=run_dummy_server, daemon=True).start()

# ==========================================
# 2. CẤU HÌNH VÀ LOGIC CHÍNH
# ==========================================
START_HOUR = 6   # 6h sáng
END_HOUR = 22    # 22h tối

def is_working_hours():
    """Kiểm tra xem hiện tại có nằm trong khoảng 6h - 22h không"""
    now = datetime.now() + timedelta(hours=7)
    return START_HOUR <= now.hour < END_HOUR

def run_single_pipeline():
    """
    Chạy trọn gói 1 chu kỳ cào data:
    Khởi tạo Browser -> Load session/storage_state -> Cào -> Push DB -> Đóng triệt để Browser xả RAM
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n==================================================")
    print(f"🚀 [{current_time}] BẮT ĐẦU CHẠY ĐỒNG BỘ XỬ LÝ SỰ CỐ")
    print(f"==================================================")

    browser = None
    try:
        with sync_playwright() as p:
            # Khởi tạo browser & nạp storage_state đã lưu sẵn trong login_and_get_page
            browser, page = login_and_get_page(p)

            print("🔄 Đang làm mới trang...")
            page.reload(wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # 1. Cào dữ liệu từ cột Sự cố
            jobs = scrape_nghiem_thu_ban_giao(page)

            # 2. Đẩy lên Supabase (bảng thong_tin_su_co)
            push_jobs_to_supabase(jobs)

            print("🏁 Hoàn thành chu kỳ đồng bộ dữ liệu!")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra trong quá trình xử lý: {e}")

    finally:
        # Bắt buộc đóng browser sau mỗi chu kỳ để giải phóng 100% RAM
        if browser:
            try:
                browser.close()
                print("🧹 Đã đóng trình duyệt & xả RAM hoàn toàn về 0MB!")
            except Exception:
                pass

def main():
    print(f"🤖 Bot Auto-Sync Supabase (Xử Lý Sự Cố) đã khởi động!")
    print(f"⏰ Khung giờ hoạt động: {START_HOUR}:00 - {END_HOUR}:00 hàng ngày.\n")

    while True:
        if is_working_hours():
            # Run 1 chu kỳ duy nhất (mở browser -> cào -> đóng browser)
            run_single_pipeline()

            # Random thời gian nghỉ từ 1100s đến 1300s (~18 - 21 phút)
            sleep_seconds = random.randint(1100, 1300)
            next_run = datetime.now() + timedelta(seconds=sleep_seconds)
            
            print(f"⏰ Lần cập nhật tiếp theo: {next_run.strftime('%H:%M:%S')}")
            print(f"💤 Tạm dừng {sleep_seconds} giây (Trạng thái rảnh RAM)...")
            time.sleep(sleep_seconds)

        else:
            # Chế độ nghỉ đêm (sau 22h đêm đến trước 6h sáng)
            now_str = datetime.now().strftime("%H:%M:%S")
            print(f"🌙 [{now_str}] Đã ngoài giờ làm việc (nghỉ từ {END_HOUR}h - {START_HOUR}h).")
            print("💤 Đang ngủ đêm... Kiểm tra lại sau 10 phút.")
            time.sleep(600)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng chương trình thủ công (Ctrl+C)!")

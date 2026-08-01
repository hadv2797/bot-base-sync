import time
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

from step1_login import login_and_get_page
from step2_scrape import scrape_nghiem_thu_ban_giao
from step3_push_db import push_jobs_to_supabase  # Đã sửa lại tên hàm đúng với step3

# Cấu hình khung giờ hoạt động (Khung giờ làm việc)
START_HOUR = 6   # 6h sáng
END_HOUR = 22    # 10h tối (22h)

def is_working_hours():
    """Kiểm tra xem hiện tại có nằm trong khoảng 6h - 22h không"""
    now = datetime.now()
    return START_HOUR <= now.hour < END_HOUR

def run_pipeline(page):
    """Hàm xử lý cào và push DB cho Xử lý sự cố"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n==================================================")
    print(f"🚀 [{current_time}] BẮT ĐẦU CHẠY ĐỒNG BỘ XỬ LÝ SỰ CỐ")
    print(f"==================================================")

    try:
        print("🔄 Đang làm mới trang...")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # 1. Cào dữ liệu từ cột Sự cố
        jobs = scrape_nghiem_thu_ban_giao(page)

        # 2. Đẩy lên Supabase (bảng thong_tin_su_co)
        push_jobs_to_supabase(jobs)

    except Exception as e:
        print(f"❌ Có lỗi xảy ra trong quá trình xử lý: {e}")

    print("🏁 Hoàn thành chu kỳ đồng bộ dữ liệu!")

def main():
    print(f"🤖 Bot Auto-Sync Supabase (Xử Lý Sự Cố) đã khởi động!")
    print(f"⏰ Khung giờ hoạt động: {START_HOUR}:00 - {END_HOUR}:00 hàng ngày.\n")

    with sync_playwright() as p:
        browser, page = login_and_get_page(p)

        try:
            while True:
                if is_working_hours():
                    # --- BẬT CHẾ ĐỘ LÀM VIỆC (6h - 22h) ---
                    run_pipeline(page)

                    # Random thời gian nghỉ từ 110s đến 130s (~2 phút) để giống người thật
                    sleep_seconds = random.randint(1100, 1300)
                    next_run = datetime.now() + timedelta(seconds=sleep_seconds)
                    
                    print(f"⏰ Lần cập nhật tiếp theo: {next_run.strftime('%H:%M:%S')}")
                    print(f"💤 Tạm dừng {sleep_seconds} giây...")
                    time.sleep(sleep_seconds)

                else:
                    # --- BẬT CHẾ ĐỘ NGỦ ĐÊM (21h - 7h) ---
                    now_str = datetime.now().strftime("%H:%M:%S")
                    print(f"🌙 [{now_str}] Đã ngoài giờ làm việc (sau {END_HOUR}h).")
                    
                    # Check lại giờ mỗi 10 phút (600s) xem đã đến 7h sáng chưa
                    time.sleep(600)

        finally:
            browser.close()
            print("🔒 Đã đóng trình duyệt an toàn.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng chương trình thủ công (Ctrl+C)!")
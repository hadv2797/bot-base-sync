import time
from playwright.sync_api import sync_playwright

def parse_stage_118754(page):
    print("--- BẮT ĐẦU QUÉT DỮ LIỆU CỘT STAGE-118754 ---")
    
    # 1. Chờ trang tải hoàn toàn và cuộn trang nhẹ để kích hoạt Lazy Load
    page.wait_for_load_state("domcontentloaded")
    page.mouse.wheel(0, 500)
    page.wait_for_timeout(2000)

    # 2. Thử chờ stage xuất hiện trong tối đa 15 giây
    try:
        page.wait_for_selector("#stage-118754", timeout=15000, state="attached")
        print("-> ✅ Đã tìm thấy cột #stage-118754 trên DOM!")
    except Exception:
        print("⚠️ Không thấy ID #stage-118754 theo cách thông thường, chuyển sang quét theo Title...")

    # 3. Lấy Element Stage (Ưu tiên ID -> Sau đó đến tên Giai đoạn)
    stage_locator = page.locator("#stage-118754")
    if stage_locator.count() == 0:
        stage_locator = page.locator(".stage").filter(
            has=page.locator("span", has_text="Xác nhận hoàn thành với khách hàng")
        ).first

    if stage_locator.count() == 0:
        print("❌ Vẫn không tìm thấy cột stage. Vui lòng kiểm tra lại quyền tài khoản hoặc URL!")
        return []

    # 4. Trích xuất danh sách công việc (Jobs) bên trong Stage
    jobs_data = []
    job_items = stage_locator.locator(".item.--job-wrapper").all()
    print(f"-> 🎯 Tìm thấy {len(job_items)} công việc trong giai đoạn này.")

    for item in job_items:
        # Lấy Job ID & Token
        job_id = item.get_attribute("data-id")
        
        # Lấy Tiêu đề job
        title_el = item.locator(".name").first
        title = title_el.inner_text().strip() if title_el.count() > 0 else ""
        
        # Lấy Mô tả ngắn / Tagline
        tagline_el = item.locator(".tagline").first
        tagline = tagline_el.inner_text().strip() if tagline_el.count() > 0 else ""
        
        # Lấy danh sách Tags
        tags = [t.inner_text().strip() for t in item.locator(".ui-tag").all()]
        
        # Lấy Người phụ trách (Assignee)
        uname_el = item.locator(".uname").first
        assignee = uname_el.inner_text().strip() if uname_el.count() > 0 else ""
        
        # Lấy Thời hạn
        time_el = item.locator(".time").first
        deadline = time_el.inner_text().strip() if time_el.count() > 0 else ""

        payload = {
            "job_id": job_id,
            "title": title,
            "tagline": tagline,
            "tags": tags,
            "assignee": assignee,
            "deadline": deadline,
            "stage_id": "118754"
        }
        jobs_data.append(payload)

    print(f"-> ✅ Trích xuất thành công {len(jobs_data)} bản ghi!")
    return jobs_data

from datetime import datetime
import re
from playwright.sync_api import Page

def scrape_nghiem_thu_ban_giao(page: Page):
    print("🔍 Đang cào dữ liệu từ cột 'Xác nhận hoàn thành với khách hàng'...")
    
    # 1. Ép DOM render và cuộn nhẹ trang để kích hoạt Lazy Load dữ liệu của Base
    page.wait_for_load_state("domcontentloaded")
    page.mouse.wheel(0, 500)
    page.wait_for_timeout(2000)

    # 2. Xử lý selector Stage linh hoạt (Ưu tiên ID -> Sau đó đến Tên Stage)
    stage_el = None
    try:
        # Thử tìm theo ID trước
        page.wait_for_selector("#stage-118754", timeout=10000, state="attached")
        stage_el = page.query_selector("#stage-118754")
    except Exception:
        print("⚠️ Không thấy #stage-118754, đang tìm Stage theo tên 'Xác nhận hoàn thành với khách hàng'...")

    if not stage_el:
        # Fallback: Tìm stage theo Tên hiển thị
        stages = page.query_selector_all(".stage")
        for s in stages:
            title_node = s.query_selector(".title span")
            if title_node and "Xác nhận hoàn thành với khách hàng" in title_node.inner_text():
                stage_el = s
                break

    if not stage_el:
        print("❌ Không tìm thấy cột 'Xác nhận hoàn thành với khách hàng' trên giao diện!")
        return []

    # 3. Lấy danh sách job items trong Stage
    job_elements = stage_el.query_selector_all(".items .--job-wrapper")
    print(f"📊 Tìm thấy {len(job_elements)} công việc trong cột.")

    jobs_data = []
    scraped_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for job_el in job_elements:
        try:
            job_id = job_el.get_attribute("data-id")

            # Xử lý Timestamp cập nhật
            last_update_ts = job_el.get_attribute("data-last_update")
            if last_update_ts and last_update_ts.isdigit():
                updated_at = datetime.fromtimestamp(int(last_update_ts)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                updated_at = scraped_now

            # Tiêu đề công việc
            name_el = job_el.query_selector(".name")
            job_title = name_el.inner_text().strip() if name_el else ""

            # Tagline / Nội dung ngắn
            tagline_el = job_el.query_selector(".tagline")
            tagline_text = tagline_el.inner_text().strip() if tagline_el else ""

            # Danh sách Tags
            tag_list_attr = job_el.get_attribute("data-taglist") or ""
            tags = tag_list_attr.split() if tag_list_attr else []

            # Người phụ trách
            uname_el = job_el.query_selector(".uname")
            assignee = uname_el.inner_text().strip() if uname_el else ""

            # Chuẩn hóa URL chi tiết của Job
            url_el = job_el.query_selector(".name.url")
            raw_url = url_el.get_attribute("data-url") if url_el else ""
            
            job_url = ""
            if raw_url:
                clean_path = raw_url.replace(":job/", "job/").replace("/open_job", "").lstrip("/")
                job_url = f"https://workflow.base.vn/{clean_path}"

            job_item = {
                "job_id": job_id,
                "job_title": job_title,
                "assignee": assignee,
                "tagline_info": tagline_text,
                "tags": tags,
                "url": job_url,
                "first_seen_at": scraped_now,
                "updated_at": updated_at,
                "stage_name": "Xác nhận hoàn thành với khách hàng",
            }

            jobs_data.append(job_item)

        except Exception as e:
            print(f"⚠️ Lỗi parse item job_id={job_id if 'job_id' in locals() else 'N/A'}: {e}")
            continue

    return jobs_data

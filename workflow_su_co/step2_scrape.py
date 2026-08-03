from datetime import datetime
import re
from playwright.sync_api import Page


def scrape_nghiem_thu_ban_giao(page: Page):
    print("🔍 Đang cào dữ liệu từ cột 'Xác nhận hoàn thành với khách hàng'...")
    stage_selector = "#stage-118754"

    try:
        page.wait_for_selector(stage_selector, timeout=15000)
    except Exception:
        print(f"⚠️ Không tìm thấy cột với selector {stage_selector}")
        return []

    job_elements = page.query_selector_all(
        f"{stage_selector} .items .--job-wrapper"
    )
    print(f"📊 Tìm thấy {len(job_elements)} công việc trong cột.")

    jobs_data = []
    # Lấy ngày hiện tại khi bot chạy cào (Định dạng YYYY-MM-DD HH:MM:SS)
    scraped_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for job_el in job_elements:
        try:
            job_id = job_el.get_attribute("data-id")

            # Lấy timestamp cập nhật gần nhất từ attribute data-last_update của Base
            last_update_ts = job_el.get_attribute("data-last_update")
            updated_at = (
                datetime.fromtimestamp(int(last_update_ts)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if last_update_ts
                else scraped_now
            )

            name_el = job_el.query_selector(".name")
            job_title = name_el.inner_text().strip() if name_el else ""

            tagline_el = job_el.query_selector(".tagline")
            tagline_text = (
                tagline_el.inner_text().strip() if tagline_el else ""
            )

            tag_list_attr = job_el.get_attribute("data-taglist") or ""
            tags = tag_list_attr.split() if tag_list_attr else []

            uname_el = job_el.query_selector(".uname")
            assignee = uname_el.inner_text().strip() if uname_el else ""

            url_el = job_el.query_selector(".name.url")
            raw_url = url_el.get_attribute("data-url") if url_el else ""
            job_url = (
                f"https://workflow.base.vn/{raw_url.replace(':job/', 'job/').replace('/open_job', '')}"
                if raw_url
                else ""
            )

            job_item = {
                "job_id": job_id,
                "job_title": job_title,
                "assignee": assignee,
                "tagline_info": tagline_text,
                "tags": tags,
                "url": job_url,
                "first_seen_at": scraped_now,  # Ngày đầu tiên bot cào được
                "updated_at": updated_at,  # Ngày cập nhật từ Base
                "stage_name": "Xác nhận hoàn thành với khách hàng",
            }

            jobs_data.append(job_item)

        except Exception as e:
            print(f"⚠️ Lỗi parse item: {e}")
            continue

    return jobs_data

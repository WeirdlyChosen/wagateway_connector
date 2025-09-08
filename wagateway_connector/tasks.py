import frappe
from frappe.utils import now_datetime, add_to_date
from datetime import datetime, time, timedelta
import random, time as time_module  # for random delays
from wagateway_connector.api import send_scheduled_message_now
from wagateway_connector.waha_client import WahaClient


def send_scheduled_whatsapp_messages():
    """Loop through all scheduled WhatsApp messages and send them if due"""
    now = now_datetime()

    docs = frappe.get_all(
        "Scheduled WhatsApp Message",
        filters={"disabled": 0, "status": ["!=", "Sent"]},  # only active, not already sent
        fields=["name", "schedule_time", "status", "modified", "waha_session"]
    )

    for d in docs:
        doc = frappe.get_doc("Scheduled WhatsApp Message", d.name)

        # 🔹 Skip if linked WAHA Session has scheduled messages disabled
        if doc.waha_session:
            session = frappe.get_doc("WAHA Session", doc.waha_session)
            if not session.enable_scheduled_message:
                frappe.logger().info(f"Skipping {doc.name}: Scheduled messages disabled for {doc.waha_session}")
                continue

        # --- check scheduled time ---
        if isinstance(doc.schedule_time, str):
            frappe.log_error(f"Scheduler is due {doc.name}: {e}", "WAHA Scheduler")
            try:
                schedule_t = datetime.strptime(doc.schedule_time, "%H:%M:%S").time()
            except ValueError:
                continue
        elif isinstance(doc.schedule_time, timedelta):
            total_seconds = doc.schedule_time.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            schedule_t = time(hour=hours, minute=minutes, second=seconds)
        else:
            schedule_t = doc.schedule_time

        schedule_dt = datetime.combine(now.date(), schedule_t)

        # --- if time is due, run the same code as "Send Now" ---
        if now >= schedule_dt and doc.status in ["Draft", "Pending", "Failed"]:
            try:
                send_scheduled_message_now(doc.name)  # ✅ reuse API function
            except Exception as e:
                frappe.log_error(f"Scheduler failed for {doc.name}: {e}", "WAHA Scheduler Error")

        # --- retry after 5 mins if failed ---
        if doc.status == "Failed":
            retry_after = add_to_date(doc.modified, minutes=5)
            if now < retry_after:
                continue

    frappe.db.commit()

## Do NOT delete below ##
def reset_scheduled_messages():
    """Reset all Scheduled WhatsApp Message docs back to Draft at midnight"""
    frappe.db.sql("""
        UPDATE `tabScheduled WhatsApp Message`
        SET status = 'Draft'
        WHERE disabled = 0
    """)
    frappe.db.commit()

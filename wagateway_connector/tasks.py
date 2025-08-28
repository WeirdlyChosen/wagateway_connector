import frappe
from frappe.utils import now_datetime, add_to_date
from wagateway_connector.waha_client import WahaClient
from datetime import datetime, time, timedelta


def process_single_message(docname):
    frappe.logger().info(f"➡️ Entered process_single_message for {docname}") # logger

    now = now_datetime()
    client = WahaClient()
    doc = frappe.get_doc("Scheduled WhatsApp Message", docname)

    # If message is still in Draft, move it to Pending before cron tries to send
    if doc.status == "Draft":
        doc.status = "Pending"
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    contacts = [c.strip() for c in (doc.contacts or "").split(",") if c.strip()]
    success = True

    for chat_id in contacts:
        try:
            client.send_text(chat_id=chat_id, text=doc.message,
                             session=doc.waha_session or client.default_session)

            # create Communication log on success
            comm = frappe.new_doc("Communication")
            comm.communication_medium = "WhatsApp"
            comm.sent_or_received = "Sent"
            comm.content = doc.message
            comm.recipients = chat_id
            comm.reference_doctype = doc.doctype
            comm.reference_name = doc.name
            comm.timeline_doctype = doc.doctype
            comm.timeline_name = doc.name
            comm.subject = (f"WhatsApp message sent to {chat_id}")[:140]
            comm.status = "Linked"
            comm.communication_date = now
            comm.insert(ignore_permissions=True)

        except Exception as e:
            success = False
            
            # failure log
            comm = frappe.new_doc("Communication")
            comm.communication_medium = "WhatsApp"
            comm.sent_or_received = "Sent"
            comm.content = f"Failed to send message: {e}"
            comm.recipients = chat_id
            comm.reference_doctype = doc.doctype
            comm.reference_name = doc.name
            comm.subject = (f"WhatsApp send failed to {chat_id}")[:140]
            comm.status = "Failed"
            comm.communication_date = now
            comm.insert(ignore_permissions=True)

            # set status to Failed ONLY if send actually failed
            doc.status = "Failed"
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "Failed"}

    # only set Sent if there were contacts and sending worked
    if success and contacts:
        doc.status = "Sent"
        doc.save(ignore_permissions=True)
        frappe.db.commit()
    elif not contacts:
        # keep Pending if no contacts, don’t wrongly mark as Sent
        return {"status": "No Contacts"}


def send_scheduled_whatsapp_messages():
    """Loop through all scheduled WhatsApp messages and send them if due"""
    frappe.log_error(message="Scheduler triggered", title="WAHA Cron Test") # logger
    frappe.logger().info("🔔 Scheduler triggered send_scheduled_whatsapp_messages") # logger
    now = now_datetime()
    frappe.logger().info(f"🚀 Scheduler triggered at {now}") # logger

    docs = frappe.get_all(
        "Scheduled WhatsApp Message",
        filters={"disabled": 0},  # check all active messages
        #filters={"disabled": 0, "status": ["!=", "Sent"]},  # only active, not already sent
        fields=["name", "schedule_time", "status", "modified"]
    )

    frappe.logger().info(f"Found {len(docs)} scheduled messages to check") # logger    

    for d in docs:
        doc = frappe.get_doc("Scheduled WhatsApp Message", d.name)
        frappe.logger().info(f"Processing doc: {doc.name}, status={doc.status}, schedule_time={doc.schedule_time}") # logger


        # --- check scheduled time ---
        if isinstance(doc.schedule_time, str):
            try:
                schedule_t = datetime.strptime(doc.schedule_time, "%H:%M:%S").time()
            except ValueError:
                frappe.log_error(f"Invalid time string for {doc.name}: {doc.schedule_time}", "WhatsApp Scheduler")
                continue
        else:
            schedule_t = doc.schedule_time

        schedule_dt = datetime.combine(now.date(), schedule_t)
        if now < schedule_dt:
            continue  # not yet time

        # --- retry after 5 mins if failed ---
        if doc.status == "Failed":
            retry_after = add_to_date(doc.modified, minutes=5)
            if now < retry_after:
                continue

        # --- process the single message ---
        process_single_message(doc.name)

    frappe.db.commit()


def reset_scheduled_messages():
    """Reset all Scheduled WhatsApp Message docs back to Draft at midnight"""
    frappe.db.sql("""
        UPDATE `tabScheduled WhatsApp Message`
        SET status = 'Draft'
        WHERE disabled = 0
    """)
    frappe.db.commit()

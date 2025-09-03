import frappe
from frappe.utils import now_datetime, add_to_date
from wagateway_connector.waha_client import WahaClient
from datetime import datetime, time, timedelta



def process_single_message(docname):
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
                             session=doc.waha_session)
            frappe.log_error(message=f"Sending to {chat_id}", title="WAHA sending") #   logger to error log

            # create Communication log on success
            comm = frappe.new_doc("Communication")
            comm.communication_medium = "Chat"
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
            comm.communication_medium = "Chat"
            comm.sent_or_received = "Sent"
            comm.content = f"Failed to send message: Payload: chat_id={chat_id}, text={doc.message}, session={doc.waha_session} | {e}"
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
    now = now_datetime()

    docs = frappe.get_all(
        "Scheduled WhatsApp Message",
        filters={"disabled": 0, "status": ["!=", "Sent"]},  # only active, not already sent
        fields=["name", "schedule_time", "status", "modified"]
    )

    for d in docs:
        doc = frappe.get_doc("Scheduled WhatsApp Message", d.name)

        # --- check scheduled time ---
        if isinstance(doc.schedule_time, str):
            try:
                schedule_t = datetime.strptime(doc.schedule_time, "%H:%M:%S").time()
            except ValueError:
                continue
        else:
            # If it's a timedelta, convert to time
            if isinstance(doc.schedule_time, timedelta):
                total_seconds = doc.schedule_time.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                schedule_t = time(hour=hours, minute=minutes, second=seconds)
            else:
                schedule_t = doc.schedule_time

        # Combine today's date with the scheduled time
        schedule_dt = datetime.combine(now.date(), schedule_t)

        if now >= schedule_dt and doc.status in ["Draft", "Pending", "Failed"]:
            process_single_message(doc.name)

        # --- retry after 5 mins if failed ---
        if doc.status == "Failed":
            retry_after = add_to_date(doc.modified, minutes=5)
            if now < retry_after:
                continue

    frappe.db.commit()


def reset_scheduled_messages():
    """Reset all Scheduled WhatsApp Message docs back to Draft at midnight"""
    frappe.db.sql("""
        UPDATE `tabScheduled WhatsApp Message`
        SET status = 'Draft'
        WHERE disabled = 0
    """)
    frappe.db.commit()

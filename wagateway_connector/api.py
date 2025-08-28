import frappe
from wagateway_connector.waha_client import WahaClient

@frappe.whitelist()
def test_connection():
    """Test WAHA connectivity by calling /api/sessions"""
    try:
        client = WahaClient()
        sessions = client.get_sessions()
        frappe.msgprint(f"✅ Connected to WAHA!\n\nFound {len(sessions)} sessions.")
        return sessions
    except Exception as e:
        frappe.throw(f"❌ Connection failed: {e}")

@frappe.whitelist()
def fetch_all_waha_sessions():
    """Sync all WAHA sessions from API into WAHA Session doctype"""
    client = WahaClient()
    sessions = client.get_sessions()
    from frappe.utils import now_datetime

    updated = []
    for s in sessions:
        name = s.get("name")
        if not name:
            continue

        doc = frappe.get_doc("WAHA Session", {"session_name": name}) \
              if frappe.db.exists("WAHA Session", {"session_name": name}) \
              else frappe.new_doc("WAHA Session")

        doc.session_name = name
        doc.status = s.get("status")
        doc.engine = s.get("engine")
        doc.last_sync = now_datetime()
        doc.info_json = frappe.as_json(s, indent=2)

        doc.save(ignore_permissions=True)
        updated.append(name)

    frappe.db.commit()
    return {"updated": updated}

@frappe.whitelist()
def refresh_waha_session(docname: str):
    """Refresh a single WAHA Session from the API and update the doctype"""
    client = WahaClient()
    sessions = client.get_sessions()
    session = next((s for s in sessions if s.get("name") == docname), None)

    if not session:
        frappe.throw(f"Session {docname} not found in WAHA")

    doc = frappe.get_doc("WAHA Session", {"session_name": docname})
    doc.status = session.get("status")
    doc.engine = session.get("engine")
    from frappe.utils import now_datetime
    doc.last_sync = now_datetime()
    doc.info_json = frappe.as_json(session, indent=2)
    doc.save(ignore_permissions=True)

    return {"status": doc.status}

@frappe.whitelist()
def test_waha_session(docname: str):
    """Test if a WAHA session is alive"""
    client = WahaClient()
    sessions = client.get_sessions()
    session = next((s for s in sessions if s.get("name") == docname), None)

    if not session:
        frappe.throw(f"Session {docname} not found in WAHA")

    return {"status": session.get("status")}

@frappe.whitelist()
def send_scheduled_message_now(docname: str):
    """Manually send a Scheduled WhatsApp Message"""
    doc = frappe.get_doc("Scheduled WhatsApp Message", docname)
    client = WahaClient()

    contacts = [c.strip() for c in (doc.contacts or "").split(",") if c.strip()]
    if not contacts:
        frappe.throw("No contacts found to send message")

    for chat_id in contacts:
        try:
            client.send_text(
                chat_id=chat_id,
                text=doc.message,
                session=doc.waha_session or client.default_session
            )
            # log communication
            comm = frappe.new_doc("Communication")
            comm.communication_medium = "WhatsApp"
            comm.sent_or_received = "Sent"
            comm.content = doc.message
            comm.recipients = chat_id
            comm.reference_doctype = "Scheduled WhatsApp Message"
            comm.reference_name = doc.name
            comm.timeline_doctype = "Scheduled WhatsApp Message"   # ✅ show in Activity
            comm.timeline_name = doc.name
            comm.subject = (f"WhatsApp message sent to {chat_id}")[:140]
            comm.status = "Linked"
            comm.communication_date = frappe.utils.now_datetime()
            comm.insert(ignore_permissions=True)

        except Exception as e:
            doc.status = "Failed"
            doc.save(ignore_permissions=True)
            frappe.throw(f"❌ Failed to send to {chat_id}: {e}")

    doc.status = "Sent"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "success", "doc": doc.name}

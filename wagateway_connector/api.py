import frappe
import requests
import re # sanitizer
import random # send WA message
import time # send WA message
from wagateway_connector.waha_client import WahaClient

#### Helpers ####
def sanitize_contact_name(name: str) -> str:
    """Remove emojis, symbols, and special characters from contact name."""
    if not name:
        return "Unnamed"

    # Keep letters, numbers, spaces, underscores, and dashes only
    cleaned = re.sub(r'[^A-Za-z0-9\s_-]', '', name)

    # Collapse extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Ensure not empty
    return cleaned or "Unnamed"

#### END of Helpers ####

#### WAHA Sessions ####
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

        doc = frappe.get_doc("WAHA Session", name) \
              if frappe.db.exists("WAHA Session", name) \
              else frappe.new_doc("WAHA Session")

        doc.name = name
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

    doc = frappe.get_doc("WAHA Session", docname)
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
def sync_whatsapp_groups(docname: str):
    """Fetch WhatsApp groups via WAHA, sync into WAHA Session child table, and auto-sync with Contact records"""
    client = WahaClient()
    session = frappe.get_doc("WAHA Session", docname)

    groups = client.get_groups(session.name)

    existing = {g.jid: g for g in session.groups}
    seen = set()

    # --- Phase 1: Sync child table ---
    for g in groups:
        jid = g.get("JID")
        name = g.get("Name")
        if not jid:
            continue

        seen.add(jid)

        if jid in existing:
            row = existing[jid]
            if row.name1 != name:
                row.name1 = name
                frappe.logger().info(f"Updated group row: {jid} -> {name}")
        else:
            session.append("groups", {"jid": jid, "name1": name})
            frappe.logger().info(f"Added new group row: {jid} -> {name}")

    # remove groups not present
    for row in list(session.groups):
        if row.jid not in seen:
            frappe.logger().info(f"Removing group row: {row.jid}")
            session.remove(row)

    # save JSON + child rows first
    session.group_info_json = frappe.as_json(groups, indent=2)
    session.save(ignore_permissions=True)
    frappe.db.commit()

    # --- Phase 2: Sync with Contact ---
    for g in groups:
        jid = g.get("JID")
        name = g.get("Name")
        if not jid:
            continue

        sanitized_name = sanitize_contact_name(name) or "Group"

        # ensure uniqueness of first_name
        base_name = sanitized_name
        while frappe.db.exists("Contact", {"first_name": sanitized_name}):
            suffix = jid.split("@")[0][-4:]
            sanitized_name = f"{base_name}_{suffix}"

        # check if contact already exists
        contact_docname = frappe.db.exists("Contact", {"wag_id": jid})
        if contact_docname:
            contact = frappe.get_doc("Contact", contact_docname)
            if contact.first_name != sanitized_name:
                contact.first_name = sanitized_name
                contact.save(ignore_permissions=True)
        else:
            contact = frappe.new_doc("Contact")
            contact.first_name = sanitized_name
            contact.wag_id = jid
            contact.wa_address = jid
            contact.insert(ignore_permissions=True)
            frappe.logger().info(f"Created contact for {jid}: {sanitized_name}")

        # --- Link child row to Contact ---
        row = next((r for r in session.groups if r.jid == jid), None)
        if row and not row.contact:
            row.contact = contact.name

    # save again after linking contacts
    session.save(ignore_permissions=True)
    frappe.db.commit()

    return {"synced": len(groups)}


@frappe.whitelist()
def get_waha_qr(docname):
    """Return WAHA QR code if session not logged in"""
    session = frappe.get_doc("WAHA Session", docname)

    # Call WAHA API to check status
    base_url = session.base_url  # assuming you stored this
    try:
        resp = requests.get(f"{base_url}/api/sessions/{session.session_id}")
        data = resp.json()
    except Exception as e:
        frappe.throw(f"Failed to connect to WAHA: {e}")

    if not data.get("is_logged_in"):
        # Get QR code
        qr_resp = requests.get(f"{base_url}/api/sessions/{session.session_id}/qr")
        qr_data = qr_resp.json().get("qr")
        return {"logged_in": False, "qr": qr_data}

    return {"logged_in": True}

def update_sched_msg_enable_flag(doc, method=None):
    """Update enable_scheduled_message in Scheduled WhatsApp Message when WAHA Session is updated"""
    frappe.logger().info(f"Updating Scheduled Messages for WAHA Session {doc.name}")

    # propagate to all linked Scheduled WhatsApp Messages
    sched_msgs = frappe.get_all("Scheduled WhatsApp Message", filters={"waha_session": doc.name})
    for sm in sched_msgs:
        frappe.db.set_value(
            "Scheduled WhatsApp Message",
            sm.name,
            "enable_scheduled_message",
            doc.enable_scheduled_message or 0
        )
    frappe.db.commit()

#### Scheduled WhatsApp Messages #### 
@frappe.whitelist()
def send_scheduled_message_now(docname: str):
    """Manually send a Scheduled WhatsApp Message"""
    doc = frappe.get_doc("Scheduled WhatsApp Message", docname)
    client = WahaClient()

    if not doc.contact:
        frappe.throw("No contacts found to send message")

    delay_start = doc.random_delay_start or 0
    delay_to = doc.random_delay_to or 0

    for row in doc.contact:
        contact = frappe.get_doc("Contact", row.contact)
        if not contact.wa_address:
            frappe.throw(f"Contact {contact.name} has no WA Address")

        try:
            client.send_text(
                chat_id=contact.wa_address,
                text=doc.message,
                session=doc.waha_session or client.default_session
            )
            # log communication
            chat_id=contact.first_name
            comm = frappe.new_doc("Communication")
            comm.communication_medium = "Chat"
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

            # random delay
            if delay_start or delay_to:
                wait_time = random.randint(delay_start, delay_to)
                time.sleep(wait_time)

        except Exception as e:
            doc.status = "Failed"
            doc.save(ignore_permissions=True)
            frappe.throw(f"❌ Failed to send to {chat_id}: {e}")

    doc.status = "Sent"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "success", "doc": doc.name}



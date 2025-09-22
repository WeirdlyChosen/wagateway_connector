import frappe
import re
import random
import string

def random_uid(length=8):
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_contact_custom_fields():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    custom_fields = {
        "Contact": [
            {
                "fieldname": "wag_id",
                "label": "WhatsApp Group JID",
                "fieldtype": "Data",
                "read_only": 1,
                "hidden": 1
            },
            {
                "fieldname": "wa_address",
                "label": "WhatsApp Address",
                "fieldtype": "Data",
                "read_only": 1,
                "hidden": 1
            },
            {
                "fieldname": "birthday",
                "fieldtype": "Date",
                "label": "Birthday",
                "read_only": 0,
                "hidden": 0,
                "insert_after": "address",
            },
            {
                "fieldname": "uid",
                "fieldtype": "Data",
                "label": "UID",
                "read_only": 1,
                "hidden": 1,
                "unique": 1,
            },
        ]
    }

    create_custom_fields(custom_fields)

def update_wa_address(doc, method=None):
    """Auto-fill wa_address based on wag_id or mobile_no"""
    # Case 1: WhatsApp group JID
    if getattr(doc, "wag_id", None):
        doc.wa_address = doc.wag_id

    # Case 2: Normal mobile number
    elif doc.mobile_no:
        # 🔹 Keep only digits
        wa_number = re.sub(r"\D", "", doc.mobile_no)

        # 🔹 If starts with '0', replace with '62'
        if wa_number.startswith("0"):
            wa_number = "62" + wa_number[1:]

        doc.wa_address = f"{wa_number}@c.us" if wa_number else None

    else:
        doc.wa_address = None
    

def ensure_uid(doc, method=None):
    if not doc.uid:
        doc.uid = random_uid()

def update_number(doc, method=None):
    """Auto-fill number from linked Contact's wa_address"""
    if doc.contact:
        contact = frappe.get_doc("Contact", doc.contact)
        if contact.wa_address:
            # strip @c.us / @g.us
            doc.number = contact.wa_address.split("@")[0]
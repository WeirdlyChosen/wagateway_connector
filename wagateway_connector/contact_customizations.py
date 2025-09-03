import frappe
import re

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
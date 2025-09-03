import frappe

# Add Whatsapp fields for Contacts
def execute():
    contact = frappe.get_doc("DocType", "Contact")

    def ensure_field(field):
        if not any(f.fieldname == field["fieldname"] for f in contact.fields):
            contact.append("fields", field)
            frappe.msgprint(f"Added field {field['fieldname']} to Contact")

    fields = [
        {"fieldname": "wag_id", "fieldtype": "Data", "label": "WhatsApp Group JID", "read_only": 1, "hidden": 1},
        {"fieldname": "wa_address", "fieldtype": "Data", "label": "WhatsApp Address", "read_only": 1, "hidden": 1},
    ]
    for f in fields:
        ensure_field(f)

    contact.save()
    frappe.db.commit()

# Change Permission level for sync with google contact to prevent other syncing contacts from google contacts
def execute():
    # Ensure the field exists first
    field = frappe.db.get_value(
        "Custom Field",
        {"dt": "Contact", "fieldname": "sync_with_google_contacts"},
        ["name"],
    )

    if field:
        frappe.db.set_value("Custom Field", field, "permlevel", 2)
        frappe.db.commit()
        frappe.msgprint("Updated Contact.sync_with_google_contacts to permission level 2")
    else:
        # In case it's not a Custom Field but a core DocField
        docfield = frappe.db.get_value(
            "DocField",
            {"parent": "Contact", "fieldname": "sync_with_google_contacts"},
            ["name"],
        )
        if docfield:
            frappe.db.set_value("DocField", docfield, "permlevel", 2)
            frappe.db.commit()
            frappe.msgprint("Updated core Contact.sync_with_google_contacts to permission level 2")
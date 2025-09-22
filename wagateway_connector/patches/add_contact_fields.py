import frappe

def execute():
    # ------------------------------------
    # 1. Add Custom Fields
    # ------------------------------------
    fields = [
        {
            "fieldname": "wag_id",
            "fieldtype": "Data",
            "label": "WhatsApp Group JID",
            "read_only": 1,
            "hidden": 1,
        },
        {
            "fieldname": "wa_address",
            "fieldtype": "Data",
            "label": "WhatsApp Address",
            "read_only": 1,
            "hidden": 1,
        },
        {
            "fieldname": "birthday",
            "fieldtype": "Date",
            "label": "Birthday",
            "read_only": 1,
            "hidden": 1,
        },
        {
            "fieldname": "uid",
            "fieldtype": "Data",
            "label": "UID",
            "default": random_uid(),  # default value at field definition
            "reqd": 0,
            "unique": 1,
            "read_only": 1,
            "no_copy": 1,
            "hidden": 1,
        },
    ]

    for field in fields:
        if not frappe.db.exists("Custom Field", {"dt": "Contact", "fieldname": field["fieldname"]}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Contact",
                **field
            }).insert(ignore_permissions=True)

    frappe.clear_cache(doctype="Contact")

    # ------------------------------------
    # 2. Update permlevel for sync_with_google_contacts
    # ------------------------------------
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

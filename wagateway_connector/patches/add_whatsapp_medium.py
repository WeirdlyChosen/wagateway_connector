import frappe

def execute():
    """Add WhatsApp as a Communication Medium if not exists"""
    df = frappe.db.get_value(
        "DocField",
        {"parent": "Communication", "fieldname": "communication_medium"},
        ["options"]
    )
    if df and "WhatsApp" not in df:
        options = df + "\nWhatsApp"
        frappe.db.set_value(
            "DocField",
            {"parent": "Communication", "fieldname": "communication_medium"},
            "options",
            options
        )
        frappe.clear_cache(doctype="Communication")
        frappe.logger().info("✅ Added WhatsApp as Communication Medium")

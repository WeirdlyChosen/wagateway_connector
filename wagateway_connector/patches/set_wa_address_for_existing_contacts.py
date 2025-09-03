import frappe
from wagateway_connector.contact_customizations import update_wa_address

def execute():
    for c in frappe.get_all("Contact", fields=["name"]):
        doc = frappe.get_doc("Contact", c.name)
        update_wa_address(doc)
        doc.save(ignore_permissions=True)
    frappe.db.commit()

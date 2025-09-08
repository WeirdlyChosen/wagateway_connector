frappe.ui.form.on('Scheduled Whatsapp Message Contact', {
    contact: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.contact) {
            frappe.db.get_doc('Contact', row.contact).then(contact => {
                if (contact.wa_address) {
                    row.number = contact.wa_address.split('@')[0];
                    frm.refresh_field('contacts');
                }
            });
        }
    }
});

// Copyright (c) 2025, HomeAutomator.id and contributors
// For license information, please see license.txt

// frappe.ui.form.on("WhatsApp Server", {
// 	refresh(frm) {
frappe.ui.form.on('WhatsApp Server', {
    refresh: function(frm) {
        frm.add_custom_button('Test Connection', function() {
            frappe.call({
                method: 'wagateway_connector.api.test_wa_connection',
                callback: function(r) {
                    frappe.msgprint(r.message);
                }
            });
        });
    }
});
// 	},
// });

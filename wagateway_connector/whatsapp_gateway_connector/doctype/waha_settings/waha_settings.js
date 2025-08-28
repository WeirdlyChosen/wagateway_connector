// Copyright (c) 2025, HomeAutomator.id and contributors
// For license information, please see license.txt

// frappe.ui.form.on("WAHA Settings", {
// 	refresh(frm) {
frappe.ui.form.on('WAHA Settings', {
    refresh: function(frm) {
        frm.add_custom_button('Test Connection', function() {
            frappe.call({
                method: 'wagateway_connector.api.test_connection',
                callback: function(r) {
                    frappe.msgprint(r.message);
                }
            });
        });
    }
});
// 	},
// });

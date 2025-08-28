// Copyright (c) 2025, HomeAutomator.id and contributors
// For license information, please see license.txt

// frappe.ui.form.on("WAHA Session", {
// 	refresh(frm) {
frappe.ui.form.on('WAHA Session', {
    onload: function(frm) {
        if (!frm.is_new()) {
            frappe.call({
                method: "wagateway_connector.api.refresh_waha_session",
                args: { docname: frm.doc.name },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __("Session refreshed: " + r.message.status),
                            indicator: 'green'
                        });
                        
                    }
                }
            });
        }
    },

    refresh: function(frm) {
        frm.add_custom_button(__('Test Session'), function() {
            frappe.call({
                method: "wagateway_connector.api.test_waha_session",
                args: {
                    docname: frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__('✅ Session Status: ' + r.message.status));
                    }
                }
            });
        }, __("Actions"));
    }
});
// 	},
// });

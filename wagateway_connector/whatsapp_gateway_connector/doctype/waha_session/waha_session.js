// Copyright (c) 2025, HomeAutomator.id and contributors
// For license information, please see license.txt

// frappe.ui.form.on("WAHA Session", {
// 	refresh(frm) {
frappe.ui.form.on('WAHA Session', {
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
        // 🔹 Sync Groups button
        frm.add_custom_button(__('Sync Groups'), function() {
            frappe.call({
                method: "wagateway_connector.api.sync_whatsapp_groups",
                args: { docname: frm.doc.name },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __("Synced " + r.message.synced + " groups"),
                            indicator: "green"
                        });
                        frm.reload_doc(); // refresh child table
                    }
                }
            });
        }, __("Actions"));
    }
});
// 	},
// });

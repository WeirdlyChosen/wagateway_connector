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
                // 🔹 Show QR button
        frm.add_custom_button(__('Show QR'), function() {
            frappe.call({
                method: "wagateway_connector.api.get_qr_code",
                args: { docname: frm.doc.name },
                callback: function(r) {
                    if (r.message && r.message.qr) {
                        let d = new frappe.ui.Dialog({
                            title: __("Scan WhatsApp QR"),
                            fields: [{
                                fieldtype: "HTML",
                                fieldname: "qr_html",
                                options: `<div style="text-align:center">
                                    <img src="data:image/png;base64,${r.message.qr}" style="max-width:300px"/>
                                    <p>${__("Scan this QR in WhatsApp App")}</p>
                                </div>`
                            }]
                        });
                        d.show();
                    } else {
                        frappe.msgprint(__('⚠ No QR available (maybe already logged in).'));
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

        // ✅ Stop Session / Logout
        frm.add_custom_button(__('Stop Session'), function() {
            frappe.call({
                method: "wagateway_connector.api.stop_waha_session",
                args: { docname: frm.doc.name },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__('🛑 Session stopped: ' + r.message.status));
                        frm.reload_doc();
                    }
                }
            });
        }, __("Actions"));
    }
});
// 	},
// });

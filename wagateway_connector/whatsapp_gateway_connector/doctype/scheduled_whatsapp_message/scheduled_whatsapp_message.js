// Copyright (c) 2025, HomeAutomator.id and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Scheduled WhatsApp Message", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Scheduled WhatsApp Message', {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.disabled == 0) {
            frm.add_custom_button(__('Send Now'), function() {
                frappe.call({
                    method: "wagateway_connector.api.send_scheduled_message_now",
                    args: { docname: frm.doc.name },
                    callback: function(r) {
                        if (r.message) {
                            frm.set_value("status", r.message.status);
                            frm.refresh_field("status");
                            frappe.show_alert({
                            message: __("Message " + r.message.status),
                            indicator: (["Sent", "success", "Success"].includes(r.message.status) ? "green" : "red")
                            });
                        }
                    }
                });
            });
        }
    }
});

frappe.ui.form.on("Scheduled WhatsApp Message", {
    waha_session: function(frm) {
        if (frm.doc.waha_session) {
            frappe.db.get_value("WAHA Session", frm.doc.waha_session, "enable_scheduled_message")
                .then(r => {
                    if (r && r.message) {
                        frm.set_value("enable_scheduled_message", r.message.enable_scheduled_message);
                    }
                });
        } else {
            frm.set_value("enable_scheduled_message", 0);
        }
    }
});

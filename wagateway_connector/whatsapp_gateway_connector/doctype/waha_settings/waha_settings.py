# Copyright (c) 2025, HomeAutomator.id and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from wagateway_connector.waha_client import WahaClient

class WahaSettings(Document):
    def onload(self):
        # add custom button in form UI
        self.set_onload('custom_buttons', [
            {"label": "Test Connection", "method": "wagateway_connector.api.test_connection"}
        ])

import frappe
import requests
class WahaClient:
    def __init__(self, base_url=None, api_key=None, default_session=None):
        # Highest priority → arguments passed from WhatsApp Server DocType
        if base_url and api_key:
            self.base_url = base_url.rstrip("/")
            self.api_key = api_key
            self.default_session = default_session or "default"

        else:
            # Fallback to WAHA Settings DocType
            settings = frappe.get_doc("WAHA Settings")

            self.base_url = (
                settings.base_url.rstrip("/")
                if settings.base_url else None
            )
            self.api_key = settings.get_password("api_key")
            self.default_session = settings.default_session or "default"

        # Final validation
        if not self.base_url:
            frappe.throw("WAHA Base URL is missing.")
        
        if not self.api_key:
            frappe.throw("WAHA API Key is missing.")

        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _url(self, path: str):
        return f"{self.base_url}{path}"

    def get_sessions(self):
        r = requests.get(self._url("/api/sessions"), headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def get_groups(self, session: str):
        url = f"{self.base_url}/api/{session}/groups"
        resp = requests.get(url, headers=self.headers, timeout=15)
        resp.raise_for_status()
        return resp.json() or []

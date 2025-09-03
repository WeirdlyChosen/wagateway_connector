import frappe
import requests

class WahaClient:
    def __init__(self):
        # Load settings from WAHA Settings (Single DocType)
        settings = frappe.get_doc("WAHA Settings")
        self.base_url = settings.base_url.rstrip("/") if settings.base_url else None
        self.api_key = settings.get_password("api_key")
        self.default_session = settings.default_session or "default"

        if not self.base_url or not self.api_key:
            frappe.throw("WAHA Base URL and X-Api-Key must be set in WAHA Settings")

        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _url(self, path: str):
        return f"{self.base_url}{path}"

    def get_sessions(self):
        """GET /api/sessions - List all sessions"""
        r = requests.get(self._url("/api/sessions"), headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def send_text(self, chat_id: str, text: str, session: str = None):
        """POST /api/sendText - Send a text message"""
        payload = {
            "chatId": chat_id,
            "text": text,
            "session": session or self.default_session,
        }
        r = requests.post(self._url("/api/sendText"), headers=self.headers, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()

    def send_file_url(self, chat_id: str, file_url: str, caption: str = None, session: str = None):
        """POST /api/sendFile - Send file via URL"""
        payload = {
            "chatId": chat_id,
            "fileUrl": file_url,
            "caption": caption or "",
            "session": session or self.default_session,
        }
        r = requests.post(self._url("/api/sendFile"), headers=self.headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def send_file_data(self, chat_id: str, filename: str, filedata_base64: str, caption: str = None, session: str = None):
        """POST /api/sendFile - Send file via Base64 data"""
        payload = {
            "chatId": chat_id,
            "fileName": filename,
            "fileData": filedata_base64,
            "caption": caption or "",
            "session": session or self.default_session,
        }
        r = requests.post(self._url("/api/sendFile"), headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def get_groups(self, session: str):
        """Fetch WhatsApp groups from WAHA"""
        url = f"{self.base_url}/api/{session}/groups"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json() or []
import os
from typing import Any

import httpx


class ApiClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("SADANGU_API_URL", "http://127.0.0.1:8000").rstrip("/")
        self.timeout = 12.0
        self.token: str | None = None

    def _request(self, method: str, path: str, **kwargs) -> Any:
        headers = dict(kwargs.pop("headers", {}) or {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.request(method, path, headers=headers, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()

    def login(self, phone: str, pin: str):
        data = self._request("POST", "/api/auth/login", json={"phone": phone, "pin": pin})
        self.token = data["access_token"]
        return data

    def logout(self):
        self.token = None

    def dashboard(self):
        return self._request("GET", "/api/dashboard")

    def ceremonies(self):
        return self._request("GET", "/api/ceremonies")

    def pooja_items(self, ceremony_id: str):
        return self._request("GET", f"/api/ceremonies/{ceremony_id}/pooja-items")

    def bookings(self):
        return self._request("GET", "/api/bookings")

    def create_booking(self, payload: dict):
        return self._request("POST", "/api/bookings", json=payload)

    def update_booking(self, booking_id: str, payload: dict):
        return self._request("PUT", f"/api/bookings/{booking_id}", json=payload)

    def update_booking_status(self, booking_id: str, status: str):
        return self._request("PATCH", f"/api/bookings/{booking_id}/status", json={"status": status})

    def customers(self):
        return self._request("GET", "/api/customers")

    def create_customer(self, payload: dict):
        return self._request("POST", "/api/customers", json=payload)

    def update_customer(self, customer_id: str, payload: dict):
        return self._request("PUT", f"/api/customers/{customer_id}", json=payload)

    def payments(self):
        return self._request("GET", "/api/payments")

    def create_payment(self, payload: dict):
        return self._request("POST", "/api/payments", json=payload)

    def reminders(self):
        return self._request("GET", "/api/reminders")

import os
from datetime import date, timedelta
from pathlib import Path

TEST_DB = Path(__file__).parent / "test_runtime.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["APP_ENV"] = "test"
os.environ["AUTH_REQUIRED"] = "true"
os.environ["ADMIN_PHONE"] = "9000000000"
os.environ["ADMIN_PIN"] = "9876"
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-hmac-signing"
os.environ["AUTO_CREATE_SCHEMA"] = "true"
os.environ["SEED_DEMO_DATA"] = "true"

from fastapi.testclient import TestClient
from app.main import app


def auth_headers(client: TestClient):
    response = client.post("/api/auth/login", json={"phone": "9000000000", "pin": "9876"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_and_authentication():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        assert client.get("/api/dashboard").status_code == 401
        assert client.post("/api/auth/login", json={"phone": "9000000000", "pin": "0000"}).status_code == 401
        headers = auth_headers(client)
        assert client.get("/api/dashboard", headers=headers).status_code == 200


def test_core_booking_and_payment_flow():
    with TestClient(app) as client:
        headers = auth_headers(client)
        ceremonies = client.get("/api/ceremonies", headers=headers)
        assert ceremonies.status_code == 200
        rows = ceremonies.json()
        assert len(rows) >= 6
        ceremony_id = rows[0]["id"]

        event_date = (date.today() + timedelta(days=30)).isoformat()
        payload = {
            "customer_name": "Test Family",
            "mobile_number": "9000000001",
            "ceremony_id": ceremony_id,
            "event_date": event_date,
            "start_time": "10:00:00",
            "end_time": "12:00:00",
            "location": "Chennai",
            "total_amount": "5000",
            "advance_amount": "1000",
        }
        created = client.post("/api/bookings", json=payload, headers=headers)
        assert created.status_code == 201, created.text
        booking = created.json()
        assert float(booking["paid_amount"]) == 1000
        assert float(booking["balance_amount"]) == 4000

        duplicate = client.post(
            "/api/bookings",
            json={**payload, "mobile_number": "9000000002", "customer_name": "Conflict Family"},
            headers=headers,
        )
        assert duplicate.status_code == 409

        invalid_advance = client.post(
            "/api/bookings",
            json={**payload, "event_date": (date.today() + timedelta(days=31)).isoformat(), "advance_amount": "6000"},
            headers=headers,
        )
        assert invalid_advance.status_code == 422

        overpay = client.post(
            "/api/payments",
            json={"booking_id": booking["id"], "amount": "4001", "method": "UPI"},
            headers=headers,
        )
        assert overpay.status_code == 422

        payment = client.post(
            "/api/payments",
            json={"booking_id": booking["id"], "amount": "4000", "method": "UPI"},
            headers=headers,
        )
        assert payment.status_code == 201

        bookings = client.get("/api/bookings", headers=headers)
        refreshed = next(x for x in bookings.json() if x["id"] == booking["id"])
        assert float(refreshed["balance_amount"]) == 0
        assert refreshed["payment_status"] == "PAID"


def test_customer_and_booking_updates():
    with TestClient(app) as client:
        headers = auth_headers(client)
        ceremony_id = client.get('/api/ceremonies', headers=headers).json()[0]['id']
        created = client.post(
            '/api/bookings',
            headers=headers,
            json={
                'customer_name': 'Update Family',
                'mobile_number': '9000000010',
                'ceremony_id': ceremony_id,
                'event_date': (date.today() + timedelta(days=60)).isoformat(),
                'start_time': '06:00:00',
                'end_time': '08:00:00',
                'location': 'Chennai',
                'total_amount': '3000',
                'advance_amount': '500',
            },
        )
        assert created.status_code == 201, created.text
        booking = created.json()

        customer = client.put(
            f"/api/customers/{booking['customer_id']}",
            headers=headers,
            json={'gotram': 'Bharadwaja', 'rasi': 'Mesham', 'nakshatram': 'Ashwini'},
        )
        assert customer.status_code == 200, customer.text
        assert customer.json()['gotram'] == 'Bharadwaja'

        moved = client.put(
            f"/api/bookings/{booking['id']}",
            headers=headers,
            json={'start_time': '07:00:00', 'end_time': '09:00:00', 'location': 'Mylapore'},
        )
        assert moved.status_code == 200, moved.text
        assert moved.json()['location'] == 'Mylapore'

        cancelled = client.patch(
            f"/api/bookings/{booking['id']}/status",
            headers=headers,
            json={'status': 'CANCELLED'},
        )
        assert cancelled.status_code == 200, cancelled.text
        assert cancelled.json()['status'] == 'CANCELLED'

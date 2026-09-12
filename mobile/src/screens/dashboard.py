from __future__ import annotations

from datetime import date

import flet as ft

from theme import CREAM_DARK, DEEP_MAROON, GOLD, INK, MAROON, MUTED, WHITE
from ui import empty_state, money, page_heading, surface


def _action(app, icon, label: str, target: str) -> ft.Container:
    return ft.Container(
        expand=True,
        bgcolor=WHITE,
        border=ft.Border.all(1, CREAM_DARK),
        border_radius=16,
        padding=11,
        ink=True,
        on_click=lambda _: app.show_screen(target),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[ft.Icon(icon, color=MAROON, size=25), ft.Text(label, size=11, color=INK, weight=ft.FontWeight.W_600)],
        ),
    )


def _stat(value, label: str, icon, bgcolor: str) -> ft.Container:
    return ft.Container(
        expand=True,
        bgcolor=bgcolor,
        border_radius=18,
        padding=12,
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Icon(icon, color=MAROON, size=21),
                ft.Text(str(value), size=21, weight=ft.FontWeight.W_700, color=DEEP_MAROON),
                ft.Text(label, size=10, color=MUTED),
            ],
        ),
    )


def dashboard_screen(app) -> ft.Control:
    try:
        data = app.api.dashboard()
    except Exception as exc:
        app.api_error(exc)
        data = {"today_bookings": 0, "upcoming_bookings": 0, "pending_amount": 0, "next_booking": None}

    next_booking = data.get("next_booking")
    controls: list[ft.Control] = [
        page_heading("வணக்கம், ஐயா", date.today().strftime("%d %b %Y")),
        ft.Row(
            spacing=10,
            controls=[
                _stat(data.get("today_bookings", 0), "இன்றைய சடங்குகள்", ft.Icons.EVENT_AVAILABLE_ROUNDED, "#FFF0E1"),
                _stat(data.get("upcoming_bookings", 0), "வரவிருப்பவை", ft.Icons.UPCOMING_ROUNDED, "#F5EFFF"),
            ],
        ),
        surface(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=2, controls=[ft.Text("நிலுவை தொகை", size=11, color=MUTED), ft.Text(money(data.get("pending_amount", 0)), size=24, weight=ft.FontWeight.W_700, color=MAROON)]),
                    ft.Container(width=50, height=50, border_radius=16, bgcolor="#FFF1D6", alignment=ft.Alignment.CENTER, content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, color=GOLD)),
                ],
            ),
            bgcolor="#FFF9F0",
        ),
        ft.Text("விரைவு செயல்கள்", size=13, weight=ft.FontWeight.W_600, color=DEEP_MAROON),
        ft.Row(spacing=10, controls=[_action(app, ft.Icons.ADD_CIRCLE_OUTLINE, "புதிய பதிவு", "new-booking"), _action(app, ft.Icons.PEOPLE_OUTLINE, "வாடிக்கையாளர்", "customers")]),
        ft.Row(spacing=10, controls=[_action(app, ft.Icons.CHECKLIST_ROUNDED, "பூஜை பட்டியல்", "pooja"), _action(app, ft.Icons.CURRENCY_RUPEE_ROUNDED, "கட்டணங்கள்", "payments")]),
    ]

    if next_booking:
        controls.extend(
            [
                ft.Text("அடுத்த நிகழ்ச்சி", size=13, weight=ft.FontWeight.W_600, color=DEEP_MAROON),
                surface(
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(next_booking.get("ceremony_tamil", ""), size=17, weight=ft.FontWeight.W_700, color=MAROON),
                                    ft.Text(str(next_booking.get("start_time", ""))[:5], size=12, weight=ft.FontWeight.W_600, color=GOLD),
                                ],
                            ),
                            ft.Text(next_booking.get("customer_name", ""), color=INK, weight=ft.FontWeight.W_600),
                            ft.Text(next_booking.get("event_date", ""), size=11, color=MUTED),
                            ft.Row(spacing=5, controls=[ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=15, color=GOLD), ft.Text(next_booking.get("location") or "", size=11, color=MUTED, expand=True)]),
                        ],
                    )
                ),
            ]
        )
    else:
        controls.append(empty_state(ft.Icons.EVENT_AVAILABLE_OUTLINED, "பதிவுகள் இல்லை", "புதிய சடங்கு பதிவைச் சேர்க்கவும்"))

    return ft.Column(controls=controls, spacing=12, scroll=ft.ScrollMode.AUTO)

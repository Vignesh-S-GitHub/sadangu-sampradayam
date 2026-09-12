from __future__ import annotations

import flet as ft

from theme import GOLD, INK, MAROON, MUTED
from ui import page_heading, surface


def _menu(app, icon, title: str, subtitle: str, target: str):
    return surface(
        ft.Row(
            controls=[
                ft.Container(width=44, height=44, border_radius=14, bgcolor="#FFF1D6", alignment=ft.Alignment.CENTER, content=ft.Icon(icon, color=MAROON)),
                ft.Column(expand=True, spacing=2, controls=[ft.Text(title, weight=ft.FontWeight.W_700, color=INK), ft.Text(subtitle, size=10, color=MUTED)]),
                ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color=GOLD),
            ],
        ),
        padding=12,
    )


def more_screen(app) -> ft.Control:
    pooja = _menu(app, ft.Icons.CHECKLIST_ROUNDED, "பூஜை பட்டியல்", "சடங்கு பொருட்கள்", "pooja")
    pooja.on_click = lambda _: app.show_screen("pooja")
    payments = _menu(app, ft.Icons.CURRENCY_RUPEE_ROUNDED, "கட்டணங்கள்", "நிலுவை மற்றும் வரவு", "payments")
    payments.on_click = lambda _: app.show_screen("payments")
    reminders = _menu(app, ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, "நினைவூட்டல்", "அடுத்த நிகழ்ச்சிகள்", "reminders")
    reminders.on_click = lambda _: app.show_screen("reminders")
    logout = surface(ft.Row(controls=[ft.Icon(ft.Icons.LOGOUT_ROUNDED, color=MAROON), ft.Text("வெளியேறு", color=MAROON, weight=ft.FontWeight.W_700)]), padding=14)
    logout.on_click = lambda _: app.logout()
    return ft.Column(
        spacing=11,
        scroll=ft.ScrollMode.AUTO,
        controls=[page_heading("மேலும்", "சடங்கு சம்பிரதாயம்"), pooja, payments, reminders, logout, ft.Text("Sadangu Sampradayam • V1", size=10, color=MUTED, text_align=ft.TextAlign.CENTER)],
    )

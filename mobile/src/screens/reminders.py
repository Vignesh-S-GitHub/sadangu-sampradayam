from __future__ import annotations

import flet as ft

from theme import GOLD, INK, MAROON, MUTED
from ui import empty_state, page_heading, surface


def reminders_screen(app) -> ft.Control:
    try:
        rows = app.api.reminders()
    except Exception as exc:
        app.api_error(exc)
        rows = []

    controls: list[ft.Control] = [page_heading("நினைவூட்டல்கள்", "அடுத்த 7 நாட்களில் உள்ள நிகழ்ச்சிகள்")]
    if not rows:
        controls.append(empty_state(ft.Icons.NOTIFICATIONS_NONE_OUTLINED, "நினைவூட்டல் இல்லை", "அடுத்த ஏழு நாட்களில் சடங்கு இல்லை"))
    for row in rows:
        controls.append(
            surface(
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(width=44, height=44, border_radius=14, bgcolor="#FFF1D6", alignment=ft.Alignment.CENTER, content=ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=GOLD)),
                        ft.Column(expand=True, spacing=3, controls=[ft.Text(row["title"], weight=ft.FontWeight.W_700, color=INK), ft.Text(f'{row["event_date"]} • {row["start_time"]}', size=11, color=MAROON), ft.Text(row.get("location") or "", size=10, color=MUTED)]),
                    ],
                )
            )
        )
    return ft.Column(controls=controls, spacing=11, scroll=ft.ScrollMode.AUTO)

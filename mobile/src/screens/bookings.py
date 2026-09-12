from __future__ import annotations

from datetime import date, timedelta

import flet as ft
import httpx

from theme import CREAM_DARK, GOLD, GREEN, INK, MAROON, MUTED, RED, WHITE
from ui import empty_state, input_field, money, page_heading, primary_button, surface


def _status_color(status: str) -> str:
    return RED if status == "CANCELLED" else GREEN


def bookings_screen(app) -> ft.Control:
    try:
        rows = app.api.bookings()
    except Exception as exc:
        app.api_error(exc)
        rows = []

    async def open_maps(row):
        url = row.get("google_maps_url")
        if not url and row.get("location"):
            from urllib.parse import quote
            url = f"https://www.google.com/maps/search/?api=1&query={quote(row['location'])}"
        await app.open_url(url)

    def cancel_booking(row):
        def confirm(_):
            app.page.pop_dialog()
            try:
                app.api.update_booking_status(row["id"], "CANCELLED")
                app.notify("பதிவு ரத்து செய்யப்பட்டது")
                app.show_screen("bookings")
            except Exception as exc:
                app.api_error(exc)

        app.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("பதிவை ரத்து செய்யவா?"),
                content=ft.Text(f"{row['ceremony_tamil']} - {row['customer_name']}"),
                actions=[
                    ft.TextButton("வேண்டாம்", on_click=lambda _: app.page.pop_dialog()),
                    ft.TextButton("ரத்து செய்", on_click=confirm),
                ],
            )
        )

    controls: list[ft.Control] = [
        page_heading(
            "பதிவுகள்",
            "அனைத்து சடங்கு நேரங்களும்",
            ft.IconButton(icon=ft.Icons.ADD_CIRCLE_ROUNDED, icon_color=MAROON, on_click=lambda _: app.show_screen("new-booking")),
        )
    ]
    if not rows:
        controls.append(empty_state(ft.Icons.CALENDAR_MONTH_OUTLINED, "பதிவுகள் இல்லை", "முதல் சடங்கு பதிவைச் சேர்க்கவும்"))

    for row in rows:
        action_buttons: list[ft.Control] = []
        if row.get("status") != "CANCELLED":
            action_buttons.append(
                ft.OutlinedButton(content="வரைபடம்", icon=ft.Icons.MAP_OUTLINED, on_click=lambda _, r=row: open_maps(r))
            )
            action_buttons.append(
                ft.TextButton(content="ரத்து", icon=ft.Icons.CANCEL_OUTLINED, on_click=lambda _, r=row: cancel_booking(r))
            )
        controls.append(
            surface(
                ft.Column(
                    spacing=7,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(row["ceremony_tamil"], size=17, weight=ft.FontWeight.W_700, color=MAROON),
                                ft.Text(row["status"], size=10, color=_status_color(row["status"]), weight=ft.FontWeight.W_600),
                            ],
                        ),
                        ft.Text(row["customer_name"], weight=ft.FontWeight.W_600, color=INK),
                        ft.Text(f'{row["event_date"]}  •  {str(row["start_time"])[:5]} – {str(row["end_time"])[:5]}', size=12, color=MUTED),
                        ft.Row(spacing=5, controls=[ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=15, color=GOLD), ft.Text(row.get("location") or "", size=11, color=MUTED, expand=True)]),
                        ft.Divider(height=1, color=CREAM_DARK),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f'மொத்தம் {money(row["total_amount"])}', size=11, color=INK),
                                ft.Text(f'நிலுவை {money(row["balance_amount"])}', size=11, color=RED if float(row["balance_amount"]) > 0 else GREEN, weight=ft.FontWeight.W_600),
                            ],
                        ),
                        ft.Row(controls=action_buttons, wrap=True) if action_buttons else ft.Container(height=0),
                    ],
                )
            )
        )
    return ft.Column(controls=controls, spacing=11, scroll=ft.ScrollMode.AUTO)


def new_booking_screen(app) -> ft.Control:
    if not app.ceremonies:
        try:
            app.ceremonies = app.api.ceremonies()
        except Exception as exc:
            app.api_error(exc)

    name = input_field("வாடிக்கையாளர் பெயர் *", icon=ft.Icons.PERSON_OUTLINED)
    phone = input_field("மொபைல் எண் *", icon=ft.Icons.PHONE_OUTLINED, keyboard_type=ft.KeyboardType.PHONE)
    ceremony = ft.Dropdown(
        label="சடங்கு வகை *",
        border_radius=14,
        border_color=CREAM_DARK,
        focused_border_color=GOLD,
        filled=True,
        fill_color=WHITE,
        options=[ft.DropdownOption(key=str(x["id"]), text=x["name_tamil"]) for x in app.ceremonies],
    )
    event_date = input_field("தேதி * (YYYY-MM-DD)", icon=ft.Icons.CALENDAR_TODAY, value=(date.today() + timedelta(days=1)).isoformat())
    start = input_field("தொடக்க நேரம் *", icon=ft.Icons.SCHEDULE, value="06:00")
    end = input_field("முடிவு நேரம் *", icon=ft.Icons.SCHEDULE, value="09:00")
    location = input_field("இடம் *", icon=ft.Icons.LOCATION_ON_OUTLINED, multiline=True, min_lines=2, max_lines=3)
    maps_url = input_field("Google Maps link", icon=ft.Icons.MAP_OUTLINED)
    total = input_field("மொத்த தொகை ₹", value="0", keyboard_type=ft.KeyboardType.NUMBER)
    advance = input_field("முன்பணம் ₹", value="0", keyboard_type=ft.KeyboardType.NUMBER)
    notes = input_field("குறிப்புகள்", icon=ft.Icons.NOTES_ROUNDED, multiline=True, min_lines=2, max_lines=3)

    def save(_):
        required = [name.value, phone.value, ceremony.value, event_date.value, start.value, end.value, location.value]
        if not all(required):
            app.notify("தேவையான விவரங்களை நிரப்பவும்", error=True)
            return
        payload = {
            "customer_name": name.value.strip(),
            "mobile_number": phone.value.strip(),
            "ceremony_id": ceremony.value,
            "event_date": event_date.value.strip(),
            "start_time": start.value.strip() + (":00" if len(start.value.strip()) == 5 else ""),
            "end_time": end.value.strip() + (":00" if len(end.value.strip()) == 5 else ""),
            "location": location.value.strip(),
            "google_maps_url": maps_url.value.strip() or None,
            "total_amount": total.value or "0",
            "advance_amount": advance.value or "0",
            "notes": notes.value.strip() or None,
        }
        try:
            app.api.create_booking(payload)
            app.notify("பதிவு வெற்றிகரமாக சேமிக்கப்பட்டது")
            app.show_screen("bookings")
        except Exception as exc:
            app.api_error(exc, "பதிவு சேமிக்க முடியவில்லை")

    return ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            page_heading("புதிய பதிவு", "ஒரு நிமிடத்தில் சடங்கு பதிவு", ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color=MAROON, on_click=lambda _: app.show_screen("bookings"))),
            name,
            phone,
            ceremony,
            event_date,
            ft.Row(spacing=10, controls=[ft.Container(expand=True, content=start), ft.Container(expand=True, content=end)]),
            location,
            maps_url,
            ft.Row(spacing=10, controls=[ft.Container(expand=True, content=total), ft.Container(expand=True, content=advance)]),
            notes,
            ft.Container(height=2),
            primary_button("பதிவு செய்", save, icon=ft.Icons.SAVE_ROUNDED),
            ft.Container(height=8),
        ],
    )

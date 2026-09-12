from __future__ import annotations

import flet as ft

from theme import CREAM_DARK, GOLD, INK, MAROON, MUTED, WHITE
from ui import empty_state, input_field, page_heading, primary_button, surface


def customers_screen(app) -> ft.Control:
    try:
        rows = app.api.customers()
    except Exception as exc:
        app.api_error(exc)
        rows = []

    def edit_customer(row):
        name = input_field("பெயர்", value=row.get("name") or "")
        phone = input_field("மொபைல் எண்", value=row.get("mobile_number") or "", keyboard_type=ft.KeyboardType.PHONE)
        address = input_field("முகவரி", value=row.get("address") or "", multiline=True, min_lines=2, max_lines=3)
        gotram = input_field("கோத்திரம்", value=row.get("gotram") or "")
        rasi = input_field("ராசி", value=row.get("rasi") or "")
        nakshatram = input_field("நட்சத்திரம்", value=row.get("nakshatram") or "")
        notes = input_field("குறிப்புகள்", value=row.get("notes") or "", multiline=True, min_lines=2, max_lines=3)

        def save(_):
            try:
                app.api.update_customer(
                    row["id"],
                    {
                        "name": name.value.strip(),
                        "mobile_number": phone.value.strip(),
                        "address": address.value.strip() or None,
                        "gotram": gotram.value.strip() or None,
                        "rasi": rasi.value.strip() or None,
                        "nakshatram": nakshatram.value.strip() or None,
                        "notes": notes.value.strip() or None,
                    },
                )
                app.page.pop_dialog()
                app.notify("வாடிக்கையாளர் விவரம் புதுப்பிக்கப்பட்டது")
                app.show_screen("customers")
            except Exception as exc:
                app.api_error(exc, "புதுப்பிக்க முடியவில்லை")

        app.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("வாடிக்கையாளர் திருத்தம்"),
                content=ft.Container(width=360, content=ft.Column(spacing=10, tight=True, scroll=ft.ScrollMode.AUTO, controls=[name, phone, address, gotram, rasi, nakshatram, notes])),
                actions=[ft.TextButton("மூடு", on_click=lambda _: app.page.pop_dialog()), ft.TextButton("சேமி", on_click=save)],
            )
        )

    controls: list[ft.Control] = [
        page_heading(
            "வாடிக்கையாளர்கள்",
            "குடும்ப வரலாறு மற்றும் ஜாதக விவரங்கள்",
            ft.IconButton(icon=ft.Icons.PERSON_ADD_ALT_1_ROUNDED, icon_color=MAROON, on_click=lambda _: app.show_screen("new-customer")),
        )
    ]
    if not rows:
        controls.append(empty_state(ft.Icons.PEOPLE_OUTLINE, "வாடிக்கையாளர்கள் இல்லை", "புதிய வாடிக்கையாளரைச் சேர்க்கவும்"))
    for row in rows:
        astro = " • ".join(x for x in [row.get("gotram"), row.get("rasi"), row.get("nakshatram")] if x)
        controls.append(
            surface(
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.CircleAvatar(bgcolor=MAROON, content=ft.Text((row.get("name") or "?")[:1].upper(), color=WHITE, weight=ft.FontWeight.W_700)),
                        ft.Column(
                            expand=True,
                            spacing=3,
                            controls=[
                                ft.Text(row.get("name") or "", weight=ft.FontWeight.W_700, color=INK),
                                ft.Text(row.get("mobile_number") or "", size=12, color=MUTED),
                                ft.Text(row.get("address") or astro or "", size=11, color=MUTED, max_lines=2),
                            ],
                        ),
                        ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=GOLD, on_click=lambda _, r=row: edit_customer(r)),
                    ],
                )
            )
        )
    return ft.Column(controls=controls, spacing=11, scroll=ft.ScrollMode.AUTO)


def customer_form_screen(app) -> ft.Control:
    name = input_field("பெயர் *", icon=ft.Icons.PERSON_OUTLINED)
    phone = input_field("மொபைல் எண் *", icon=ft.Icons.PHONE_OUTLINED, keyboard_type=ft.KeyboardType.PHONE)
    alt_phone = input_field("மாற்று மொபைல்", icon=ft.Icons.PHONE_ANDROID_OUTLINED, keyboard_type=ft.KeyboardType.PHONE)
    address = input_field("முகவரி", icon=ft.Icons.HOME_OUTLINED, multiline=True, min_lines=2, max_lines=3)
    gotram = input_field("கோத்திரம்")
    rasi = input_field("ராசி")
    nakshatram = input_field("நட்சத்திரம்")
    notes = input_field("குடும்ப குறிப்புகள்", multiline=True, min_lines=2, max_lines=3)

    def save(_):
        if not name.value or not phone.value:
            app.notify("பெயர் மற்றும் மொபைல் எண் தேவை", error=True)
            return
        try:
            app.api.create_customer(
                {
                    "name": name.value.strip(),
                    "mobile_number": phone.value.strip(),
                    "alternate_mobile": alt_phone.value.strip() or None,
                    "address": address.value.strip() or None,
                    "gotram": gotram.value.strip() or None,
                    "rasi": rasi.value.strip() or None,
                    "nakshatram": nakshatram.value.strip() or None,
                    "notes": notes.value.strip() or None,
                }
            )
            app.notify("வாடிக்கையாளர் சேர்க்கப்பட்டார்")
            app.show_screen("customers")
        except Exception as exc:
            app.api_error(exc, "வாடிக்கையாளரை சேர்க்க முடியவில்லை")

    return ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            page_heading("புதிய வாடிக்கையாளர்", "குடும்ப விவரங்களை ஒருமுறை சேமிக்கவும்", ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color=MAROON, on_click=lambda _: app.show_screen("customers"))),
            name, phone, alt_phone, address,
            ft.Row(spacing=10, controls=[ft.Container(expand=True, content=gotram), ft.Container(expand=True, content=rasi)]),
            nakshatram, notes,
            primary_button("சேமி", save, icon=ft.Icons.SAVE_ROUNDED),
            ft.Container(height=8),
        ],
    )

from __future__ import annotations

import flet as ft

from theme import CREAM_DARK, GREEN, INK, MAROON, MUTED, RED, WHITE
from ui import empty_state, input_field, money, page_heading, surface


def payments_screen(app) -> ft.Control:
    try:
        bookings = [x for x in app.api.bookings() if x.get("status") != "CANCELLED"]
    except Exception as exc:
        app.api_error(exc)
        bookings = []

    def add_payment(row):
        balance = float(row.get("balance_amount") or 0)
        amount = input_field("தொகை ₹", value=str(int(balance)) if balance else "0", keyboard_type=ft.KeyboardType.NUMBER)
        method = ft.Dropdown(
            label="முறை",
            value="UPI",
            options=[ft.DropdownOption(key=x, text=x.replace("_", " ")) for x in ["UPI", "CASH", "BANK_TRANSFER", "OTHER"]],
            border_radius=14,
            border_color=CREAM_DARK,
            filled=True,
            fill_color=WHITE,
        )
        notes = input_field("குறிப்பு")

        def save(_):
            try:
                app.api.create_payment({"booking_id": row["id"], "amount": amount.value, "method": method.value, "notes": notes.value.strip() or None})
                app.page.pop_dialog()
                app.notify("கட்டணம் பதிவு செய்யப்பட்டது")
                app.show_screen("payments")
            except Exception as exc:
                app.api_error(exc, "கட்டணத்தை பதிவு செய்ய முடியவில்லை")

        app.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("கட்டணம் பதிவு"),
                content=ft.Container(width=340, content=ft.Column(tight=True, spacing=10, controls=[ft.Text(f'{row["customer_name"]} • {money(balance)} நிலுவை', size=12, color=MUTED), amount, method, notes])),
                actions=[ft.TextButton("மூடு", on_click=lambda _: app.page.pop_dialog()), ft.TextButton("சேமி", on_click=save)],
            )
        )

    controls: list[ft.Control] = [page_heading("கட்டணங்கள்", "முன்பணம் மற்றும் நிலுவை தொகை")]
    pending = [x for x in bookings if float(x.get("balance_amount") or 0) > 0]
    if not pending:
        controls.append(empty_state(ft.Icons.PAYMENTS_OUTLINED, "நிலுவை இல்லை", "அனைத்து பதிவுகளும் செலுத்தப்பட்டுள்ளன"))
    for row in pending:
        controls.append(
            surface(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text(row["customer_name"], weight=ft.FontWeight.W_700, color=INK), ft.Text(money(row["balance_amount"]), color=RED, weight=ft.FontWeight.W_700)]),
                        ft.Text(row["ceremony_tamil"], size=12, color=MAROON),
                        ft.Text(f'மொத்தம் {money(row["total_amount"])} • பெற்றது {money(row["paid_amount"])}', size=11, color=MUTED),
                        ft.OutlinedButton(content="கட்டணம் சேர்", icon=ft.Icons.ADD_CARD_ROUNDED, on_click=lambda _, r=row: add_payment(r)),
                    ],
                )
            )
        )
    return ft.Column(controls=controls, spacing=11, scroll=ft.ScrollMode.AUTO)

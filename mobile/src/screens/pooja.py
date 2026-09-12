from __future__ import annotations

from urllib.parse import quote

import flet as ft

from theme import CREAM_DARK, GOLD, MAROON, MUTED, WHITE
from ui import empty_state, page_heading, primary_button, surface


def pooja_screen(app) -> ft.Control:
    if not app.ceremonies:
        try:
            app.ceremonies = app.api.ceremonies()
        except Exception as exc:
            app.api_error(exc)

    if not app.ceremonies:
        return ft.Column(controls=[page_heading("பூஜை பட்டியல்"), empty_state(ft.Icons.CHECKLIST_OUTLINED, "சடங்கு தரவு இல்லை", "சேவையக இணைப்பை சரிபார்க்கவும்")])

    ceremony = ft.Dropdown(
        label="சடங்கு தேர்வு",
        value=str(app.ceremonies[0]["id"]),
        border_radius=14,
        border_color=CREAM_DARK,
        focused_border_color=GOLD,
        filled=True,
        fill_color=WHITE,
        options=[ft.DropdownOption(key=str(x["id"]), text=x["name_tamil"]) for x in app.ceremonies],
    )
    item_box = ft.Column(spacing=2)

    def load_items(_=None):
        try:
            rows = app.api.pooja_items(ceremony.value)
        except Exception as exc:
            app.api_error(exc)
            rows = []
        item_box.controls = [
            ft.Checkbox(
                label=x["name_tamil"] + (f'  •  {x.get("quantity"):g} {x.get("unit") or ""}' if x.get("quantity") is not None else ""),
                value=True,
                active_color=MAROON,
                check_color=WHITE,
            )
            for x in rows
        ]
        app.page.update()

    async def share_whatsapp(_):
        selected = [x.label for x in item_box.controls if getattr(x, "value", False)]
        title = next((x["name_tamil"] for x in app.ceremonies if str(x["id"]) == ceremony.value), "பூஜை")
        message = "வணக்கம் 🙏\n\n" + title + " தேவையான பொருட்கள்:\n\n" + "\n".join(f"• {x}" for x in selected) + "\n\nநன்றி\nசடங்கு சம்பிரதாயம்"
        await app.open_url("https://wa.me/?text=" + quote(message))

    ceremony.on_select = load_items
    load_items()

    return ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            page_heading("பூஜை பட்டியல்", "சடங்குக்கான பொருட்களை உடனே பகிருங்கள்"),
            ceremony,
            surface(item_box),
            primary_button("WhatsApp அனுப்பு", share_whatsapp, icon=ft.Icons.SEND_ROUNDED),
            ft.Text("தேவையற்ற பொருட்களை untick செய்து அனுப்பலாம்.", size=10, color=MUTED, text_align=ft.TextAlign.CENTER),
        ],
    )

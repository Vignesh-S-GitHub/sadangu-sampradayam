from __future__ import annotations

import flet as ft
import httpx

from api_client import ApiClient
from screens.bookings import bookings_screen, new_booking_screen
from screens.customers import customers_screen, customer_form_screen
from screens.dashboard import dashboard_screen
from screens.more import more_screen
from screens.payments import payments_screen
from screens.pooja import pooja_screen
from screens.reminders import reminders_screen
from theme import CARD, CREAM, CREAM_DARK, GOLD, MAROON, MOBILE_MAX_WIDTH, MUTED, WHITE
from ui import input_field, primary_button, tamil_title


class SadanguApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.api = ApiClient()
        self.launcher = ft.UrlLauncher()
        self.ceremonies: list[dict] = []
        self.current_screen = "dashboard"

        page.title = "Sadangu Sampradayam"
        page.bgcolor = "#EFE2C6"
        page.padding = 0
        page.spacing = 0
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(color_scheme_seed=MAROON, use_material3=True)
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.body = ft.Column(expand=True, spacing=0)
        self.root = ft.Container(width=MOBILE_MAX_WIDTH, expand=True, bgcolor=CREAM, content=self.body)
        self.nav = self._navigation_bar()
        self.show_login()

    def _navigation_bar(self) -> ft.NavigationBar:
        return ft.NavigationBar(
            selected_index=0,
            bgcolor=WHITE,
            indicator_color=CREAM_DARK,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="முகப்பு"),
                ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH_OUTLINED, selected_icon=ft.Icons.CALENDAR_MONTH, label="பதிவுகள்"),
                ft.NavigationBarDestination(icon=ft.Icons.PEOPLE_OUTLINED, selected_icon=ft.Icons.PEOPLE, label="வாடிக்கையாளர்"),
                ft.NavigationBarDestination(icon=ft.Icons.MORE_HORIZ, label="மேலும்"),
            ],
            on_change=self._nav_changed,
        )

    def _nav_changed(self, e):
        target = ["dashboard", "bookings", "customers", "more"][e.control.selected_index]
        self.show_screen(target)

    def _header(self) -> ft.Container:
        return ft.Container(
            bgcolor=WHITE,
            padding=ft.Padding.only(left=14, right=8, top=8, bottom=8),
            border=ft.Border(bottom=ft.BorderSide(1, CREAM_DARK)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Image(src="logo_mark.png", width=42, height=42, fit=ft.BoxFit.CONTAIN),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    tamil_title("சடங்கு சம்பிரதாயம்", 15),
                                    ft.Text("Sadangu Sampradayam", size=9, color=GOLD),
                                ],
                            ),
                        ],
                    ),
                    ft.IconButton(icon=ft.Icons.NOTIFICATIONS_NONE_ROUNDED, icon_color=MAROON, on_click=lambda _: self.show_screen("reminders")),
                ],
            ),
        )

    def notify(self, message: str, *, error: bool = False):
        self.page.show_dialog(
            ft.SnackBar(
                ft.Text(message, color=WHITE),
                bgcolor="#B3261E" if error else "#18794E",
                show_close_icon=True,
                close_icon_color=WHITE,
            )
        )

    def api_error(self, exc: Exception, fallback: str = "சேவையக இணைப்பு தோல்வி"):
        if isinstance(exc, httpx.HTTPStatusError):
            try:
                detail = exc.response.json().get("detail", fallback)
                if isinstance(detail, list):
                    detail = detail[0].get("msg", fallback)
                self.notify(str(detail), error=True)
                return
            except Exception:
                pass
        self.notify(fallback, error=True)

    def set_root(self, control: ft.Control):
        self.root.content = control
        self.page.clean()
        self.page.add(self.root)
        self.page.update()

    def show_login(self):
        phone = input_field("மொபைல் எண்", icon=ft.Icons.PHONE_OUTLINED, keyboard_type=ft.KeyboardType.PHONE)
        pin = input_field("PIN", icon=ft.Icons.LOCK_OUTLINED, password=True, keyboard_type=ft.KeyboardType.NUMBER)

        def login(_):
            if not phone.value or not pin.value:
                self.notify("மொபைல் எண் மற்றும் PIN தேவை", error=True)
                return
            try:
                self.api.login(phone.value.strip(), pin.value.strip())
                self.load_shell("dashboard")
            except Exception as exc:
                self.api_error(exc, "மொபைல் எண் அல்லது PIN தவறு")

        hero = ft.Container(
            padding=ft.Padding.only(left=22, right=22, top=26, bottom=12),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Image(src="logo.png", width=255, height=255, fit=ft.BoxFit.CONTAIN),
                    ft.Text("புரோகிதர் சேவை மேலாண்மை", size=13, color="#9F6A10"),
                ],
            ),
        )
        form = ft.Container(
            padding=ft.Padding.only(left=22, right=22, top=8, bottom=28),
            content=ft.Column(
                spacing=13,
                controls=[
                    phone,
                    pin,
                    primary_button("உள்நுழை", login, icon=ft.Icons.LOGIN),
                    ft.Text("குடும்ப பயன்பாட்டிற்கான பாதுகாப்பான நிர்வாக உள்நுழைவு", size=10, color=MUTED, text_align=ft.TextAlign.CENTER),
                ],
            ),
        )
        self.set_root(ft.SafeArea(ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[hero, form])))

    def load_shell(self, target: str):
        try:
            self.ceremonies = self.api.ceremonies()
        except Exception as exc:
            self.api_error(exc)
            self.ceremonies = []
        self.body.controls = [
            self._header(),
            ft.Container(expand=True, padding=16, content=ft.Column(expand=True)),
            self.nav,
        ]
        self.page.clean()
        self.page.add(self.root)
        self.show_screen(target)

    @property
    def content_host(self) -> ft.Container:
        return self.body.controls[1]

    def show_screen(self, name: str, **kwargs):
        self.current_screen = name
        builders = {
            "dashboard": lambda: dashboard_screen(self),
            "bookings": lambda: bookings_screen(self),
            "new-booking": lambda: new_booking_screen(self),
            "customers": lambda: customers_screen(self),
            "new-customer": lambda: customer_form_screen(self),
            "pooja": lambda: pooja_screen(self),
            "payments": lambda: payments_screen(self),
            "reminders": lambda: reminders_screen(self),
            "more": lambda: more_screen(self),
        }
        builder = builders.get(name, builders["dashboard"])
        self.content_host.content = builder()
        nav_indices = {"dashboard": 0, "bookings": 1, "customers": 2, "more": 3}
        if name in nav_indices:
            self.nav.selected_index = nav_indices[name]
        self.page.update()

    async def open_url(self, url: str | None):
        if not url:
            self.notify("இணைப்பு இல்லை", error=True)
            return
        try:
            await self.launcher.launch_url(url, mode=ft.LaunchMode.EXTERNAL_APPLICATION, web_only_window_name="_blank")
        except Exception:
            await self.launcher.launch_url(url, web_only_window_name="_blank")

    def logout(self):
        self.api.logout()
        self.show_login()


def main(page: ft.Page):
    SadanguApp(page)

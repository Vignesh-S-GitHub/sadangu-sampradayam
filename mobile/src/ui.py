from __future__ import annotations

from decimal import Decimal

import flet as ft

from theme import CARD, CARD_RADIUS, CREAM_DARK, DEEP_MAROON, GOLD, INK, MAROON, MUTED, WHITE, CONTROL_RADIUS


def money(value) -> str:
    try:
        return f"₹{Decimal(str(value)):,.0f}"
    except Exception:
        return "₹0"


def tamil_title(text: str, size: int = 18, color: str = DEEP_MAROON) -> ft.Text:
    return ft.Text(text, size=size, weight=ft.FontWeight.W_700, color=color)


def caption(text: str) -> ft.Text:
    return ft.Text(text, size=11, color=MUTED)


def surface(content: ft.Control, *, padding: int = 16, bgcolor: str = CARD) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        padding=padding,
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, CREAM_DARK),
    )


def input_field(
    label: str,
    *,
    value: str | None = None,
    icon=None,
    keyboard_type=None,
    password: bool = False,
    multiline: bool = False,
    min_lines: int | None = None,
    max_lines: int | None = None,
) -> ft.TextField:
    return ft.TextField(
        label=label,
        value=value,
        leading_icon=icon,
        keyboard_type=keyboard_type,
        password=password,
        can_reveal_password=password,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines,
        border_radius=CONTROL_RADIUS,
        border_color=CREAM_DARK,
        focused_border_color=GOLD,
        filled=True,
        fill_color=WHITE,
        color=INK,
        label_style=ft.TextStyle(color=MUTED),
    )


def primary_button(text: str, on_click, *, icon=None, expand: bool = True) -> ft.Container:
    button = ft.FilledButton(
        content=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=MAROON,
            color=WHITE,
            padding=ft.Padding.symmetric(horizontal=20, vertical=15),
            shape=ft.RoundedRectangleBorder(radius=CONTROL_RADIUS),
        ),
    )
    return ft.Container(width=float("inf") if expand else None, content=button)


def outlined_button(text: str, on_click, *, icon=None, expand: bool = True) -> ft.Container:
    button = ft.OutlinedButton(
        content=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=MAROON,
            side=ft.BorderSide(1, GOLD),
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=CONTROL_RADIUS),
        ),
    )
    return ft.Container(width=float("inf") if expand else None, content=button)


def page_heading(title: str, subtitle: str | None = None, action: ft.Control | None = None) -> ft.Row:
    controls: list[ft.Control] = [
        ft.Column(
            expand=True,
            spacing=2,
            controls=[
                tamil_title(title, 20),
                ft.Text(subtitle, size=11, color=MUTED) if subtitle else ft.Container(height=0),
            ],
        )
    ]
    if action:
        controls.append(action)
    return ft.Row(controls=controls, vertical_alignment=ft.CrossAxisAlignment.CENTER)


def empty_state(icon, title: str, subtitle: str) -> ft.Container:
    return surface(
        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(icon, size=38, color=GOLD),
                tamil_title(title, 15),
                ft.Text(subtitle, size=11, color=MUTED, text_align=ft.TextAlign.CENTER),
            ],
        ),
        padding=24,
    )

"""
宠物选择/设置 Screen
"""

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image as KivyImage
import os
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

from pets.pet_data import (
    PETS,
    get_selected_pet, set_selected_pet,
    get_api_key, set_api_key,
    get_pet_visible, set_pet_visible,
)


def _T():
    return MDApp.get_running_app().theme


class PetMenuScreen(Screen):
    """选择/管理健身宠物"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "pet_menu"
        self.dialog = None
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        t = _T()
        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(16), dp(20), dp(16), dp(12)],
        )

        # 标题
        layout.add_widget(MDLabel(
            text="🏋️ 健身宠物",
            font_style="H4", halign="center",
            size_hint_y=None, height=dp(50), bold=True,
            theme_text_color="Custom", text_color=t["primary"],
        ))

        # 当前选择
        current_pet = get_selected_pet()
        if current_pet and current_pet not in PETS:
            current_pet = None
            set_selected_pet(None)
        # 只有一个宠物时自动选中
        if not current_pet and len(PETS) == 1:
            current_pet = list(PETS.keys())[0]
            set_selected_pet(current_pet)
            app = MDApp.get_running_app()
            if hasattr(app, "pet_overlay"):
                app.pet_overlay.reload_pet()
        if PETS:
            status_text = f"当前选择: {PETS.get(current_pet, {}).get('name', '未选择')}"
        else:
            status_text = "暂无可用宠物"
        self.status_label = MDLabel(
            text=status_text,
            font_style="Subtitle2", halign="center",
            size_hint_y=None, height=dp(24),
            theme_text_color="Custom", text_color=t["text_sec"],
        )
        layout.add_widget(self.status_label)

        # 宠物列表（可滚动）
        scroll = ScrollView(size_hint=(1, 1))
        pet_list = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=[dp(4), dp(4)],
        )
        pet_list.bind(minimum_height=pet_list.setter("height"))

        for pid, pdef in PETS.items():
            card = self._make_pet_card(pid, pdef, current_pet == pid)
            pet_list.add_widget(card)

        scroll.add_widget(pet_list)
        layout.add_widget(scroll)

        # API Key 区域
        api_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None, height=dp(80),
            spacing=dp(4), padding=[dp(4), dp(4)],
        )
        api_box.add_widget(MDLabel(
            text="DeepSeek API Key（可选，用于AI聊天）",
            font_style="Caption",
            theme_text_color="Custom", text_color=t["text_sec"],
            size_hint_y=None, height=dp(16),
        ))

        key_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(4))
        saved_key = get_api_key()
        masked = saved_key[:8] + "****" if len(saved_key) > 8 else ""
        self.api_input = MDTextField(
            text=masked if masked else saved_key,
            hint_text="sk-...",
            mode="fill",
            size_hint_x=0.7,
            font_size=dp(12),
            password=True,
        )
        key_row.add_widget(self.api_input)

        save_key_btn = MDRaisedButton(
            text="保存",
            size_hint_x=0.3,
            md_bg_color=t["primary"],
            font_size=dp(12),
            on_release=lambda b: self._save_api_key(),
        )
        key_row.add_widget(save_key_btn)
        api_box.add_widget(key_row)
        layout.add_widget(api_box)

        # 开关：显示宠物
        switch_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(40),
            spacing=dp(8), padding=[dp(8), dp(4)],
        )
        switch_box.add_widget(MDLabel(
            text="显示宠物",
            font_style="Body2", size_hint_x=0.6,
        ))
        visible = get_pet_visible()
        self.toggle_btn = MDRaisedButton(
            text="隐藏宠物" if visible else "显示宠物",
            size_hint_x=0.4,
            md_bg_color=t["primary"] if visible else (0.4, 0.4, 0.4, 0.5),
            font_size=dp(13),
            on_release=lambda b: self._toggle_visible(),
        )
        switch_box.add_widget(self.toggle_btn)
        layout.add_widget(switch_box)

        # 返回
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(8)))
        back_btn = MDFlatButton(
            text="返回主菜单",
            font_size=dp(14), size_hint_y=None, height=dp(36),
            on_release=lambda b: self._go_back(),
        )
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def _make_pet_card(self, pid, pdef, is_selected):
        t = _T()
        color = pdef.get("color", t["primary"])
        selected_border = (1, 1, 1, 1) if is_selected else (0, 0, 0, 0)

        card = MDCard(
            orientation="horizontal",
            size_hint_y=None, height=dp(76),
            padding=[dp(14), dp(10)],
            spacing=dp(12),
            md_bg_color=(*color[:3], 0.15) if not is_selected else (*color[:3], 0.3),
            radius=[dp(8)],
            line_width=dp(2) if is_selected else dp(0.5),
            line_color=selected_border if is_selected else (*color[:3], 0.2),
            ripple_behavior=True,
            on_release=lambda b, p=pid: self._select_pet(p),
        )

        # 宠物形象（static.png）
        pet_dir = pdef.get("dir", pid)
        static_path = os.path.join("assets", "pets", pet_dir, "static.png")
        icon = KivyImage(
            source=static_path if os.path.exists(static_path) else "",
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            allow_stretch=True,
            keep_ratio=True,
        )
        card.add_widget(icon)

        # 信息
        info = MDBoxLayout(orientation="vertical", size_hint_x=0.7)
        info.add_widget(MDLabel(
            text=pdef["name"],
            font_style="Subtitle2", bold=True,
            theme_text_color="Custom", text_color=t["text"],
            size_hint_y=0.5,
        ))
        info.add_widget(MDLabel(
            text=pdef.get("description", ""),
            font_style="Caption",
            theme_text_color="Custom", text_color=t["text_sec"],
            size_hint_y=0.5,
        ))
        card.add_widget(info)

        # 选中标记
        if is_selected:
            check = MDLabel(
                text="✓", font_style="H4",
                size_hint_x=0.15, halign="center",
                theme_text_color="Custom", text_color=color,
            )
            card.add_widget(check)

        return card

    def _select_pet(self, pet_id):
        """选择宠物"""
        set_selected_pet(pet_id)

        # 通知 overlay 重新加载
        app = MDApp.get_running_app()
        if hasattr(app, "pet_overlay"):
            app.pet_overlay.reload_pet()

        # 刷新页面
        self.refresh()

    def refresh(self):
        self.build_ui()

    def _save_api_key(self):
        key = self.api_input.text.strip()
        if key:
            set_api_key(key)
            self.dialog = MDDialog(
                text="API Key 已保存！",
                buttons=[MDFlatButton(text="好的", on_release=lambda b: self.dialog.dismiss())],
            )
            self.dialog.open()
        else:
            set_api_key("")
            self.dialog = MDDialog(
                text="已清除 API Key",
                buttons=[MDFlatButton(text="好的", on_release=lambda b: self.dialog.dismiss())],
            )
            self.dialog.open()

    def _toggle_visible(self):
        current = get_pet_visible()
        new_val = not current
        set_pet_visible(new_val)
        app = MDApp.get_running_app()
        if hasattr(app, "pet_overlay"):
            if new_val:
                app.pet_overlay.show()
            else:
                app.pet_overlay.hide()
        self.refresh()

    def _go_back(self):
        self.manager.current = "menu"

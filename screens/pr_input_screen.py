# PR 数据输入 Screen

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

from core.data import load_pr, save_pr


PR_FIELDS = [
    ("深蹲", "squat"),
    ("卧推", "bench"),
    ("硬拉", "deadlift"),
    ("体重", "bw"),
    ("木板卧推", "木板卧推"),
    ("暂停硬拉", "暂停硬拉"),
    ("前蹲", "前蹲"),
]

# 字段映射到 PR 数据键名
FIELD_KEY = {
    "squat": "深蹲",
    "bench": "卧推",
    "deadlift": "硬拉",
    "bw": "体重",
}


class PRInputScreen(Screen):
    """PR 数据输入页面"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "pr_input"
        self.fields = {}
        self.dialog = None
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(10))

        # 标题
        layout.add_widget(
            MDLabel(
                text="各项目 PR 重量",
                font_style="H4",
                halign="center",
                size_hint_y=None,
                height=dp(60),
                bold=True,
            )
        )
        layout.add_widget(
            MDLabel(
                text="单位：kg",
                font_style="Caption",
                halign="center",
                size_hint_y=None,
                height=dp(20),
                theme_text_color="Hint",
            )
        )

        # PR 数据输入卡片
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(30), dp(15)],
            spacing=dp(8),
            radius=[dp(12)],
            md_bg_color=(0.08, 0.08, 0.15, 0.6),
        )
        card.bind(minimum_height=card.setter("height"))

        pr_data = load_pr()

        for label, key in PR_FIELDS:
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(44),
                spacing=dp(10),
            )

            row.add_widget(
                MDLabel(
                    text=label,
                    font_style="Subtitle2",
                    size_hint_x=0.35,
                    halign="right",
                    valign="middle",
                )
            )

            data_key = FIELD_KEY.get(key, key)
            current_val = str(pr_data.get(data_key, 0))

            text_field = MDTextField(
                text=current_val,
                hint_text="kg",
                mode="rectangle",
                input_filter="int",
                size_hint_x=0.4,
            )
            self.fields[key] = text_field
            row.add_widget(text_field)

            row.add_widget(
                MDLabel(
                    text="kg",
                    font_style="Body2",
                    size_hint_x=0.15,
                    halign="left",
                    valign="middle",
                    theme_text_color="Hint",
                )
            )

            card.add_widget(row)

        layout.add_widget(card)

        # 按钮区域
        btn_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(20),
            padding=[dp(30), dp(5)],
        )

        save_btn = MDRaisedButton(
            text="保存 PR",
            font_size=dp(15),
            md_bg_color=(0.18, 0.42, 0.31, 1),
            size_hint_x=0.4,
            on_release=lambda b: self._save_pr(),
        )
        btn_box.add_widget(save_btn)

        back_btn = MDFlatButton(
            text="返回主菜单",
            font_size=dp(14),
            size_hint_x=0.4,
            on_release=lambda b: self._go_back(),
        )
        btn_box.add_widget(back_btn)

        layout.add_widget(btn_box)
        layout.add_widget(MDBoxLayout())  # 弹性填充
        self.add_widget(layout)

    def _save_pr(self):
        """保存 PR 数据"""
        pr_data = load_pr()
        for key, field in self.fields.items():
            val = field.text.strip()
            if val:
                try:
                    data_key = FIELD_KEY.get(key, key)
                    pr_data[data_key] = float(val)
                except ValueError:
                    self._show_error(f"{key} 请输入有效数字")
                    return

        save_pr(pr_data)
        self._show_success("PR 重量已保存！")

    def _show_error(self, msg):
        self.dialog = MDDialog(
            title="错误",
            text=msg,
            buttons=[
                MDRaisedButton(text="好", on_release=lambda b: self.dialog.dismiss()),
            ],
        )
        self.dialog.open()

    def _show_success(self, msg):
        self.dialog = MDDialog(
            text=msg,
            buttons=[
                MDRaisedButton(
                    text="好",
                    on_release=lambda b: (
                        self.dialog.dismiss()
                    ),
                ),
            ],
        )
        self.dialog.open()

    def _go_back(self):
        self.manager.current = "menu"

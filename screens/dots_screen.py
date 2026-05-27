# DOTS 系数计算 Screen

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

from core.data import load_pr
from core.logic import calc_dots


class DOTSScreen(Screen):
    """DOTS 系数计算页面"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "dots"
        self.fields = {}
        self.dialog = None
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))

        # 标题
        layout.add_widget(
            MDLabel(
                text="DOTS 系数计算",
                font_style="H4",
                halign="center",
                size_hint_y=None,
                height=dp(55),
                bold=True,
            )
        )
        layout.add_widget(
            MDLabel(
                text="DOTS = 总重量 / 系数（基于体重）",
                font_style="Caption",
                halign="center",
                size_hint_y=None,
                height=dp(20),
                theme_text_color="Hint",
            )
        )

        # 输入卡片
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

        dots_fields = [
            ("体重 (kg)", "bw", str(pr_data.get("体重", 93))),
            ("深蹲 (kg)", "squat", str(pr_data.get("深蹲", 230))),
            ("卧推 (kg)", "bench", str(pr_data.get("卧推", 140))),
            ("硬拉 (kg)", "deadlift", str(pr_data.get("硬拉", 190))),
        ]

        for label, key, default_val in dots_fields:
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
                    size_hint_x=0.4,
                    halign="right",
                    valign="middle",
                )
            )

            text_field = MDTextField(
                text=default_val,
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
                    size_hint_x=0.1,
                    halign="left",
                    valign="middle",
                    theme_text_color="Hint",
                )
            )

            card.add_widget(row)

        layout.add_widget(card)

        # 结果显示
        self.result_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=[dp(15), dp(10)],
            radius=[dp(12)],
            md_bg_color=(0.1, 0.25, 0.2, 0.6),
        )
        self.total_label = MDLabel(
            text="三大项总和: -- kg",
            font_style="Subtitle1",
            halign="center",
            size_hint_y=None,
            height=dp(25),
        )
        self.dots_label = MDLabel(
            text="DOTS: --",
            font_style="H3",
            halign="center",
            size_hint_y=None,
            height=dp(40),
            bold=True,
            theme_text_color="Custom",
            text_color=(0.3, 0.9, 0.7, 1),
        )
        self.result_card.add_widget(self.total_label)
        self.result_card.add_widget(self.dots_label)
        layout.add_widget(self.result_card)

        # 计算按钮
        calc_btn = MDRaisedButton(
            text="计算 DOTS",
            font_size=dp(16),
            md_bg_color=(0.91, 0.27, 0.38, 1),
            size_hint_y=None,
            height=dp(44),
            on_release=lambda b: self._calc(),
        )
        layout.add_widget(calc_btn)

        # 返回
        back_btn = MDFlatButton(
            text="返回主菜单",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(36),
            on_release=lambda b: self._go_back(),
        )
        layout.add_widget(back_btn)

        layout.add_widget(MDBoxLayout())  # 弹性填充
        self.add_widget(layout)

    def _calc(self):
        """计算 DOTS"""
        try:
            bw = float(self.fields["bw"].text.strip())
            squat = float(self.fields["squat"].text.strip())
            bench = float(self.fields["bench"].text.strip())
            deadlift = float(self.fields["deadlift"].text.strip())

            if bw <= 0:
                self._show_error("体重必须大于 0")
                return

            total = squat + bench + deadlift
            dots = calc_dots(bw, total)

            self.total_label.text = f"三大项总和: {total} kg"
            self.dots_label.text = f"DOTS: {dots}"
        except ValueError:
            self._show_error("请输入有效数字")

    def _show_error(self, msg):
        self.dialog = MDDialog(
            title="错误",
            text=msg,
            buttons=[
                MDRaisedButton(text="好", on_release=lambda b: self.dialog.dismiss()),
            ],
        )
        self.dialog.open()

    def on_pre_enter(self):
        """进入页面时刷新 PR 默认值"""
        pr_data = load_pr()
        mapping = {"bw": "体重", "squat": "深蹲", "bench": "卧推", "deadlift": "硬拉"}
        for key, data_key in mapping.items():
            if key in self.fields:
                val = pr_data.get(data_key, 0)
                if val and self.fields[key].text in ("0", ""):
                    self.fields[key].text = str(val)

    def _go_back(self):
        self.manager.current = "menu"

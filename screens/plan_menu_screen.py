# 训练计划选择 Screen

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView

from core.data import get_program_names


class PlanMenuScreen(Screen):
    """选择训练计划"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "plan_menu"
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=[dp(20), dp(30), dp(20), dp(20)],
        )

        # 标题
        title = MDLabel(
            text="选择训练计划",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=dp(60),
            bold=True,
        )
        layout.add_widget(title)

        # 计划卡片
        programs = get_program_names()
        for name in programs:
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100),
                padding=dp(15),
                spacing=dp(8),
                md_bg_color=(0.06, 0.20, 0.38, 1),
                radius=[dp(12)],
                ripple_behavior=True,
                on_release=lambda btn, p=name: self._select_program(p),
            )

            card.add_widget(
                MDIcon(
                    icon="chart-line",
                    font_size=dp(32),
                    halign="center",
                    size_hint_y=None,
                    height=dp(40),
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 0.95),
                )
            )
            card.add_widget(
                MDLabel(
                    text=name,
                    font_style="Subtitle1",
                    halign="center",
                    size_hint_y=None,
                    height=dp(30),
                    bold=True,
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 0.95),
                )
            )
            layout.add_widget(card)

        # 更多计划（占位）
        locked = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=dp(15),
            md_bg_color=(0.2, 0.2, 0.2, 0.5),
            radius=[dp(12)],
            disabled=True,
        )
        locked.add_widget(
            MDLabel(
                text="更多计划即将推出...",
                font_style="Subtitle1",
                halign="center",
                size_hint_y=None,
                height=dp(40),
                theme_text_color="Hint",
            )
        )
        layout.add_widget(locked)

        # 返回按钮
        back_btn = MDFlatButton(
            text="返回主菜单",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40),
            on_release=lambda b: self._go_back(),
        )
        layout.add_widget(back_btn)

        layout.add_widget(MDBoxLayout())  # 弹性填充
        self.add_widget(layout)

    def _select_program(self, program_name):
        """选择计划 → 显示练前需知 → 进入视图"""
        if program_name == "Jamal 力量举计划" or "jamal" in program_name.lower():
            self._show_jamal_notice()
        else:
            self.manager.get_screen("plan_view").set_program("jamal")
            self.manager.current = "plan_view"

    def _show_jamal_notice(self):
        """显示练前需知弹窗"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        theme = app.theme

        content = MDScrollView(size_hint_y=None, height=dp(360))
        text = MDLabel(
            text=(
                "[b]W1~W11 训练间隔：[/b]\n"
                "D1 → D2 → 休息 → D3 → 休息 → D4 → 休息 → D1\n\n"
                "[b]W12 训练间隔：[/b]\n"
                "D1 → 休息 → D2 → 休息 → 休息 → D3\n\n"
                "[b]每周 D2 卧推补充：[/b]\n"
                "卧推一般都是 4 组，可根据自身容量增加 1~2 组\n\n"
                "[b]D4 硬拉重量选择：[/b]\n"
                "硬拉根据 RPE 选择重量，做完后重量 -10% 做完剩下的组。\n"
                "例：RPE 3, 4, 5，对应重量 100, 110, 120。\n"
                "做完 RPE 5（120）之后，用 120 × (1-10%) = 108 做剩下的组"
            ),
            font_style="Body1",
            halign="left",
            valign="top",
            padding=[dp(20), dp(10)],
            markup=True,
            size_hint_y=None,
            theme_text_color="Custom",
            text_color=theme["text"],
        )
        text.bind(
            texture_size=lambda inst, val: setattr(text, "height", max(val[1], dp(360)))
        )
        content.add_widget(text)

        dialog = MDDialog(
            title="练前需知",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="知道了，开始训练",
                    md_bg_color=theme["primary"],
                    on_release=lambda b: (
                        dialog.dismiss(),
                        self._proceed_to_plan(),
                    )
                ),
            ],
        )
        dialog.open()

    def _proceed_to_plan(self):
        self.manager.get_screen("plan_view").set_program("jamal")
        self.manager.current = "plan_view"

    def _go_back(self):
        self.manager.current = "menu"

# 免责协议 Screen

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout


def _T():
    return MDApp.get_running_app().theme



AGREEMENT_TEXT = """重要提示：请仔细阅读以下协议

1. 免责声明
本软件（力量举计划选择器）仅供个人训练参考使用。开发者不保证训练计划的准确性、完整性和适用性。用户应根据自身身体状况合理安排训练。

2. 健康风险
力量举训练存在一定的受伤风险。在开始任何训练计划之前，建议先咨询专业医师或健身教练。如因使用本软件导致的任何身体损伤或其他损失，开发者不承担任何责任。

3. 数据隐私
本软件的所有数据（包括 PR 数据、训练记录等）仅保存在本地设备上，不会上传至任何服务器。开发者无法访问您的个人数据。

4. 知识产权
本软件及其所含内容受版权法保护。未经授权不得复制、分发或修改。

5. 协议变更
开发者保留随时修改本协议的权利。继续使用本软件即表示您接受更新后的协议。

6. 版权声明
本软件（LWUP - lai Wei universe power）©2026 张绍远（抖音：张开来自我）保留所有权利。未经授权不得复制、分发或修改。"""


class DisclaimerScreen(Screen):
    """免责协议页面 — 同意后才能进入主菜单"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "disclaimer"
        self.build_ui()

    def build_ui(self):
        # 主容器
        layout = MDBoxLayout(orientation="vertical", spacing=dp(10))

        # ---- 标题 ----
        title = MDLabel(
            text="免责协议",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=dp(60),
            theme_text_color="Custom",
            text_color=_T()["primary"],
            bold=True,
        )
        layout.add_widget(title)

        # ---- 协议内容（可滚动） ----
        scroll = MDScrollView()
        content = MDLabel(
            text=AGREEMENT_TEXT,
            font_style="Body1",
            halign="left",
            valign="top",
            padding=[dp(20), dp(10), dp(20), dp(10)],
            markup=True,
            size_hint_y=None,
            theme_text_color="Custom",
            text_color=_T()["text"],
        )
        content.bind(
            texture_size=lambda inst, val: setattr(
                content, "height", max(val[1], dp(400))
            )
        )
        scroll.add_widget(content)
        layout.add_widget(scroll)

        # ---- 按钮区域 ----
        btn_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(60),
            padding=[dp(20), dp(5), dp(20), dp(15)],
        )

        agree_btn = MDRaisedButton(
            text="同  意",
            font_size=dp(16),
            md_bg_color=_T()["primary"],
            on_release=self.on_agree,
        )
        disagree_btn = MDFlatButton(
            text="不同意",
            font_size=dp(16),
            text_color=_T()["text_sec"],
            on_release=self.on_disagree,
        )

        btn_layout.add_widget(agree_btn)
        btn_layout.add_widget(disagree_btn)
        layout.add_widget(btn_layout)

        self.add_widget(layout)

    def on_agree(self, *args):
        """同意协议 → 进入主菜单"""
        try:
            from kivymd.app import MDApp
            MDApp.get_running_app().play_click()
        except:
            pass
        self.manager.current = "menu"

    def on_disagree(self, *args):
        """不同意 → 退出 App"""
        try:
            from kivymd.app import MDApp
            MDApp.get_running_app().play_click()
        except:
            pass
        Clock.schedule_once(lambda dt: exit(0), 0.3)

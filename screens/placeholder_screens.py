# 占位 Screen（阶段五、六完善）

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout


def _T():
    return MDApp.get_running_app().theme



class PRInputScreen(Screen):
    """PR 数据输入（占位）"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "pr_input"
        layout = MDBoxLayout(orientation="vertical", spacing=dp(20), padding=dp(30))
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(60)))
        layout.add_widget(MDLabel(text="PR 数据", font_style="H4", halign="center"))
        layout.add_widget(MDLabel(text="此功能待完善", font_style="Body1", halign="center",
                                  theme_text_color="Hint"))
        layout.add_widget(MDBoxLayout())
        back = MDFlatButton(text="返回主菜单", font_size=dp(14), size_hint_y=None, height=dp(40))
        back.bind(on_release=lambda btn: setattr(self.manager, "current", "menu"))
        layout.add_widget(back)
        self.add_widget(layout)


class HistoryScreen(Screen):
    """训练历史（占位）"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "history"
        layout = MDBoxLayout(orientation="vertical", spacing=dp(20), padding=dp(30))
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(60)))
        layout.add_widget(MDLabel(text="训练记录", font_style="H4", halign="center"))
        layout.add_widget(MDLabel(text="此功能待完善", font_style="Body1", halign="center",
                                  theme_text_color="Hint"))
        layout.add_widget(MDBoxLayout())
        back = MDFlatButton(text="返回主菜单", font_size=dp(14), size_hint_y=None, height=dp(40))
        back.bind(on_release=lambda btn: setattr(self.manager, "current", "menu"))
        layout.add_widget(back)
        self.add_widget(layout)


class DOTSScreen(Screen):
    """DOTS 计算（占位）"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "dots"
        layout = MDBoxLayout(orientation="vertical", spacing=dp(20), padding=dp(30))
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(60)))
        layout.add_widget(MDLabel(text="DOTS 计算", font_style="H4", halign="center"))
        layout.add_widget(MDLabel(text="此功能待完善", font_style="Body1", halign="center",
                                  theme_text_color="Hint"))
        layout.add_widget(MDBoxLayout())
        back = MDFlatButton(text="返回主菜单", font_size=dp(14), size_hint_y=None, height=dp(40))
        back.bind(on_release=lambda btn: setattr(self.manager, "current", "menu"))
        layout.add_widget(back)
        self.add_widget(layout)


class AboutScreen(Screen):
    """关于页面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "about"
        layout = MDBoxLayout(orientation="vertical", spacing=dp(6), padding=dp(30))
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(40)))

        # 标志
        layout.add_widget(MDLabel(text="🔥", font_style="H1", halign="center", size_hint_y=None, height=dp(50)))
        layout.add_widget(MDLabel(text="LWUP", font_style="H2", halign="center", bold=True,
                                  theme_text_color="Custom", text_color=_T()["primary"]))
        layout.add_widget(MDLabel(text="lai Wei universe power", font_style="Subtitle2",
                                  halign="center", theme_text_color="Hint"))
        # 分隔线
        line = MDBoxLayout(size_hint_y=None, height=dp(2), md_bg_color=_T()["primary"],
                           padding=[dp(60), 0])
        layout.add_widget(line)
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(12)))

        info = (
            "版本：v0.5.1 测试版\n"
            "制作人：张绍远\n"
            "抖音：张开来自我\n"
            "邮箱：910571220@qq.com\n"
            "\n"
            "力量举训练计划助手\n"
            "基于 Jamal 百分比计划\n"
            "\n"
            "数据仅保存在本地\n"
            "\n"
            "该软件仅为测试版本，bug较多，请见谅"
        )
        layout.add_widget(MDLabel(text=info, font_style="Body1", halign="center",
                                  theme_text_color="Custom", text_color=_T()["text"]))
        layout.add_widget(MDBoxLayout())
        back = MDFlatButton(text="返回", font_size=dp(14), size_hint_y=None, height=dp(40))
        back.bind(on_release=lambda btn: setattr(self.manager, "current", "menu"))
        layout.add_widget(back)
        self.add_widget(layout)

# LWUP - lai Wei universe power
# 力量举训练计划助手 - 四主题切换系统

import os, sys
from kivy.config import Config

Config.set("kivy", "exit_on_escape", "0")
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ZCOOL_KuaiLe.ttf")
Config.set("kivy", "default_font", ["ZCOOL_KuaiLe", _FONT_PATH])

from kivy.core.text import LabelBase
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivymd.app import MDApp

# ── 四套主题配色 ──
THEMES = [
    {
        "name": "暗黑钢铁",
        "theme_style": "Dark",
        "palette": "DeepOrange",
        "bg": (0.05, 0.05, 0.08, 1),
        "surface": (0.09, 0.09, 0.12, 1),
        "primary": (1, 0.27, 0, 1),
        "primary_light": (1, 0.42, 0.21, 1),
        "accent": (1, 0.18, 0.33, 1),
        "text": (0.94, 0.93, 0.89, 1),
        "text_sec": (0.54, 0.54, 0.54, 1),
        "steel": (0.16, 0.16, 0.21, 1),
        "icon": "weather-night",
    },
    {
        "name": "纯净明亮",
        "theme_style": "Light",
        "palette": "Blue",
        "bg": (0.96, 0.96, 0.96, 1),
        "surface": (1, 1, 1, 1),
        "primary": (0.15, 0.39, 0.92, 1),
        "primary_light": (0.35, 0.55, 0.95, 1),
        "accent": (0.92, 0.31, 0.39, 1),
        "text": (0.1, 0.1, 0.1, 1),
        "text_sec": (0.45, 0.45, 0.45, 1),
        "steel": (0.85, 0.85, 0.88, 1),
        "icon": "white-balance-sunny",
    },
    {
        "name": "粉甜可爱",
        "theme_style": "Light",
        "palette": "Pink",
        "bg": (0.99, 0.95, 0.97, 1),
        "surface": (1, 1, 1, 1),
        "primary": (0.93, 0.28, 0.60, 1),
        "primary_light": (0.95, 0.45, 0.70, 1),
        "accent": (0.80, 0.20, 0.40, 1),
        "text": (0.29, 0.02, 0.31, 1),
        "text_sec": (0.55, 0.35, 0.50, 1),
        "steel": (0.95, 0.88, 0.92, 1),
        "icon": "heart",
    },
    {
        "name": "霓虹炫彩",
        "theme_style": "Dark",
        "palette": "Red",
        "bg": (0.04, 0.04, 0.10, 1),
        "surface": (0.10, 0.10, 0.23, 1),
        "primary": (1, 0.18, 0.33, 1),
        "primary_light": (0.90, 0.30, 0.50, 1),
        "accent": (0.20, 1, 0.80, 1),
        "text": (1, 1, 1, 1),
        "text_sec": (0.60, 0.60, 0.80, 1),
        "steel": (0.15, 0.15, 0.30, 1),
        "icon": "brightness-7",
    },
]


class PowerLiftingApp(MDApp):
    """LWUP 力量举训练助手 - 四主题切换"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_theme_idx = 0
        theme = THEMES[0]
        self.theme_cls.primary_palette = theme["palette"]
        self.theme_cls.theme_style = theme["theme_style"]
        self.theme_cls.material_style = "M3"
        self.sound_enabled = True
        self.click_sound = None

    @property
    def theme(self):
        return THEMES[self.current_theme_idx]

    def build(self):
        self.title = "LWUP"
        _icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
        self.icon = _icon_path
        Window.set_icon(_icon_path)

        # 禁用鼠标右键的红色触摸点
        _orig_dispatch = Window.dispatch
        def _filter_dispatch(event_type, *args, **kwargs):
            if event_type == 'on_mouse_down' and len(args) >= 3 and args[2] == 'right':
                return  # 拦截右键 → 不产生红色小球
            return _orig_dispatch(event_type, *args, **kwargs)
        Window.dispatch = _filter_dispatch

        _sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "click.wav")
        self.click_sound = SoundLoader.load(_sound_path)

        for _name in ["Roboto", "RobotoThin", "RobotoLight", "RobotoMedium", "RobotoBlack"]:
            LabelBase.register(name=_name, fn_regular=_FONT_PATH)

        # 初始化数据路径
        from core.data import init_data_paths
        init_data_paths(self.user_data_dir)

        # 初始化宠物配置
        from pets.pet_data import init_pet_config
        init_pet_config(self.user_data_dir)

        # 根布局：FloatLayout（ScreenManager + PetOverlay 叠加）
        root = FloatLayout()

        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))
        self._build_all_screens()
        root.add_widget(self.sm)

        # 宠物叠加层（在所有界面之上）
        from pets.pet_overlay import PetOverlay
        self.pet_overlay = PetOverlay()
        root.add_widget(self.pet_overlay)

        return root

    def _build_all_screens(self):
        """重建所有页面（主题切换时调用）"""
        self.sm.clear_widgets()
        from screens.disclaimer_screen import DisclaimerScreen
        from screens.menu_screen import MenuScreen
        from screens.plan_menu_screen import PlanMenuScreen
        from screens.plan_view_screen import PlanViewScreen
        from screens.history_screen import HistoryScreen
        from screens.pr_input_screen import PRInputScreen
        from screens.dots_screen import DOTSScreen
        from screens.placeholder_screens import AboutScreen
        from screens.pet_menu_screen import PetMenuScreen
        self.sm.add_widget(DisclaimerScreen(name="disclaimer"))
        self.sm.add_widget(MenuScreen(name="menu"))
        self.sm.add_widget(PlanMenuScreen(name="plan_menu"))
        self.sm.add_widget(PlanViewScreen(name="plan_view"))
        self.sm.add_widget(PRInputScreen(name="pr_input"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(DOTSScreen(name="dots"))
        self.sm.add_widget(AboutScreen(name="about"))
        self.sm.add_widget(PetMenuScreen(name="pet_menu"))

    def switch_theme(self):
        """切换到下一个主题"""
        self.current_theme_idx = (self.current_theme_idx + 1) % len(THEMES)
        theme = self.theme
        self.theme_cls.primary_palette = theme["palette"]
        self.theme_cls.theme_style = theme["theme_style"]
        # 重建所有页面
        self._build_all_screens()
        self.sm.current = "menu"
        self.play_click()

    def on_start(self):
        if os.name == "nt":
            Window.size = (420, 780)

    def go_to(self, screen_name):
        self.root.current = screen_name

    def play_click(self):
        if self.sound_enabled and self.click_sound:
            self.click_sound.play()


if __name__ == "__main__":
    PowerLiftingApp().run()

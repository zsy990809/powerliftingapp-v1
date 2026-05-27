# 主菜单 Screen — 支持动态主题

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp

from core.data import load_pr


def _T():
    """获取当前主题颜色"""
    return MDApp.get_running_app().theme


MENU_ITEMS = [
    {"icon": "clipboard-list", "text": "选择计划", "target": "plan_menu"},
    {"icon": "dumbbell",       "text": "PR 数据",  "target": "pr_input"},
    {"icon": "book-open-variant", "text": "训练记录", "target": "history"},
    {"icon": "dog-side",      "text": "健身宠物", "target": "pet_menu"},
    {"icon": "scale-balance",  "text": "DOTS 计算", "target": "dots"},
    {"icon": "information",    "text": "关于",      "target": "about"},
    {"icon": "exit-run",       "text": "退出",      "target": "exit"},
]


class MenuScreen(Screen):
    """主菜单 — 支持四主题切换"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "menu"
        self._card_widgets = []
        self.build_ui()

    def build_ui(self):
        t = _T()
        layout = MDBoxLayout(
            orientation="vertical", spacing=dp(12),
            padding=[dp(16), dp(24), dp(16), dp(12)],
        )

        # ── 标题 ──
        title_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(90))

        # 闪闪发光的广告位
        ad_label = MDLabel(
            text="⭐ 广告位招租 ⭐", font_style="Subtitle1", halign="center",
            size_hint_y=None, height=dp(22), bold=True,
            theme_text_color="Custom", text_color=(1, 0.84, 0, 1),  # 金色
        )
        title_box.add_widget(ad_label)
        self._ad_label = ad_label
        Clock.schedule_once(lambda dt: self._start_ad_flash(), 0.3)

        glow = MDLabel(
            text="LWUP", font_style="H2", halign="center",
            size_hint_y=None, height=dp(50), bold=True,
            theme_text_color="Custom", text_color=t["primary"],
        )
        title_box.add_widget(glow)
        line = MDBoxLayout(size_hint_y=None, height=dp(3), md_bg_color=t["primary_light"], padding=[dp(40), 0])
        title_box.add_widget(line)
        sub = MDLabel(
            text="lai Wei universe power  ▸", font_style="Caption",
            halign="center", size_hint_y=None, height=dp(18),
            theme_text_color="Custom", text_color=t["text_sec"],
        )
        title_box.add_widget(sub)
        layout.add_widget(title_box)

        # ── 三大项 ──
        pr_data = load_pr()
        lifts = [
            ("深蹲", pr_data.get("深蹲", 230), t["primary"]),
            ("卧推", pr_data.get("卧推", 140), t["accent"]),
            ("硬拉", pr_data.get("硬拉", 190), t["primary_light"]),
        ]
        lift_box = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(54),
            spacing=dp(8), padding=[dp(4), dp(2), dp(4), dp(4)],
        )
        for _name, _wt, _color in lifts:
            plate = MDCard(
                orientation="vertical", size_hint=(0.33, 1),
                md_bg_color=(0, 0, 0, 0), radius=[dp(26)],
                padding=[dp(4), dp(2)], line_color=_color, line_width=dp(2),
            )
            plate.add_widget(MDLabel(
                text=str(_wt), font_style="H5", halign="center",
                bold=True, size_hint_y=0.55,
                theme_text_color="Custom", text_color=_color,
            ))
            plate.add_widget(MDLabel(
                text=_name, font_style="Caption", halign="center",
                size_hint_y=0.35, theme_text_color="Custom", text_color=t["text_sec"],
            ))
            lift_box.add_widget(plate)
        layout.add_widget(lift_box)

        # ── 功能卡片网格 ──
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        self._card_widgets = []
        _card_colors = [t["primary"], t["accent"], t["primary_light"],
                        t["accent"], t["primary"], t["steel"], (0.35, 0.07, 0.07, 1)]
        for i, item in enumerate(MENU_ITEMS):
            card = MDCard(
                orientation="vertical", size_hint_y=None, height=dp(105),
                padding=[dp(6), dp(6)], spacing=dp(2),
                md_bg_color=t["surface"], radius=[dp(10)],
                line_width=dp(1.5), line_color=(*_card_colors[i][:3], 0.3),
                ripple_behavior=True,
                on_release=lambda btn, tg=item["target"]: self._on_card_click(tg),
            )
            icon = MDIcon(
                icon=item["icon"], font_size=dp(28), halign="center",
                size_hint_y=0.55, theme_text_color="Custom",
                text_color=_card_colors[i],
            )
            card.add_widget(icon)
            card.add_widget(MDLabel(
                text=item["text"], font_style="Subtitle2", halign="center",
                size_hint_y=0.35, bold=True,
                theme_text_color="Custom", text_color=t["text"],
            ))
            grid.add_widget(card)
            self._card_widgets.append(card)
        layout.add_widget(grid)

        # ── 底部栏：主题切换 + 版本号 ──
        bottom = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
        # 主题切换按钮（左）
        theme_btn = MDIconButton(
            icon=t["icon"], font_size=dp(18),
            on_release=lambda btn: self._switch_theme(),
            theme_text_color="Custom", text_color=t["text_sec"],
        )
        bottom.add_widget(theme_btn)
        # 版本号（右）
        bottom.add_widget(MDBoxLayout())  # 弹性
        bottom.add_widget(MDLabel(
            text="v0.5.1 测试版", font_style="Caption",
            size_hint_x=0.4, halign="right",
            theme_text_color="Custom", text_color=t["text_sec"],
        ))
        layout.add_widget(bottom)
        self.add_widget(layout)

        # 入场动画
        Clock.schedule_once(lambda dt: self._entry_animation(), 0.1)

    def _entry_animation(self):
        for i, w in enumerate(self._card_widgets):
            w.opacity = 0
            w.y -= dp(20)
            anim = Animation(opacity=1, y=w.y + dp(20), duration=0.3, t="out_back")
            anim.delay = 0.06 * i
            anim.start(w)

    def _start_ad_flash(self):
        """广告位招租 闪闪发光动画"""
        if not hasattr(self, '_ad_label') or not self._ad_label:
            return

        def _pulse(_dt):
            if not hasattr(self, '_ad_label') or not self._ad_label:
                return
            # 金色 ↔ 白色 交替，配合透明度脉冲
            is_gold = self._ad_label.text_color == (1, 0.84, 0, 1)
            if is_gold:
                anim = Animation(text_color=(1, 1, 1, 1), opacity=0.6, duration=0.4, t="out_sine")
            else:
                anim = Animation(text_color=(1, 0.84, 0, 1), opacity=1.0, duration=0.4, t="out_sine")
            anim.start(self._ad_label)

        Clock.schedule_interval(_pulse, 0.8)

    def _switch_theme(self):
        MDApp.get_running_app().switch_theme()

    def _on_card_click(self, target):
        try:
            MDApp.get_running_app().play_click()
        except:
            pass
        if target == "exit":
            exit(0)
        else:
            self.manager.current = target

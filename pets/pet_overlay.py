"""
浮动宠物叠加层 — 可在所有界面拖动、点击交互
"""

import os
import random
import glob
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard

from pets.pet_data import (
    get_selected_pet, get_pet, get_api_key, get_pet_visible,
    set_pet_visible, get_pet_position, set_pet_position,
)
from pets.pet_chat import SpeechBubble, ChatDialog


def _assets(*parts):
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "pets", *parts
    )


class PetOverlay(FloatLayout):
    """
    浮动宠物叠加层 — 在所有界面之上
    - 可拖动
    - 点出弹出 3 操作按钮
    - 帧动画
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.pet_id = None
        self.pet_def = None
        self.frames = []
        self.current_frame_idx = 0
        self.anim_clock = None
        self.pet_image = None
        self.pet_size = (dp(80), dp(100))

        # 子组件引用
        self.action_menu = None
        self.speech_bubble = None
        self.chat_dialog = None
        self.horror_sound = None

        # 拖动状态
        self._drag_start = None
        self._pet_pos = (0.8, 0.15)  # 相对位置 (0-1)

        # 加载恐怖音效
        self._load_horror_sound()

        # 初始化宠物
        Clock.schedule_once(lambda dt: self._init_pet(), 0.5)

    def _assets_path(self, *parts):
        return _assets(*parts)

    def _load_horror_sound(self):
        """加载恐怖音效"""
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "horror.wav"
        )
        if os.path.exists(path):
            self.horror_sound = SoundLoader.load(path)

    def _init_pet(self):
        """从配置加载宠物"""
        pet_id = get_selected_pet()
        if not pet_id:
            return

        self.pet_id = pet_id
        self.pet_def = get_pet(pet_id)
        if not self.pet_def:
            return

        if not get_pet_visible():
            return

        # 加载帧
        self._load_frames()

        # 恢复位置
        px, py = get_pet_position()
        self._pet_pos = (px, py)

        # 创建宠物图像
        self._create_pet_widget()

        # 启动动画（多帧时）
        if self.pet_def.get("frame_count", 1) > 1 and len(self.frames) > 1:
            fps = self.pet_def.get("fps", 6)
            self.anim_clock = Clock.schedule_interval(self._next_frame, 1.0 / fps)

    def _load_frames(self):
        """加载宠物帧图像到内存"""
        pet_def = self.pet_def
        if not pet_def:
            return

        if pet_def.get("emoji"):
            # Emoji 宠物——用文字替代
            self.frames = [pet_def["emoji_char"]]
            return

        frame_count = pet_def.get("frame_count", 1)
        pattern = pet_def.get("frame_pattern", "ye_{i:02d}.png")
        pet_dir = pet_def.get("dir", "")

        for i in range(frame_count):
            fname = pattern.replace("{i:02d}", f"{i:02d}")
            fpath = self._assets_path(pet_dir, fname)
            if os.path.exists(fpath):
                self.frames.append(fpath)
            else:
                # 尝试静态图
                static_path = self._assets_path(pet_dir, "static.png")
                if os.path.exists(static_path):
                    self.frames.append(static_path)
                    break

        if not self.frames:
            self.frames = ["🐾"]  # 终极备用

    def _create_pet_widget(self):
        """创建可显示的宠物 Widget"""
        self._remove_pet_widget()

        if self.pet_def.get("emoji"):
            # Emoji 模式
            self.pet_image = Label(
                text=self.frames[0] if self.frames else "🐱",
                font_size=dp(40),
                size_hint=(None, None),
                size=(dp(50), dp(50)),
            )
        else:
            # 图片模式
            tex_path = self.frames[0] if self.frames else ""
            if not tex_path or not os.path.exists(str(tex_path)):
                tex_path = self._assets_path("ye_jiaxing", "static.png")
            self.pet_image = Image(
                source=str(tex_path),
                size_hint=(None, None),
                allow_stretch=True,
                keep_ratio=True,
            )
            # 根据窗口比例确定大小
            w_ratio, h_ratio = self.pet_def.get("size", (0.12, 0.16))
            self.pet_image.size = (Window.width * w_ratio, Window.height * h_ratio)

        # 初始位置
        self.pet_image.pos = (
            (Window.width - self.pet_image.width) * self._pet_pos[0],
            (Window.height - self.pet_image.height) * self._pet_pos[1],
        )

        self.add_widget(self.pet_image)

    def _remove_pet_widget(self):
        """移除宠物 Widget"""
        if self.pet_image and self.pet_image in self.children:
            self.remove_widget(self.pet_image)
        self.pet_image = None

    def _next_frame(self, dt):
        """动画下一帧"""
        if not self.pet_image or not self.frames or self.pet_def.get("emoji"):
            return
        self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frames)
        tex_path = self.frames[self.current_frame_idx]
        if os.path.exists(str(tex_path)):
            self.pet_image.source = str(tex_path)

    # ── 触摸事件：拖动 + 点击 ──

    def on_touch_down(self, touch):
        if not self.pet_image or self.pet_image not in self.children:
            return super().on_touch_down(touch)

        # 先让子 widget（操作菜单按钮等）处理触摸
        if super().on_touch_down(touch):
            return True

        # 检查是否点击了宠物
        if self.pet_image.collide_point(*touch.pos):
            self._drag_start = touch.pos
            self._drag_offset = (
                touch.x - self.pet_image.x,
                touch.y - self.pet_image.y,
            )
            return True

        # 点击其他地方 → 关闭操作菜单和气泡，放行触摸到下层界面
        self._dismiss_action_menu()
        self._dismiss_speech_bubble()
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self._drag_start:
            return super().on_touch_move(touch)

        # 拖动宠物
        if self.pet_image:
            dx = touch.x - self._drag_start[0]
            dy = touch.y - self._drag_start[1]

            # 判断是否为拖动（移动超过阈值）
            if abs(dx) > 5 or abs(dy) > 5:
                new_x = touch.x - self._drag_offset[0]
                new_y = touch.y - self._drag_offset[1]

                # 边界限制
                new_x = max(0, min(new_x, Window.width - self.pet_image.width))
                new_y = max(0, min(new_y, Window.height - self.pet_image.height))

                self.pet_image.pos = (new_x, new_y)

                # 更新相对位置
                self._pet_pos = (
                    new_x / (Window.width - self.pet_image.width) if Window.width > self.pet_image.width else 0,
                    new_y / (Window.height - self.pet_image.height) if Window.height > self.pet_image.height else 0,
                )

        return True

    def on_touch_up(self, touch):
        if not self._drag_start:
            return super().on_touch_up(touch)

        dx = abs(touch.x - self._drag_start[0])
        dy = abs(touch.y - self._drag_start[1])

        # 保存位置
        set_pet_position(self._pet_pos[0], self._pet_pos[1])

        # 如果是点击（没有拖动）
        if dx < 10 and dy < 10:
            self._show_action_menu()
        else:
            # 拖动结束，收起菜单
            self._dismiss_action_menu()

        self._drag_start = None
        return True

    # ── 操作菜单 ──

    def _show_action_menu(self):
        """显示 3 个操作按钮"""
        self._dismiss_action_menu()

        if not self.pet_image:
            return

        theme = MDApp.get_running_app().theme
        menu = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint=(None, None),
            padding=[dp(4), dp(4)],
        )
        menu.size = (dp(100), dp(130))

        btn_go = MDRaisedButton(
            text="滚",
            size_hint=(1, None), height=dp(34),
            md_bg_color=(0.8, 0.15, 0.15, 0.9),
            font_size=dp(12),
            on_release=lambda b: self._action_go(),
        )
        btn_chat = MDRaisedButton(
            text="聊天",
            size_hint=(1, None), height=dp(34),
            md_bg_color=theme["primary"],
            font_size=dp(12),
            on_release=lambda b: self._action_chat(),
        )
        btn_scary = MDRaisedButton(
            text="不可名状の古神低语",
            size_hint=(1, None), height=dp(34),
            md_bg_color=(0.3, 0.1, 0.3, 0.9),
            font_size=dp(8),
            on_release=lambda b: self._action_scary(),
        )

        menu.add_widget(btn_go)
        menu.add_widget(btn_chat)
        menu.add_widget(btn_scary)

        # 放在宠物旁边
        px, py = self.pet_image.pos
        pw, ph = self.pet_image.size
        menu_x = px + pw + dp(5)
        menu_y = py
        if menu_x + dp(100) > Window.width:
            menu_x = px - dp(105)
        if menu_y + dp(130) > Window.height:
            menu_y = Window.height - dp(130)
        if menu_y < 0:
            menu_y = 0

        menu.pos = (menu_x, menu_y)
        self.action_menu = menu
        self.add_widget(menu)

    def _dismiss_action_menu(self):
        if self.action_menu and self.action_menu in self.children:
            self.remove_widget(self.action_menu)
        self.action_menu = None

    def _dismiss_speech_bubble(self):
        if self.speech_bubble and self.speech_bubble in self.children:
            self.speech_bubble.cancel_auto_dismiss()
            self.remove_widget(self.speech_bubble)
        self.speech_bubble = None

    # ── 操作按钮动作 ──

    def _action_go(self):
        """滚 — 隐藏宠物"""
        self._dismiss_action_menu()
        self.hide()

    def _action_chat(self):
        """聊天"""
        self._dismiss_action_menu()

        api_key = get_api_key()
        if not api_key:
            # 无 API key：显示随机口头禅气泡
            self._show_catchphrase()
        else:
            # 有 API key：打开聊天对话框
            self._open_chat_dialog()

    def _action_scary(self):
        """不可名状の古神低语 — 全屏古神GIF 3s + 恐怖音效"""
        self._dismiss_action_menu()

        # 播放恐怖音效
        if self.horror_sound:
            self.horror_sound.play()

        # 全屏古神动画覆盖层（手动帧轮播，避免Kivy GIF加载bug）
        self.gushen_frames = []
        gushen_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "gushen_frames"
        )
        if os.path.exists(gushen_dir):
            for fpath in sorted(glob.glob(os.path.join(gushen_dir, "frame_*.png"))):
                self.gushen_frames.append(fpath)

            if self.gushen_frames:
                self.gushen_overlay = Image(
                    source=self.gushen_frames[0],
                    size_hint=(1, 1),
                    allow_stretch=True,
                    keep_ratio=True,
                )
                self.add_widget(self.gushen_overlay)
                self.gushen_frame_idx = 0
                # 30帧 / 10fps ≈ 3s 完整轮播一次
                self.gushen_anim = Clock.schedule_interval(self._next_gushen_frame, 1.0 / 10)
                Clock.schedule_once(lambda dt: self._stop_scary(), 3)

    def _next_gushen_frame(self, dt):
        """古神动画下一帧"""
        if not hasattr(self, 'gushen_overlay') or not self.gushen_overlay:
            return
        self.gushen_frame_idx = (self.gushen_frame_idx + 1) % len(self.gushen_frames)
        self.gushen_overlay.source = self.gushen_frames[self.gushen_frame_idx]

    def _stop_scary(self):
        if self.horror_sound:
            self.horror_sound.stop()
        # 移除全屏动画覆盖层
        if hasattr(self, 'gushen_anim') and self.gushen_anim:
            self.gushen_anim.cancel()
            self.gushen_anim = None
        if hasattr(self, 'gushen_overlay') and self.gushen_overlay in self.children:
            self.remove_widget(self.gushen_overlay)
            self.gushen_overlay = None
        self.gushen_frames = []

    # ── 聊天/气泡 ──

    def _show_catchphrase(self):
        """显示随机口头禅气泡"""
        if not self.pet_def:
            return

        self._dismiss_speech_bubble()

        phrases = self.pet_def.get("no_api_phrases", [])
        if not phrases:
            phrases = [self.pet_def.get("catchphrase", "你好！")]

        text = random.choice(phrases)
        self._show_speech_bubble(text)

    def _show_speech_bubble(self, text):
        """在宠物旁显示云朵气泡"""
        if not self.pet_image:
            return

        self._dismiss_speech_bubble()

        bubble = SpeechBubble(text=text)
        # 放在宠物上方
        px, py = self.pet_image.pos
        pw, ph = self.pet_image.size
        bubble_x = px + pw * 0.1
        bubble_y = py + ph + dp(5)
        bubble.pos = (bubble_x, bubble_y)
        self.speech_bubble = bubble
        self.add_widget(bubble)

    def _open_chat_dialog(self):
        """打开 AI 聊天对话框"""
        api_key = get_api_key()
        plan_context = "当前使用 Jamal 力量举计划"
        self.chat_dialog = ChatDialog(
            self.pet_id or "unknown",
            api_key,
            plan_context,
        )

    # ── 显示/隐藏 ──

    def show(self):
        """显示宠物"""
        if self.pet_image and self.pet_image not in self.children:
            self.add_widget(self.pet_image)
            if self.pet_def.get("frame_count", 1) > 1 and len(self.frames) > 1:
                fps = self.pet_def.get("fps", 6)
                self.anim_clock = Clock.schedule_interval(self._next_frame, 1.0 / fps)
        elif not self.pet_image:
            self._init_pet()
        set_pet_visible(True)

    def hide(self):
        """隐藏宠物"""
        if self.pet_image and self.pet_image in self.children:
            self.remove_widget(self.pet_image)
        if self.anim_clock:
            self.anim_clock.cancel()
            self.anim_clock = None
        self._dismiss_action_menu()
        self._dismiss_speech_bubble()
        set_pet_visible(False)

    def toggle(self):
        """切换显示/隐藏"""
        if self.pet_image and self.pet_image in self.children:
            self.hide()
        else:
            self.show()

    def reload_pet(self):
        """重新加载宠物（更换宠物后调用）"""
        # 清理旧的宠物 widget，但不改变 visible 状态
        if self.pet_image and self.pet_image in self.children:
            self.remove_widget(self.pet_image)
        if self.anim_clock:
            self.anim_clock.cancel()
        self._dismiss_action_menu()
        self._dismiss_speech_bubble()
        self.pet_image = None
        self.anim_clock = None
        self.pet_id = None
        self.pet_def = None
        self.frames = []
        self.current_frame_idx = 0
        self._init_pet()

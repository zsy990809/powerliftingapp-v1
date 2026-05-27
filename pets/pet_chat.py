"""
聊天系统：漫画云朵气泡 + 全屏聊天对话框
"""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard


def _T():
    return MDApp.get_running_app().theme


class SpeechBubble(FloatLayout):
    """
    漫画风格云朵状对话气泡 — 在宠物旁显示
    使用 MDCard + MDLabel 实现，比 Canvas 绘制更简单
    """

    def __init__(self, text, bubble_width=dp(160), **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (bubble_width, dp(60))
        self._auto_dismiss = None

        # 气泡卡片
        card = MDCard(
            orientation="vertical",
            size_hint=(1, 1),
            padding=[dp(10), dp(8)],
            md_bg_color=(1, 1, 1, 0.92),
            radius=[dp(12), dp(12), dp(12), dp(4)],
            elevation=2,
        )
        label = MDLabel(
            text=text,
            font_style="Body2",
            halign="center",
            valign="middle",
            font_size=dp(13),
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),
            markup=True,
        )
        label.bind(size=label.setter("text_size"))
        card.add_widget(label)

        # 小三角尾巴（用圆点模拟）
        tail = MDCard(
            size_hint=(None, None), size=(dp(10), dp(10)),
            md_bg_color=(1, 1, 1, 0.92),
            radius=[dp(5)],
            pos_hint={"x": 0.15, "y": 0},
            elevation=2,
        )
        self.add_widget(card)
        self.add_widget(tail)

        # 根据文字长度调整高度
        from kivy.core.text import Label as CoreLabel
        cl = CoreLabel(text=text, font_size=dp(13), text_size=(bubble_width - dp(20), None))
        cl.refresh()
        th = max(cl.texture.height if cl.texture else dp(30), dp(30)) + dp(20)
        self.size = (bubble_width, min(th + dp(8), dp(200)))

        # 自动消失
        self._auto_dismiss = Clock.schedule_once(lambda dt: self._fade_out(), 5)

    def _fade_out(self):
        anim = Animation(opacity=0, duration=0.5)
        anim.bind(on_complete=lambda *a: self._remove_self())
        anim.start(self)

    def _remove_self(self):
        if self.parent:
            self.parent.remove_widget(self)

    def cancel_auto_dismiss(self):
        if self._auto_dismiss:
            self._auto_dismiss.cancel()


class ChatDialog:
    """
    全屏聊天对话框（接入 AI）
    管理 MDDialog，包含消息列表 + 输入框
    """

    def __init__(self, pet_id, api_key, plan_context=""):
        self.pet_id = pet_id
        self.api_key = api_key
        self.plan_context = plan_context
        self.dialog = None
        self.messages = [{"role": "user", "content": "你好！今天练什么？"}]
        self._build()

    def _build(self):
        theme = _T()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=[dp(4), dp(4)],
            size_hint_y=None,
            height=dp(380),
        )

        # 消息滚动区
        scroll = ScrollView(size_hint=(1, 1))
        self.msg_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=[dp(8), dp(4)],
            size_hint_y=None,
        )
        self.msg_box.bind(minimum_height=self.msg_box.setter("height"))
        scroll.add_widget(self.msg_box)
        content.add_widget(scroll)

        # 输入区（中文输入法下 on_text_validate 被 IME 拦截，用键盘事件代替）
        input_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(4),
        )
        self.input_field = MDTextField(
            hint_text="输入消息...",
            mode="fill",
            size_hint_x=0.75,
            font_size=dp(14),
            multiline=False,
            write_tab=False,
        )
        input_row.add_widget(self.input_field)

        send_btn = MDRaisedButton(
            text="发送",
            size_hint_x=0.25,
            md_bg_color=theme["primary"],
            on_release=self._send,
        )
        input_row.add_widget(send_btn)
        content.add_widget(input_row)

        # 提示文字
        from kivymd.uix.label import MDLabel as HintLabel
        hint = HintLabel(
            text="💡 中文输入请点击右侧「发送」按钮",
            font_style="Caption",
            halign="center",
            size_hint_y=None, height=dp(18),
            theme_text_color="Custom",
            text_color=theme["text_sec"],
        )
        content.add_widget(hint)

        # 全局键盘监听：处理 Enter 键（绕过 IME 对 on_text_validate 的拦截）
        self._keyboard_handler = None
        def _on_key_down(_win, _key, scancode, _text, _modifiers):
            if scancode == 40:  # Enter key
                self._send()
                return True
            return False
        self._keyboard_handler = Window.bind(on_key_down=_on_key_down)

        self.dialog = MDDialog(
            title=f"💪 和宠物聊天",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda b: self._close(),
                ),
            ],
        )
        self.dialog.open()
        self._is_open = True
        Clock.schedule_once(lambda dt: self._add_message("assistant", "叶家兴旺，猩猩有责！💪 有啥训练问题尽管问！"), 0.2)

    def _close(self):
        """关闭对话框，清理资源"""
        self._is_open = False
        if self._keyboard_handler:
            Window.unbind(on_key_down=self._keyboard_handler)
            self._keyboard_handler = None
        if self.dialog:
            self.dialog.dismiss()

    def _add_message(self, role, text):
        theme = _T()
        align = "right" if role == "user" else "left"
        bg = (*theme["primary"][:3], 0.15) if role == "user" else (0.2, 0.2, 0.2, 0.15)

        card = MDCard(
            orientation="horizontal",
            size_hint=(0.85, None),
            padding=[dp(8), dp(6)],
            md_bg_color=bg,
            radius=[dp(8)],
            spacing=dp(4),
        )
        label = MDLabel(
            text=text,
            font_style="Body2",
            size_hint_y=None,
            text_size=(self.msg_box.width * 0.75 or dp(240), None),
            halign=align,
            markup=True,
            theme_text_color="Custom",
            text_color=theme["text"],
        )
        label.bind(
            texture_size=lambda inst, val: setattr(label, "height", max(val[1], dp(20)))
        )
        card.add_widget(label)

        # 对齐
        card.size_hint_x = 0.85
        if role == "user":
            card.pos_hint = {"right": 1}

        self.msg_box.add_widget(card)
        Clock.schedule_once(lambda dt: self._scroll_bottom(), 0.1)

    def _scroll_bottom(self):
        """滚动到底部"""
        if self.msg_box.parent:
            scroll = self.msg_box.parent
            if hasattr(scroll, "scroll_y"):
                scroll.scroll_y = 0

    def _send(self, *args):
        text = self.input_field.text.strip()
        if not text:
            return

        self._add_message("user", text)
        self.input_field.text = ""
        self.messages.append({"role": "user", "content": text})
        self.input_field.disabled = True

        # 后台线程调用 API，避免阻塞 UI 导致闪退
        import threading
        threading.Thread(target=self._do_api_call, daemon=True).start()

    def _do_api_call(self):
        """在后台线程执行 API 请求"""
        try:
            from pets.ai_chat import chat_with_deepseek
            result = chat_with_deepseek(self.api_key, self.messages, self.plan_context)
        except Exception as e:
            result = {"success": False, "error": f"导入错误: {str(e)[:100]}"}

        # 回到主线程更新 UI
        Clock.schedule_once(lambda dt: self._handle_result(result), 0)

    def _handle_result(self, result):
        """处理 API 返回结果（主线程）"""
        # 对话框可能已被关闭
        if not self._is_open:
            return
        self.input_field.disabled = False
        if result["success"]:
            reply = result["reply"]
        else:
            reply = f"⚠️ {result.get('error', '出错了')}"

        self.messages.append({"role": "assistant", "content": reply})
        self._add_message("assistant", reply)

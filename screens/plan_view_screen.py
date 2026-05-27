# 训练计划视图 Screen — 核心页面

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem

from core.data import JAMAL_WEEKS, get_week_data, load_pr, save_records, load_records
from core.logic import calc_wt

import json
from datetime import date
from time import time


class PlanViewScreen(Screen):
    """训练计划详细视图 — 按日显示训练内容"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "plan_view"
        self.current_program = None
        self.current_week = 1
        self.current_day = 1
        self.custom_weights = {}  # {(week, day, idx): weight}
        self.dropdown_selections = {}  # {(week, day, idx): selected_name}
        self.check_states = {}  # {(week, day, idx): bool}
        self.pr_data = load_pr()
        self.dialog = None
        self.build_ui()

    def build_ui(self):
        """构建界面"""
        # 根布局
        self.root_layout = MDBoxLayout(orientation="vertical", spacing=dp(2))

        # ── 顶部信息栏 ──
        self._build_header()

        # ── 周/天选择栏 ──
        self._build_selector()

        # ── 保存按钮 ──
        self.save_btn = MDRaisedButton(
            text="完成今日训练",
            font_size=dp(14),
            md_bg_color=(0.18, 0.42, 0.31, 1),
            size_hint_y=None,
            height=dp(40),
            on_release=lambda btn: self._save_today(),
        )
        self.root_layout.add_widget(self.save_btn)

        # ── 训练内容滚动区域 ──
        self.scroll = ScrollView()
        self.content_grid = GridLayout(
            cols=1,
            spacing=dp(6),
            size_hint_y=None,
            padding=[dp(8), dp(4), dp(8), dp(8)],
        )
        self.content_grid.bind(minimum_height=self.content_grid.setter("height"))
        self.scroll.add_widget(self.content_grid)
        self.root_layout.add_widget(self.scroll)

        # ── 底部返回按钮 ──
        bottom_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10),
            padding=[dp(15), 0, dp(15), dp(5)],
        )
        back_plan = MDFlatButton(
            text="返回计划列表",
            font_size=dp(12),
            on_release=lambda b: self._go_to("plan_menu"),
        )
        back_menu = MDFlatButton(
            text="返回主菜单",
            font_size=dp(12),
            on_release=lambda b: self._go_to("menu"),
        )
        bottom_bar.add_widget(back_plan)
        bottom_bar.add_widget(back_menu)
        self.root_layout.add_widget(bottom_bar)

        self.add_widget(self.root_layout)

    def _build_header(self):
        """顶部标题 + PR 信息"""
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=[dp(15), dp(5)],
            spacing=dp(2),
        )
        title = MDLabel(
            text="Jamal 百分比计划",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            bold=True,
        )
        header.add_widget(title)

        # PR 显示的文本
        pr = self.pr_data
        pr_text = (
            f"深蹲 {pr.get('深蹲',230)}kg | 卧推 {pr.get('卧推',140)}kg | "
            f"硬拉 {pr.get('硬拉',190)}kg"
        )
        if pr.get("木板卧推") or pr.get("前蹲") or pr.get("暂停硬拉"):
            pr_text += (
                f"\n木板卧推 {pr.get('木板卧推',150)}kg | "
                f"前蹲 {pr.get('前蹲',185)}kg | "
                f"暂停硬拉 {pr.get('暂停硬拉',180)}kg"
            )
        self.pr_label = MDLabel(
            text=pr_text,
            font_style="Caption",
            halign="center",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Hint",
        )
        header.add_widget(self.pr_label)
        self.root_layout.add_widget(header)

    def _build_selector(self):
        """周/天选择器（根据当前周动态显示天数按钮）"""
        sel = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8),
            padding=[dp(10), 0, dp(10), 0],
        )

        # 周选择：用下拉菜单按钮
        self.week_btn = MDRaisedButton(
            text=f"第 {self.current_week} 周",
            font_size=dp(13),
            md_bg_color=(0.06, 0.20, 0.38, 1),
            size_hint_x=0.4,
            on_release=lambda b: self._show_week_menu(),
        )
        sel.add_widget(self.week_btn)

        # 天选择：根据当前周的实际天数动态生成按钮
        self.day_box = MDBoxLayout(spacing=dp(4), size_hint_x=0.6)
        self._rebuild_day_buttons()
        sel.add_widget(self.day_box)

        self.root_layout.add_widget(sel)
        self._update_day_buttons()

    def _rebuild_day_buttons(self):
        """根据当前周的实际天数重建天按钮"""
        self.day_box.clear_widgets()
        self.day_btns = []
        week_data = JAMAL_WEEKS.get(self.current_week, JAMAL_WEEKS[1])
        day_keys = sorted(week_data.get("days", {1:[]}).keys())
        # 如果当前选择的天不在实际天数中，重置为第1天
        if self.current_day not in day_keys:
            self.current_day = day_keys[0] if day_keys else 1
        for d in day_keys:
            label = f"D{d}"
            # 如果是测试日（1RM TEST），显示为 TEST
            btn = MDFlatButton(
                text=label,
                font_size=dp(12),
                md_bg_color=(0.2, 0.2, 0.2, 0.3),
                on_release=lambda b, day=d: self._select_day(day),
            )
            self.day_btns.append(btn)
            self.day_box.add_widget(btn)

    def _show_week_menu(self):
        """弹出周选择菜单（只显示实际存在的周）"""
        week_items = [
            {
                "text": f"第 {i} 周 - {JAMAL_WEEKS[i]['label']}",
                "on_release": lambda w=i: self._select_week(w),
            }
            for i in sorted(JAMAL_WEEKS.keys())
        ]
        self.week_menu = MDDropdownMenu(
            caller=self.week_btn,
            items=week_items,
            width_mult=6,
            max_height=dp(300),
        )
        self.week_menu.open()

    def _select_week(self, week):
        """选择周（重建天按钮）"""
        self.current_week = week
        self.current_day = 1
        self.week_btn.text = f"第 {week} 周"
        if hasattr(self, "week_menu"):
            self.week_menu.dismiss()
        self._rebuild_day_buttons()
        self._update_day_buttons()
        self._refresh_content()

    def _select_day(self, day):
        """选择天"""
        self.current_day = day
        self._update_day_buttons()
        self._refresh_content()

    def _update_day_buttons(self):
        """更新天按钮的高亮状态"""
        for i, btn in enumerate(self.day_btns):
            if i + 1 == self.current_day:
                btn.md_bg_color = (0.91, 0.27, 0.38, 0.8)
                btn.text_color = (1, 1, 1, 1)
            else:
                btn.md_bg_color = (0.2, 0.2, 0.2, 0.3)
                btn.text_color = (0.7, 0.7, 0.7, 1)

    # ─────────────────────────────────────────────
    #  内容渲染
    # ─────────────────────────────────────────────

    def set_program(self, program):
        """设置当前查看的计划"""
        self.current_program = program
        self.current_week = 1
        self.current_day = 1
        self.pr_data = load_pr()
        self._rebuild_day_buttons()
        self._update_day_buttons()
        self._refresh_content()

    def _refresh_content(self):
        """刷新训练内容"""
        self.content_grid.clear_widgets()

        # 非模板周：继承模板周的 dropdown 选择
        TEMPLATE_GROUPS = {
            1: [2, 3, 4, 5, 6],
            7: [8, 9, 10, 11],
        }
        for template_week, follow_weeks in TEMPLATE_GROUPS.items():
            if self.current_week in follow_weeks:
                # 把模板周的所有 dropdown_selections 复制到当前周
                for (tw, td, ti), val in list(self.dropdown_selections.items()):
                    if tw == template_week:
                        follow_key = (self.current_week, td, ti)
                        if follow_key not in self.dropdown_selections:
                            self.dropdown_selections[follow_key] = val

        week_data = JAMAL_WEEKS.get(self.current_week)
        if not week_data:
            self.content_grid.add_widget(
                MDLabel(text="暂无训练数据", halign="center")
            )
            return

        day_exercises = week_data["days"].get(self.current_day, [])
        if not day_exercises:
            self.content_grid.add_widget(
                MDLabel(text="当天暂无训练", halign="center")
            )
            return

        # 周/日标题
        title = MDLabel(
            text=f"{week_data['label']} | DAY {self.current_day}",
            font_style="Subtitle1",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            bold=True,
            theme_text_color="Primary",
        )
        self.content_grid.add_widget(title)

        # 表头
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(24),
            padding=[dp(4), 0],
        )
        for txt, w in [
            ("动作", 0.38),
            ("组", 0.1),
            ("次", 0.1),
            ("重量", 0.18),
            ("RPE", 0.1),
            ("", 0.14),
        ]:
            lbl = MDLabel(
                text=txt,
                font_style="Overline",
                size_hint_x=w,
                halign="center" if txt and len(txt) <= 2 else "left",
                theme_text_color="Secondary",
            )
            header.add_widget(lbl)
        self.content_grid.add_widget(header)

        # 按组分隔 + 动作卡片
        current_group = None
        for idx, ex in enumerate(day_exercises):
            group = ex.get("group", "")
            if group != current_group:
                current_group = group
                group_lbl = MDLabel(
                    text=f"  {group}",
                    font_style="Subtitle2",
                    size_hint_y=None,
                    height=dp(28),
                    bold=True,
                    theme_text_color="Error",
                )
                self.content_grid.add_widget(group_lbl)

            self._add_exercise_card(idx, ex)

    def _add_exercise_card(self, idx, ex):
        """添加一个训练动作卡片"""
        name0 = ex.get("name", "Unnamed")
        pct0 = ex.get("pct", 0)
        sets0 = ex.get("sets", "-")
        reps0 = ex.get("reps", "-")
        rpe0 = ex.get("rpe", "-")
        has_dropdown = ex.get("dropdown", False)
        # 只有模板周（W1/W7/W12）才显示 dropdown 选项
        TEMPLATE_WEEKS = {1, 7, 12}
        if self.current_week not in TEMPLATE_WEEKS:
            has_dropdown = False
        options0 = ex.get("options", [])
        is_aux = ex.get("group") == "辅助"

        key = (self.current_week, self.current_day, idx)

        # 是否已选中下拉选项
        if key in self.dropdown_selections:
            display_name = self.dropdown_selections[key]
            wgt = calc_wt(self.pr_data, display_name, pct0)
        else:
            display_name = name0.replace("（下拉可选）", "").replace("（退让组）", "")
            wgt = calc_wt(self.pr_data, name0, pct0)

        # 自定义重量覆盖
        if key in self.custom_weights:
            wt_text = f"{self.custom_weights[key]}kg"
        elif wgt == 0 and is_aux:
            wt_text = "自选"
        elif wgt != "-":
            wt_text = f"{round(wgt)}"
        else:
            wt_text = "自选" if is_aux else "-"

        # 卡片
        card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
            padding=[dp(6), dp(2)],
            spacing=dp(2),
            radius=[dp(6)],
            md_bg_color=(0.12, 0.12, 0.18, 0.6),
        )

        # 动作名
        name_lbl = MDLabel(
            text=display_name,
            font_style="Body2",
            size_hint_x=0.30,
            halign="left",
            theme_text_color="Custom",
            text_color=(0.9, 0.9, 0.9, 1),
        )
        if has_dropdown and options0:
            name_lbl.theme_text_color = "Primary"
            name_lbl.bold = True
        card.add_widget(name_lbl)

        # 组数
        card.add_widget(
            MDLabel(
                text=str(sets0) if sets0 else "-",
                font_style="Body2",
                size_hint_x=0.1,
                halign="center",
            )
        )
        # 次数
        card.add_widget(
            MDLabel(
                text=str(reps0),
                font_style="Body2",
                size_hint_x=0.1,
                halign="center",
            )
        )
        # 重量（辅助动作显示可点击按钮）
        from kivymd.uix.button import MDFlatButton
        
        if is_aux:
            wt_btn = MDFlatButton(
                text=wt_text,
                font_size=dp(12),
                size_hint_x=0.18,
                md_bg_color=(0.15, 0.4, 0.35, 0.3),
                on_release=lambda b, k=key: self._show_weight_dialog(k),
            )
            card.add_widget(wt_btn)
        else:
            card.add_widget(
                MDLabel(
                    text=wt_text,
                    font_style="Body2",
                    size_hint_x=0.18,
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.9, 0.9, 1),
                )
            )

        # RPE
        card.add_widget(
            MDLabel(
                text=str(rpe0) if rpe0 and str(rpe0).strip() else "-",
                font_style="Body2",
                size_hint_x=0.1,
                halign="center",
            )
        )
        # 更换动作按钮（仅带dropdown的辅助动作显示）
        if has_dropdown and options0:
            change_btn = MDFlatButton(
                text="更换",
                font_size=dp(10),
                size_hint_x=0.14,
                md_bg_color=(0.06, 0.2, 0.38, 0.3),
                on_release=lambda b, k=key, opts=options0: self._show_exercise_menu(k, opts),
            )
            card.add_widget(change_btn)
        else:
            card.add_widget(MDLabel(size_hint_x=0.14))

        self.content_grid.add_widget(card)

    # ─────────────────────────────────────────────
    #  交互功能
    # ─────────────────────────────────────────────

    def _show_exercise_menu(self, key, options):
        """下拉可选动作 — 弹出选项菜单"""
        if not options:
            return
        items = [
            {
                "text": opt,
                "on_release": lambda o=opt: self._select_exercise(key, o),
            }
            for opt in options
        ]
        self.ex_menu = MDDropdownMenu(
            caller=self.content_grid,
            items=items,
            width_mult=4,
            max_height=dp(300),
        )
        self.ex_menu.open()

    def _select_exercise(self, key, selected_name):
        """选择替换动作 - 同步到联动周"""
        self.dropdown_selections[key] = selected_name
        
        # 跨周联动：模板周的选择同步到跟随周
        week, day, idx = key
        TEMPLATE_GROUPS = {
            1: [2, 3, 4, 5, 6],
            7: [8, 9, 10, 11],
        }
        if week in TEMPLATE_GROUPS:
            for follow_week in TEMPLATE_GROUPS[week]:
                follow_key = (follow_week, day, idx)
                self.dropdown_selections[follow_key] = selected_name
        
        if hasattr(self, "ex_menu"):
            self.ex_menu.dismiss()
        self._refresh_content()

    def _show_weight_dialog(self, key):
        """辅助动作自定义重量弹窗"""
        if self.dialog:
            self.dialog.dismiss()

        # 当前值
        current = self.custom_weights.get(key, "")

        # 输入框
        input_field = MDTextField(
            text=str(current) if current else "",
            hint_text="输入重量 (kg)",
            input_filter="int",
            mode="fill",
            size_hint_x=0.8,
        )

        self.dialog = MDDialog(
            title="自定义重量",
            type="custom",
            content_cls=MDBoxLayout(
                MDLabel(text="辅助动作，请输入您要使用的重量：", font_style="Body2"),
                input_field,
                orientation="vertical",
                spacing=dp(10),
                padding=dp(10),
                size_hint_y=None,
                height=dp(120),
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda b: self.dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="确定",
                    on_release=lambda b: self._set_custom_weight(key, input_field.text),
                ),
            ],
        )
        self.dialog.open()

    def _set_custom_weight(self, key, value):
        """设置自定义重量"""
        if value and value.strip():
            try:
                self.custom_weights[key] = int(value.strip())
            except ValueError:
                pass
        if self.dialog:
            self.dialog.dismiss()
        self._refresh_content()

    def _save_today(self):
        """保存今日训练记录"""
        week_data = JAMAL_WEEKS.get(self.current_week)
        if not week_data:
            return

        day_exercises = week_data["days"].get(self.current_day, [])
        exercises_saved = []

        for idx, ex in enumerate(day_exercises):
            key = (self.current_week, self.current_day, idx)
            name0 = ex.get("name", "Unnamed")
            display_name = self.dropdown_selections.get(key, name0)
            pct0 = ex.get("pct", 0)

            if key in self.custom_weights:
                wt = self.custom_weights[key]
            else:
                wgt = calc_wt(self.pr_data, display_name, pct0)
                wt = round(wgt) if wgt != "-" else 0

            exercises_saved.append({
                "name": display_name,
                "sets": ex.get("sets", "-"),
                "reps": ex.get("reps", "-"),
                "weight": wt,
                "rpe": ex.get("rpe", "-"),
                "group": ex.get("group", ""),
            })

        record = {
            "id": f"{date.today().isoformat()}_{int(time() * 1000) % 100000}",
            "date": date.today().isoformat(),
            "week": self.current_week,
            "day": self.current_day,
            "program": self.current_program or "jamal",
            "week_label": week_data.get("label", f"第{self.current_week}周"),
            "day_label": f"DAY {self.current_day}",
            "exercises": exercises_saved,
        }

        # 使用平铺结构保存，每次训练单独一条记录，永不覆盖
        records = load_records()
        if "records" not in records:
            # 兼容旧格式：如有旧数据则迁移
            if "rounds" in records:
                old = records
                records = {"records": []}
                for r in old.get("rounds", []):
                    for wk, days in r.get("weeks", {}).items():
                        for dy, entries in days.items():
                            if not isinstance(entries, list):
                                entries = [entries]
                            for e in entries:
                                e["week"] = int(wk) if str(wk).isdigit() else wk
                                e["day"] = int(dy) if str(dy).isdigit() else dy
                                records["records"].append(e)
            else:
                records = {"records": []}

        records["records"].append(record)
        save_records(records)

        # 保存成功提示
        self._show_toast("今日训练已保存！")

    def _show_toast(self, msg):
        """显示提示"""
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            text=msg,
            buttons=[
                MDRaisedButton(
                    text="好",
                    on_release=lambda b: self.dialog.dismiss(),
                )
            ],
        )
        self.dialog.open()

    def _go_to(self, target):
        """切换到其他页面"""
        self.manager.current = target

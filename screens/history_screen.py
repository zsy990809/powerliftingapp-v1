# 训练历史 Screen — 平铺记录，可展开/编辑/删除

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from core.data import load_records, save_records


class HistoryScreen(Screen):
    """训练历史记录 — 平铺列表，每条可展开/编辑/删除"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "history"
        self.expand_states = {}  # {record_id: bool}
        self.dialog = None
        self.build_ui()

    def build_ui(self):
        self.root_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))

        # 标题
        header = MDBoxLayout(
            orientation="vertical", size_hint_y=None, height=dp(70),
            padding=[dp(15), dp(10)],
        )
        header.add_widget(
            MDLabel(text="训练记录", font_style="H4", halign="center",
                    size_hint_y=None, height=dp(40), bold=True)
        )
        self.info_label = MDLabel(
            text="", font_style="Caption", halign="center",
            size_hint_y=None, height=dp(20), theme_text_color="Hint",
        )
        header.add_widget(self.info_label)
        self.root_layout.add_widget(header)

        # 滚动列表
        self.scroll = ScrollView()
        self.content = GridLayout(
            cols=1, spacing=dp(6), size_hint_y=None,
            padding=[dp(8), 0, dp(8), dp(8)],
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.root_layout.add_widget(self.scroll)

        # 底部返回按钮
        back_box = MDBoxLayout(size_hint_y=None, height=dp(40), padding=[dp(15), 0])
        back_box.add_widget(
            MDFlatButton(text="返回主菜单", font_size=dp(14),
                         on_release=lambda b: self._go_back())
        )
        self.root_layout.add_widget(back_box)
        self.add_widget(self.root_layout)

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        """刷新列表"""
        self.content.clear_widgets()
        records = load_records()
        items = records.get("records", [])

        self.info_label.text = f"共 {len(items)} 条训练记录"

        if not items:
            self.content.add_widget(
                MDLabel(text="暂无训练记录\n快去训练吧！", font_style="Body1",
                        halign="center", size_hint_y=None, height=dp(100),
                        theme_text_color="Hint")
            )
            return

        # 按日期倒序排列
        sorted_items = sorted(items, key=lambda x: x.get("date", ""), reverse=True)

        for idx, item in enumerate(sorted_items):
            self._render_record(item, idx)

    # ── 单条记录渲染 ──

    def _render_record(self, record, idx):
        """渲染一条训练记录"""
        record_id = record.get("id") or record.get("date", "") + str(idx)
        expanded = self.expand_states.get(record_id, False)

        date_str = record.get("date", "未知日期")
        week_label = record.get("week_label", f"第{record.get('week', '?')}周")
        day_label = record.get("day_label", f"DAY {record.get('day', '?')}")
        exercises = record.get("exercises", [])

        # 计算卡片高度（必须显式设置，否则在 GridLayout 中高度为 0 → 内容重叠）
        header_h = dp(32)      # 顶栏高度
        pad_top = dp(8)        # padding top
        pad_bot = dp(8)        # padding bottom
        spacing_h = dp(4)      # 卡片 spacing
        if expanded and exercises:
            table_header_h = dp(22)
            row_h = len(exercises) * dp(24)
            card_height = header_h + pad_top + pad_bot + spacing_h + table_header_h + row_h
        else:
            card_height = header_h + pad_top + pad_bot

        card = MDCard(
            orientation="vertical", size_hint_y=None, height=card_height,
            padding=[dp(10), dp(8)], spacing=dp(4),
            radius=[dp(8)], md_bg_color=(0.06, 0.20, 0.38, 0.8),
        )

        # ── 顶栏：日期 + 周/天 + 操作按钮 ──
        top = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                          height=dp(32), spacing=dp(8))

        # 展开图标
        icon = "chevron-down" if expanded else "chevron-right"
        top.add_widget(MDIcon(
            icon=icon, font_size=dp(20), size_hint_x=0.06,
            theme_text_color="Custom", text_color=(1, 1, 1, 0.8),
        ))

        # 标题文字
        top.add_widget(MDLabel(
            text=f"[b]{date_str}[/b]  {week_label}  {day_label}",
            font_style="Body2", size_hint_x=0.6, markup=True,
        ))

        # 操作按钮
        btn_box = MDBoxLayout(size_hint_x=0.3, spacing=dp(2))
        btn_box.add_widget(MDIconButton(
            icon="pencil", font_size=dp(16),
            theme_text_color="Custom", text_color=(0.3, 0.8, 0.6, 1),
            on_release=lambda b, r=record, ri=record_id: self._edit_record(r),
        ))
        btn_box.add_widget(MDIconButton(
            icon="delete", font_size=dp(16),
            theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1),
            on_release=lambda b, r=record, ri=record_id: self._confirm_delete(ri, record),
        ))
        top.add_widget(btn_box)
        card.add_widget(top)

        # ── 展开区：训练动作明细 ──
        if expanded:
            if exercises:
                # 表头
                hdr = MDBoxLayout(
                    orientation="horizontal", size_hint_y=None, height=dp(22),
                    padding=[dp(16), 0, dp(8), 0],
                )
                hdr.add_widget(MDLabel(
                    text="动作", font_style="Overline", size_hint_x=0.4,
                    bold=True, theme_text_color="Primary",
                ))
                hdr.add_widget(MDLabel(
                    text="组×次", font_style="Overline", size_hint_x=0.2,
                    halign="center", bold=True, theme_text_color="Primary",
                ))
                hdr.add_widget(MDLabel(
                    text="重量", font_style="Overline", size_hint_x=0.2,
                    halign="center", bold=True, theme_text_color="Primary",
                ))
                hdr.add_widget(MDLabel(
                    text="RPE", font_style="Overline", size_hint_x=0.2,
                    halign="center", bold=True, theme_text_color="Primary",
                ))
                card.add_widget(hdr)

                for ei, ex in enumerate(exercises):
                    bg = (0.1, 0.15, 0.25, 0.3) if ei % 2 == 0 else (0, 0, 0, 0)
                    ex_box = MDBoxLayout(
                        orientation="horizontal", size_hint_y=None, height=dp(24),
                        padding=[dp(16), 0, dp(8), 0], md_bg_color=bg,
                    )
                    name = ex.get("name", "")
                    sets = ex.get("sets", "-")
                    reps = ex.get("reps", "-")
                    weight = ex.get("weight", "-")
                    rpe = ex.get("rpe", "-")
                    # 去掉名称里的分类前缀（如下拉可选）
                    display_name = name.split("（")[0] if "（" in name else name
                    ex_box.add_widget(MDLabel(
                        text=display_name, font_style="Caption", size_hint_x=0.4,
                    ))
                    ex_box.add_widget(MDLabel(
                        text=f"{sets}×{reps}", font_style="Caption",
                        size_hint_x=0.2, halign="center",
                    ))
                    ex_box.add_widget(MDLabel(
                        text=f"{weight} kg" if weight else "-",
                        font_style="Caption", size_hint_x=0.2, halign="center",
                    ))
                    ex_box.add_widget(MDLabel(
                        text=str(rpe) if rpe and rpe != "-" else "-",
                        font_style="Caption", size_hint_x=0.2, halign="center",
                    ))
                    card.add_widget(ex_box)
            else:
                card.add_widget(MDLabel(
                    text="无动作数据", font_style="Caption",
                    halign="center", theme_text_color="Hint",
                    size_hint_y=None, height=dp(24),
                ))

        # 整卡可点击展开/收起
        card.on_release = lambda rid=record_id: self._toggle_expand(rid)
        self.content.add_widget(card)

    # ── 交互 ──

    _debounce_timer = None

    def _toggle_expand(self, record_id):
        """展开/收起切换"""
        if self._debounce_timer:
            self._debounce_timer.cancel()
        self._debounce_timer = Clock.schedule_once(
            lambda dt: self._do_toggle(record_id), 0.15
        )

    def _do_toggle(self, record_id):
        was = self.expand_states.get(record_id, False)
        self.expand_states[record_id] = not was
        self.refresh()

    # ── 编辑 ──

    def _edit_record(self, record):
        """编辑训练记录：弹窗显示每个动作的可改重量"""
        exercises = record.get("exercises", [])
        if not exercises:
            return

        inputs = []
        content_box = MDBoxLayout(
            orientation="vertical", spacing=dp(8),
            padding=dp(10), size_hint_y=None,
        )
        # 计算弹窗高度
        total_h = min(len(exercises) * 60 + 20, dp(400))
        content_box.height = total_h
        scroll = ScrollView(size_hint_y=None, height=total_h)

        for ei, ex in enumerate(exercises):
            row = MDBoxLayout(
                orientation="horizontal", size_hint_y=None, height=dp(50),
                spacing=dp(8), padding=[0, 0, 0, dp(4)],
            )
            name_label = MDLabel(
                text=ex.get("name", "").split("（")[0],
                font_style="Caption", size_hint_x=0.4,
                halign="left", valign="middle",
            )
            name_label.bind(size=name_label.setter("text_size"))
            row.add_widget(name_label)

            inp = MDTextField(
                text=str(ex.get("weight", "")),
                hint_text="重量 kg", mode="fill",
                size_hint_x=0.3, font_size=dp(14),
            )
            row.add_widget(inp)
            inputs.append(inp)

            row.add_widget(MDLabel(
                text="kg", font_style="Caption", size_hint_x=0.1,
                halign="left", valign="middle",
            ))
            content_box.add_widget(row)

        scroll.add_widget(content_box)

        self.dialog = MDDialog(
            title="编辑训练重量",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDFlatButton(text="取消", on_release=lambda b: self.dialog.dismiss()),
                MDRaisedButton(
                    text="保存",
                    on_release=lambda b: self._save_edit(record, inputs),
                ),
            ],
        )
        self.dialog.open()

    def _save_edit(self, record, inputs):
        """保存编辑后的重量"""
        exercises = record.get("exercises", [])
        for i, inp in enumerate(inputs):
            if i < len(exercises):
                val = inp.text.strip()
                try:
                    exercises[i]["weight"] = int(val) if val else 0
                except ValueError:
                    pass

        # 按 id 更新记录
        records = load_records()
        for r in records.get("records", []):
            if r.get("id") == record.get("id"):
                r["exercises"] = exercises
                r["date"] = record.get("date", "")
                break
        else:
            # 没有 id 时按位置匹配
            for i, r in enumerate(records.get("records", [])):
                if r.get("date") == record.get("date") and \
                   r.get("week") == record.get("week") and \
                   r.get("day") == record.get("day"):
                    records["records"][i]["exercises"] = exercises
                    break
        save_records(records)

        if self.dialog:
            self.dialog.dismiss()
        self.refresh()

    # ── 删除 ──

    def _confirm_delete(self, record_id, record):
        self.dialog = MDDialog(
            title="确认删除",
            text=f"确定要删除 {record.get('date','')} 的训练记录吗？",
            buttons=[
                MDFlatButton(text="取消", on_release=lambda b: self.dialog.dismiss()),
                MDRaisedButton(
                    text="删除", md_bg_color=(0.8, 0.1, 0.1, 1),
                    on_release=lambda b: self._do_delete(record_id, record),
                ),
            ],
        )
        self.dialog.open()

    def _do_delete(self, record_id, record):
        if self.dialog:
            self.dialog.dismiss()
        records = load_records()
        items = records.get("records", [])
        # 用 id 匹配，没有 id 则按索引匹配
        if record.get("id"):
            records["records"] = [r for r in items if r.get("id") != record["id"]]
        else:
            # 按内容匹配
            items.pop(items.index(record))
        save_records(records)
        # 清除展开状态
        self.expand_states.pop(record_id, None)
        self.refresh()

    # ── 返回 ──

    def _go_back(self):
        self.manager.current = "menu"

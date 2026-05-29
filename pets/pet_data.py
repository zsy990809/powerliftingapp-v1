"""
宠物数据定义 + 本地配置管理
"""

import os
import json

# ── 宠物定义 ──
PETS = {
    "菠又亮": {
        "id": "菠又亮",
        "name": "菠又亮",
        "dir": "菠又亮",
        "frame_count": 30,
        "frame_pattern": "frame_{i:02d}.png",
        "static": "static.png",
        "fps": 10,
        "size": (0.16, 0.18),
        "no_api_phrases": [
            "菠头在膨胀",
            "对他使用菠萝头吧",
        ],
        "description": "闪耀の健身之星",
        "color": (0.95, 0.75, 0.05, 1),  # 金色
    },
    "鹤哥": {
        "id": "鹤哥",
        "name": "鹤哥",
        "dir": "鹤哥",
        "frame_count": 30,
        "frame_pattern": "frame_{i:02d}.png",
        "static": "static.png",
        "fps": 10,
        "size": (0.16, 0.18),
        "no_api_phrases": [
            "上了我的船，就是我鹤胡子的孩子了",
            "出了莱维，你叫我耿鹤。到了莱维，你叫我什么？",
        ],
        "description": "仙鹤流格斗术传人",
        "color": (0.0, 0.55, 0.55, 1),  # 青绿
    },
    "六道东树": {
        "id": "六道东树",
        "name": "六道东树",
        "dir": "六道东树",
        "frame_count": 30,
        "frame_pattern": "frame_{i:02d}.png",
        "static": "static.png",
        "fps": 10,
        "size": (0.16, 0.18),
        "no_api_phrases": [
            "自来也，我三天之内杀了你",
            "来做个罗汉果超级组",
        ],
        "description": "六道轮回の修行者",
        "color": (0.75, 0.0, 0.0, 1),  # 赤红
    },
    "禽宇": {
        "id": "禽宇",
        "name": "禽宇",
        "dir": "禽宇",
        "frame_count": 30,
        "frame_pattern": "frame_{i:02d}.png",
        "static": "static.png",
        "fps": 10,
        "size": (0.16, 0.18),
        "no_api_phrases": [
            "啾啾啾（歪头歪嘴吐舌头）",
            "博之我师，我吸博汁",
        ],
        "description": "禽宇の宇宙健身法",
        "color": (0.1, 0.25, 0.75, 1),  # 深蓝
    },
    "相扑恶魔": {
        "id": "相扑恶魔",
        "name": "相扑恶魔",
        "dir": "相扑恶魔",
        "frame_count": 30,
        "frame_pattern": "frame_{i:02d}.png",
        "static": "static.png",
        "fps": 10,
        "size": (0.16, 0.18),
        "no_api_phrases": [
            "200kg无套相扑硬拉",
            "谁是徐河弱？",
        ],
        "description": "相扑地狱の悪魔",
        "color": (0.45, 0.0, 0.45, 1),  # 深紫
    },
    "鹏·鹿丸": {
        "id": "鹏·鹿丸",
        "name": "鹏·鹿丸",
        "dir": "鹏·鹿丸",
        "frame_count": 30,
        "frame_pattern": "frame_{i:02d}.png",
        "static": "static.png",
        "fps": 10,
        "size": (0.16, 0.18),
        "no_api_phrases": [
            "油车省电",
            "电车省油",
            "我要去上课了",
            "我乃业绩之主",
        ],
        "description": "忍界健身の達人",
        "color": (0.15, 0.15, 0.35, 1),  # 忍蓝
    },
    "袋熊王·军": {
        "id": "袋熊王·军",
        "name": "袋熊王·军",
        "dir": "袋熊王·军",
        "frame_count": 30,
        "frame_pattern": "frame_{i:02d}.png",
        "static": "static.png",
        "fps": 10,
        "size": (0.16, 0.18),
        "no_api_phrases": [
            "我感觉腰椎突出了。",
            "深蹲把我腰蹲突了",
            "卧推把我腰推突了",
            "硬拉把我腰拉突了",
        ],
        "description": "袋熊王国の王者",
        "color": (0.6, 0.3, 0.1, 1),  # 袋棕
    },
}

# ── 本地配置管理 ──

CONFIG_FILE = None  # 在 init_pet_config 时设置


def init_pet_config(user_data_dir):
    global CONFIG_FILE
    CONFIG_FILE = os.path.join(user_data_dir, "pet_config.json")


def _get_config():
    if CONFIG_FILE and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _save_config(cfg):
    if CONFIG_FILE:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_selected_pet():
    cfg = _get_config()
    return cfg.get("selected_pet", None)


def set_selected_pet(pet_id):
    cfg = _get_config()
    cfg["selected_pet"] = pet_id
    _save_config(cfg)


def get_api_key():
    cfg = _get_config()
    return cfg.get("api_key", "")


def set_api_key(key):
    cfg = _get_config()
    cfg["api_key"] = key
    _save_config(cfg)


def get_pet_visible():
    cfg = _get_config()
    return cfg.get("visible", False)


def set_pet_visible(v):
    cfg = _get_config()
    cfg["visible"] = v
    _save_config(cfg)


def get_pet_position():
    cfg = _get_config()
    return cfg.get("pos_x", 0.8), cfg.get("pos_y", 0.1)


def set_pet_position(x, y):
    cfg = _get_config()
    cfg["pos_x"] = x
    cfg["pos_y"] = y
    _save_config(cfg)


def get_pet(pet_id):
    """获取宠物定义，如果不存在返回 None"""
    return PETS.get(pet_id, None)


def list_pets():
    """返回可用宠物 ID 列表"""
    return list(PETS.keys())

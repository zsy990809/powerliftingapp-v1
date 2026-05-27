# 力量举手机App - 计算函数
# 从桌面版 powerlifting_app.py 直接迁移

def calc_dots(bw, total):
    """DOTS = 总重量 × 500 / (−307.75076 + 24.0900756×bw − 0.1918759221×bw² + 0.0007391293×bw³ − 0.000001093×bw⁴)
    系数顺序：a=常数项, b=一次项, c=二次项, d=三次项, e=四次项 (男子系数)"""
    if bw <= 0 or total <= 0:
        return 0
    a, b, c, d, e = -307.75076, 24.0900756, -0.1918759221, 0.0007391293, -0.000001093
    coeff = a + b*bw + c*bw**2 + d*bw**3 + e*bw**4
    return round(total * 500 / coeff, 1) if coeff > 0 else 0


def calc_wt(pr_data, name, pct):
    """根据 PR 和百分比计算训练重量"""
    if pct == 0:
        return "-"
    name = name or ""
    # 优先匹配更具体的关键词
    priority = ["木板卧推", "暂停硬拉", "前蹲", "暂停深蹲", "深蹲", "卧推", "硬拉"]
    key = None
    for kw in priority:
        if kw in name:
            key = kw
            break

    # 如果仍未匹配，尝试匹配 pr_data 中的任意键
    if key is None:
        for k in pr_data.keys():
            if k in name:
                key = k
                break

    # 对包含"变式"的动作，尝试使用上下文推断更合理的默认
    if key is None and "变式" in name:
        if "卧推" in name:
            key = "卧推"
        elif "硬拉" in name:
            key = "硬拉"
        else:
            key = "前蹲" if pr_data.get("前蹲") else None

    if key is None:
        print(f"警告: 未能匹配动作 '{name}' 的 PR 键，使用深蹲作为默认值。")
        key = "深蹲"

    pr = pr_data.get(key, pr_data.get("深蹲", 230))
    try:
        return round(pr * pct)
    except Exception:
        print(f"警告: 计算重量失败 name={name} pct={pct} pr={pr}")
        return "-"


def get_round_label(round_num, program):
    return f"第{round_num}轮 - {program}"

"""
DeepSeek API 客户端
"""

import requests
import time

API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-flash"


def chat_with_deepseek(api_key, messages, plan_context=""):
    """
    调用 DeepSeek API（带自动重试）
    messages: [{"role": "user", "content": "..."}, ...]
    plan_context: 当前训练计划描述，注入到 system prompt
    """
    system_prompt = (
        "你是力量举训练助手的健身宠物，名叫叶家兴。"
        "你性格活泼幽默，爱说'叶家兴旺，猩猩有责'。"
        "你非常懂力量举训练，能回答关于深蹲、卧推、硬拉等技术问题，"
        "也能给训练建议和鼓励。回答简短有力，带点俏皮，用中文。"
    )
    if plan_context:
        system_prompt += f"\n\n用户当前训练计划信息：\n{plan_context}"

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "max_tokens": 500,
        "temperature": 0.8,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # 自动重试最多 2 次，应对偶发网络问题
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "")
                return {"success": True, "reply": content.strip()}
            else:
                return {
                    "success": False,
                    "error": f"API 请求失败 (HTTP {resp.status_code}): {resp.text[:200]}",
                }
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                time.sleep(1)
                continue
            return {"success": False, "error": "请求超时，请检查网络"}
        except requests.exceptions.ConnectionError:
            if attempt < max_retries:
                time.sleep(2)
                continue
            return {"success": False, "error": "网络连接失败，请检查网络"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)[:100]}"}

    return {"success": False, "error": "请求失败，请重试"}

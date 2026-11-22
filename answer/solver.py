"""AI 答案分析接口占位：未配置模型时绝不猜测答案。"""


def suggest_answer(question_text):
    if not question_text or not question_text.strip():
        raise ValueError("题目内容不能为空")
    return {
        "status": "not_configured",
        "answer": None,
        "explanation": "当前版本尚未接入 AI 模型。请先核对 OCR 识别出的题干，再人工判断。",
        "requires_user_confirmation": True,
    }

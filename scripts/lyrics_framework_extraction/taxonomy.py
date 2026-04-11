ALLOWED_SEMANTIC_ROLES = [
    "建立时间锚点",
    "建立场景",
    "铺垫状态",
    "深化状态",
    "局部收束",
    "情感转折",
    "抬升",
    "主题宣言",
    "Hook",
    "回返",
    "扩展确认",
    "收束",
    "过渡",
]


def to_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"

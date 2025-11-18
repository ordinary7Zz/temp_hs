import contextvars

# 1. 创建一个上下文变量，用于存储用户信息
current_user = contextvars.ContextVar('current_user', default=None)

# 2. 定义两个辅助函数，方便设置和获取
def set_user(user_id: int, user_name: str):
    """设置当前用户的信息"""
    current_user.set({"UID": user_id, "UserName": user_name})

def get_user() -> dict | None:
    """获取当前用户的信息，如果没有则返回 None"""
    return current_user.get()
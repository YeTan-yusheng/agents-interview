class DuplicateUsernameError(Exception):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"用户名{username}已存在")


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("用户名或密码错误")


class llmError(Exception):
    def __init__(self) -> None:
        super().__init__("AI 服务暂不可用，请稍后再试")


class InterviewNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("面试不存在")
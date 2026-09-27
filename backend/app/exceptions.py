class DuplicateUsernameError(Exception):
    def __init__(self,username: str):
        self.username = username
        super().__init__(f"用户名{username}已存在")


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("用户名或密码错误")

class DuplicateUsernameError(Exception):
    def __init__(self,username: str):
        self.username = username
        super().__init__(f"用户名{username}已存在")


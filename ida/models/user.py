class User:
    def __init__(self, username: str, first_name: str, last_name: str, password: str, last_logon: int, created_at: int, is_admin: bool = False, is_disabled: bool = False):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.last_logon = last_logon
        self.created_at = created_at
        self.is_admin = is_admin
        self.is_disabled = is_disabled

    def __str__(self):
        return f"User(username={self.username}, first_name={self.first_name}, last_name={self.last_name}, last_logon={self.last_logon}, created_at={self.created_at}, is_admin={self.is_admin}, is_disabled={self.is_disabled})"

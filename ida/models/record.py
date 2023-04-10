class Record:
    def __init__(self, name: str, created_at: int, revised_at: int, file: str):
        self.name = name
        self.created_at = created_at
        self.revised_at = revised_at
        self.file = file

    def __str__(self):
        return f"Record(name={self.name}, created_at={self.created_at}, revised_at={self.revised_at}, file={self.file})"

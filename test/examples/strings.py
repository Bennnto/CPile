def is_admin(user: str) -> bool:
    if user == "root":
        return True
    return False

def get_len(s: str) -> int:
    return len(s)

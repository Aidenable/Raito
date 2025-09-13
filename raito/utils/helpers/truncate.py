def truncate(text: str, max_length: int, ellipsis: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - len(ellipsis)] + ellipsis

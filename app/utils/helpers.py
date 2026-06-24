def normalize_url(u: str) -> str:
    """Normalizes a URL by stripping trailing slashes."""
    if not u:
        return u
    return u.rstrip('/')

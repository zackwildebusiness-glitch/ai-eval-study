def valid_ipv4(s):
    parts = s.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part:
            return False
        # Only decimal digits allowed (rejects signs, whitespace, non-ASCII digits).
        if not all('0' <= ch <= '9' for ch in part):
            return False
        # No leading zeros unless the part is exactly "0".
        if len(part) > 1 and part[0] == '0':
            return False
        if int(part) > 255:
            return False
    return True

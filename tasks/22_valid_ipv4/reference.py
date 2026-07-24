def valid_ipv4(s):
    parts = s.split(".")
    if len(parts) != 4:
        return False

    for part in parts:
        if len(part) == 0 or len(part) > 3:
            return False
        if not part.isdigit():
            return False
        if part != "0" and part[0] == "0":
            return False
        if int(part) > 255:
            return False

    return True

import shlex

def parse_command(text):
    if not text.strip():
        return []
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()
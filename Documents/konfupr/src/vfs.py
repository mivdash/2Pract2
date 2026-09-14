import os

def load_tree(path):
    tree = {"kind": "dir", "items": {}}
    if path and os.path.exists(path):
        _scan(path, tree)
    return tree

def _scan(real_path, node):
    for name in os.listdir(real_path):
        full = os.path.join(real_path, name)
        if os.path.isdir(full):
            child = {"kind": "dir", "items": {}}
            node["items"][name] = child
            _scan(full, child)
        else:
            node["items"][name] = {"kind": "file"}

def save_tree(node, path):
    if not os.path.exists(path):
        os.makedirs(path)
    for name, child in node["items"].items():
        full = os.path.join(path, name)
        if child["kind"] == "dir":
            save_tree(child, full)
        else:
            open(full, "w").close()

def find_node(tree, parts):
    now = tree
    for part in parts:
        if part == "..":
            return None, "cd .. не поддерживается"
        if now["kind"] != "dir":
            return None, "Это файл"
        if part not in now["items"]:
            return None, f"Нет пути: {part}"
        now = now["items"][part]
    return now, None
"""зависимости в виде дерева из ascii-символов"""

BRANCH = "|-- "
LAST_BRANCH = "`-- "
PIPE = "|   "
SPACE = "    "
CYCLE_MARK = " (цикл)"
REPEAT_MARK = " (см. выше)"


def child_mark(child, path, expanded, graph):
    """пометка для повторного пакета или пустая строка"""
    if child in path:
        return CYCLE_MARK
    if child in expanded and graph.get(child):
        return REPEAT_MARK
    return ""


def add_children(name, prefix, path, graph, state):
    """добавляет строки для зависимостей пакета, обходя дерево вглубь"""
    lines, expanded = state
    children = graph.get(name, [])
    for index, child in enumerate(children):
        last = index == len(children) - 1
        mark = child_mark(child, path, expanded, graph)
        lines.append(prefix + (LAST_BRANCH if last else BRANCH) + child + mark)
        if not mark:
            expanded.add(child)
            deeper = prefix + (SPACE if last else PIPE)
            add_children(child, deeper, path + [child], graph, state)


def format_tree(root, graph):
    """строки дерева зависимостей от корня"""
    lines = [root]
    add_children(root, "", [root], graph, (lines, {root}))
    return lines

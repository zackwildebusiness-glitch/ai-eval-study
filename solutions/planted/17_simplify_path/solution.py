def simplify_path(path):
    stack = []
    for segment in path.split('/'):
        if segment == '' or segment == '.':
            continue
        if segment == '..':
            if len(stack) > 1:
                stack.pop()
            continue
        stack.append(segment)
    return '/' + '/'.join(stack)

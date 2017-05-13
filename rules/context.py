import threading


class localcontext(threading.local):
    def __init__(self):
        self.stack = []


_context = localcontext()


class Context(dict):
    def __init__(self, rule, *args, **kwargs):
        super(Context, self).__init__()
        self.rule = rule
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        _context.stack.append(self)

    def __exit__(self, type, value, traceback):
        _context.stack.pop()


def get_current():
    return _context.stack[-1]

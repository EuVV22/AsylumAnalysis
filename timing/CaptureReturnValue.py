class CaptureReturnValue:
    return_value = None

    def __init__(self, func):
        self.func = func
        self.return_value = None

    def __call__(self, *args, **kwargs):
        self.return_value = self.func(*args, **kwargs)
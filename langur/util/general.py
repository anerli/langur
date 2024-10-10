class UniqueClassAttribute:
    def __init__(self, initial_value=None):
        self.value = initial_value
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if objtype is None:
            return self
        if not hasattr(objtype, f'_{self.name}'):
            setattr(objtype, f'_{self.name}', self.value() if callable(self.value) else self.value)
        return getattr(objtype, f'_{self.name}')

    def __set__(self, obj, value):
        setattr(type(obj), f'_{self.name}', value)


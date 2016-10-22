import shelve


class StateManager:
    def __init__(self, file):
        self.file = file

    def add_value_by_key(self, key, value):
        d = shelve.open(self.file)
        d[key] = value
        d.close()

    def get_value_from_key(self, key):
        d = shelve.open(self.file)
        if key in d:
            value = d[key]
            d.close()
            return value
        else:
            d.close()
            return False
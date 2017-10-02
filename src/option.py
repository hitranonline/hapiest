##
# A simple option type to enforce null checks
##

class Option(object):
    def get_or_else(self, default):
        if isinstance(self, Some):
            return self.value
        else:
            return default

    # Creates a new instance of Some with the given value
    @staticmethod
    def some(val): Some(val)

    # Creates a new instance of None
    @staticmethod
    def none(): None()

# The option where there is a value
class Some(Option):
    def __init__(self, value):
        self.value = value
    def is_some(self):
        return True
    def is_none(self):
        return False

# The option where there is no value
class None(Option):
    def __init__(self):
    def is_some(self):
        return False
    def is_none(self):
        return True

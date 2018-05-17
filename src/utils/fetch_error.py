from enum import Enum

class FetchErrorKind(Enum):
    BadParameter = 1  # This wont be used
    BadParameterGroup = 2  # This wont be used
    BadNuMin = 3  # This wont be used
    BadNuMax = 4  # This wont be used
    BadConnection = 5
    BadIsoList = 6
    FailedToRetreiveData = 7
    FailedToOpenThread = 8
    EmptyName = 9


# A class that contains a FetchErrorKind along with a description for the error
class FetchError:
    """
    A data class that contains an error along with a description of that error.

    """

    # Constructor for FetchError
    #
    # errors: a FetchErrorKind object
    # description: a textual description of the error
    def __init__(self, error: FetchErrorKind, description=''):
        """
        Constructs a FetchError object.

        @param error The type of error encountered
        @param description A description of what happened
        
        """
        self.error = error
        self.description = description


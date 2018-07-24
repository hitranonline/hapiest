# Code Style

_Note:_ Currently, the codebase does not conform entirely to these guidelines. Bug reports or assistance in correcting
these inconsistencies is appreciated.

The basic guidelines found in [The Hitchhiker's Guide to Python](http://docs.python-guide.org/en/latest/writing/style/)
should be followed.


## General Style

- Indentation should use 4 spaces
- Lines should be limited to 120 characters
- Types should always be specified
- CamelCase should be used for class names
- snake_case should be used for variable names
- SNAKE_CASE should be used for static variables and constants
- `'Single quotes'` should be preffered over double quotes.

## Comment Style

- Docummenting static or local variables should be done using `##`
- Documenting classes, functions, and methods should be done using docstrings with double quotes `""" like this """`
- Methods and functions should be documented using javadoc style (e.g. `:param x the x coordinate`)

e.g.
```python
class Example:
    """
    This class is an example of proper documentation in the context of hapiest.
    There is a blank line below this comment intentionally!

    """

    ## The static variable
    #  ...
    #  ...
    static_member = 4
        
    def __init__(self):
        """
        Constructor!

        """
        ## The variable
        #  ...
        self.var = 5

    def add_to_var(self, to_add):
        """
        Adds to self.var

        :param to_add the amount var should be increased by
        :returns: the new value of var
        :throws Exception thrown then to_add is not an integer
        
        """
        if type(to_add) == int:
            self.var += to_add
            return self.var
        else:
            raise Exception("Expected a number!")

```

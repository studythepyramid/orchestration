class User:
    id: int
    name: str = "Anonymous"

# 1. Access the hidden annotations
print(User.__annotations__)
# Output: {'id': <class 'int'>, 'name': <class 'str'>}

# 2. Check what actually exists as a class variable
print(hasattr(User, 'name')) # True (because it has a default value)
print(hasattr(User, 'id'))   # False (it's just a hint, no value exists yet!)

import inspect

class SimpleModel:
    age: int = 25

# Get hints including inherited ones
print(inspect.get_annotations(SimpleModel))


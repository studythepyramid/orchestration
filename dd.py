
from pydantic import BaseModel, ValidationError
import random

class HackerProfile(BaseModel):
    id: int
    alias: str = 'za'
    is_active: bool = True
    # This locks the backdoor!
    model_config = {'validate_assignment': True}

# 1. It automatically parses and converts data (Coercion)
# Notice '123' is a string, but Pydantic cleanly converts it to an int.
user = HackerProfile(id="123", alias="za")
print(user.id) # Output: 123 (as an integer)

users = []
for i in range(5):
    num = random.randint(100, 200)
    users.append(HackerProfile(id=num, alias = str(num)))


# 2. It violently rejects bad data
try:
    bad_user = HackerProfile(id="007", alias="za")
    users.append(bad_user)

    for u in users:
        if u.alias == 'za':
            print("id is string 007!")
        else:
            print("outdated, id must been changed now.")
            # why i can change the 'id' and not trigger exception?
            u.id = 'true id' + str(random.randint(1000,2000))
except ValidationError as e:
    print(e) # Spits out a highly detailed error explaining exactly which field failed

from pydantic import BaseModel, Field, ValidationError

class User(BaseModel):
    id: int
    name: str = "Anonymous"
    age: int = Field(gt=0, lt=120)

try:
    # Coercion: '1' (string) becomes 1 (int)
    user = User(id="1", age=25)
    print(user.model_dump())
except ValidationError as e:
    print(e.json())


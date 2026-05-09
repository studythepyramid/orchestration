from pydantic import BaseModel, Field, ValidationError

class User(BaseModel):
    id: int
    name: str = "Anonymous"
    age: int = Field(gt=0, lt=120)

# --- SCENARIO 1: The "Lax" Coercion ---
# Pydantic sees 'id' is a string "101", but it knows it should be an int.
# It automatically converts it for you.
user_ok = User(id="101", age=25)
print(f"ID: {user_ok.id} ({type(user_ok.id)})")
# Output: ID: 101 (<class 'int'>)

# --- SCENARIO 2: The "Bad" Data ---
try:
    User(
        id="not-a-number",  # Error: Cannot convert string to int
        age=150             # Error: Violates Field(lt=120)
    )
except ValidationError as e:
    print(e.json())


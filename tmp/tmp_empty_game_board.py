

User_card = {
        "sequence": 0,  # as card_id, uint
        "raw_input": "",
        "intent": "",
        "timestamp": 0, # seconds, or milliseconds
        }

KnowIntents = ["exit", "chat", "exec", "query", "find_cmd"]

before_input_prompt = """
 [q) -> Quit game
 [y] User Agree,  [p] Check problem
 [n] User not agree.
 [!cmd]  -> Manual override (e.g., !ls -p)
 [text]  -> Give feedback or instructions to AI")

"""

def from_input_to_ucard():
    """
    Handles user input with a cleaner, consistent prompt.
    """
    print("\n" + "-"*40)
    print(before_input_prompt)

    raw = input(">> ").strip()
    print("\n") # space up

    uc = {} # gemi, how to clone User_card instead of {}?
    uc = make_user_card(raw)

    return uc


def make_user_card(raw: str) :

    if is_single_letter_q(raw):
        uc.intent = 'exit'
        return uc

    # ...
    return 
 


def is_single_letter(line: str):
    return len(line.strip().to_low_case()) == 1


def is_single_letter_q(raw: str):
    if(is_single_letter(raw)):
        return raw.low_case() == 'q'

    return False


def has_single_leading_letter(user_input: str):
    return "yes or no"



def start_turn_based_game():

    while True:

        # USER TURN: Decide what to do
        user_card = from_input_to_ucard( )
        

        # EVALUATE TURN
        match user_card.intent():
            case "exit":
                print("[*] Game Over. Terminating.")
                break # or return, gemi, i guess it's return?

            case "y":
                print("y [-] AI didn't suggest any code to run. Use 'text' to nudge it.")

            case "exec": #if user_choice.startswith("!"):
                print("exec")

            case "":
                print("[!] Empty input. AI will re-analyze current state.")

            case _:
                # just show user input and it's processing
                # Treat everything else as natural language feedback/correction
                print("\n Boss out, you need loop again. \n")



if __name__ == "__main__":
    try:
        start_turn_based_game()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user. Closing.")



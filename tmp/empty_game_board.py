
import time

# The Template
User_card_template = {
    "sequence": 0,
    "raw_input": "",
    "intent": "",
    "timestamp": 0,
}

KnowIntents = ["exit", "chat", "exec", "query", "find_cmd", "none"]

before_input_prompt = """
 [q] -> Quit game
 [y] User Agree,  [p] Check problem
 [n] User not agree.
 [!cmd]  -> Manual override (e.g., !ls -p)
 [text]  -> Give feedback or instructions to AI
"""

def make_user_card(raw: str, seq: int):
    # Gemi: Using .copy() to clone the template
    uc = User_card_template.copy()
    uc["raw_input"] = raw
    uc["sequence"] = seq
    uc["timestamp"] = int(time.time())

    # Logic to determine intent
    clean_raw = raw.strip().lower()
    
    if clean_raw == 'q':
        uc["intent"] = "exit"
    elif clean_raw == 'y':
        uc["intent"] = "y"
    elif raw.startswith("!"):
        uc["intent"] = "exec"
    elif not clean_raw:
        uc["intent"] = "none"
    else:
        uc["intent"] = "chat"
    
    return uc

def from_input_to_ucard(turn_count: int):
    print("\n" + "-"*40)
    print(before_input_prompt)

    raw = input(">> ").strip()
    return make_user_card(raw, turn_count)

def start_turn_based_game():
    turn_count = 0
    while True:
        turn_count += 1
        
        # USER TURN
        user_card = from_input_to_ucard(turn_count)
        
        # EVALUATE TURN (Using dict access [])
        intent = user_card["intent"]

        match intent:
            case "exit":
                print("[*] Game Over. Terminating.")
                break 

            case "y":
                print("[-] AI didn't suggest any code to run. Use 'text' to nudge it.")

            case "exec":
                cmd = user_card["raw_input"][1:]
                print(f"[!] Manual Override detected: Running '{cmd}'")

            case "none":
                print("[!] Empty input. AI will re-analyze current state.")

            case "chat":
                print(f"[*] Feedback logged: {user_card['raw_input']}")
            case _:
                print("\n Boss out, you need loop again. \n")


if __name__ == "__main__":
    try:
        start_turn_based_game()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user. Closing.")

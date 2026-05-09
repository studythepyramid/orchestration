
import subprocess
from typing import List

# This is to check host machine with list of commands
# The information gathered would be a 'host context' 
# this context would be good for next step, 
# it's to setup background for ai+man to analyze problem.

cmd_list = [
    "hostnamectl",
    "whoami",
    "pwd",
    "date",
    "apt --version",
    "ip addr",
]

cmd_results: List[str] = []

def one_cmd(cmd_str: str) -> str:
    """ 
    Execute one cmd, return results formatted for the context loop.
    """
    try:
        result = subprocess.run(
            cmd_str, shell=True,
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        if result.stderr:
            output += f"\nERROR: {result.stderr.strip()}"
            
        # Wrap the output with clear boundaries for the AI to parse easily
        formatted_result = f"--- [CMD]: {cmd_str} ---\n"
        formatted_result += f"{output if output else '<no output>'}\n"
        return formatted_result
        
    except subprocess.TimeoutExpired:
        return f"--- [CMD]: {cmd_str} ---\nERROR: Timeout after 15s\n"
    except Exception as e:
        return f"--- [CMD]: {cmd_str} ---\nERROR: Exception occurred - {str(e)}\n"


def get_machine_info() -> List[str]:
    """ 
    Batch run cmd in cmd_list, fetch working context.
    Calls 'one_cmd' for each cmd in list.
    """
    # Clear the global list in case this is called multiple times per session
    cmd_results.clear()
    
    for cmd in cmd_list:
        cmd_results.append(one_cmd(cmd))

    return cmd_results


if __name__ == "__main__":
    print("Gathering machine context for the loop...\n")
    context = get_machine_info()
    
    # Join and print the context to verify it works
    full_machine_context = "\n".join(context)
    print(full_machine_context)








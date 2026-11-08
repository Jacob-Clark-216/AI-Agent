import ollama
import pathlib as pl
import time as t


# ---------------------------------------------------- Tools ----------------------------------------------------

workspace_folder = pl.Path(__file__).parent / "Workspace"

#  ---------------------Read and edit files in workspace ---------------------

def list_files() -> str:
    # List files in the workspace folder or empty if none present
    return "\n".join(f.name for f in workspace_folder.iterdir()) or "(empty)"

def read_file(filename:str) -> str:
    # Read contents of file in workspace folder
    path = workspace_folder / filename
    if not path.is_file():
        return "Error: No such file exists within the workspace"
    else:
        return path.read_text(encoding="utf-8")

def write_file(filename:str, content:str) -> str:
    # Create new file or overwrite existing file
    path = workspace_folder / filename
    path.write_text(content, encoding="utf-8")
    return f"File {filename} correctly written"

def delete_file(filename: str) -> str:
    # Delete a file in the workspace
    path = workspace_folder / filename
    if path.exists:
        decision = ""
        while decision.upper() not in ["Y", "N"]:
            decision = input(f"Agent wants to delete {filename}. Are you happy with this decision? (Y/N)")
        if decision.upper() == "Y":
            path.unlink()
            return f"File {filename} has been successfully deleted"
        else:
            return f"User has not given permission to delete {filename}"

# ----------------------------- Persistant Memory-----------------------------

memory = pl.Path("memory.md")

def load_memory() -> str:
    # Read the contents of the persistant memory file
    return memory.read_text(encoding="utf-8")

def store_memory(note:str) -> str:
    # Append note to memory file
    content = memory.read_text(encoding="utf-8")
    time_called = f"{t.ctime()} - "
    addition = "\n\n" + time_called + note
    content += addition
    memory.write_text(content, encoding="utf-8")
    return f"New note '{note}' added successfully to the memory file"

# -------------------------- Time and date retrieval --------------------------

def get_current_time() -> str:
    # Get current time
    return f"{t.ctime()}"


tools = {"list_files": list_files, "read_file": read_file, "write_file": write_file, "delete_file": delete_file, "load_memory": load_memory, "store_memory": store_memory, "get_current_time": get_current_time}

tool_schema = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in the workspace folder",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file in the workspace folder",
                    "parameters": {
                        "type": "object",
                        "properties": {"filename": {"type": "string"}},
                        "required": ["filename"]}
        }
    },
    {
        "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Create new file or overwrite existing file in the workspace folder",
                    "parameters": {
                        "type": "object",
                        "properties": {"filename": {"type": "string"}, "content": {"type": "string"}},
                        "required": ["filename"]}
        }
    },
    {
        "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Make a request to delete a file in the workspace. The user must review the request and approve or deny requests before deletion",
                    "parameters": {
                        "type": "object",
                        "properties": {"filename": {"type": "string"}},
                        "required": ["filename"]}
                }
    },
    {
        "type": "function",
                "function": {
                    "name": "load_memory",
                    "description": "Retrieve content of the persistant memory file",
                    "parameters": {"type": "object", "properties": {}}
                }
    },
        {
        "type": "function",
                "function": {
                    "name": "store_memory",
                    "description": "Save a note to the persistant memory file with a timestamp of when it was stored",
                    "parameters": {
                        "type": "object",
                        "properties": {"note": {"type": "string"}},
                        "required": ["note"]}
                }
    },
    {
        "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "Get current day, date, and time in the format [weekday] [month] [day] [hrs:mins:secs] [year]",
                    "parameters": {"type": "object", "properties": {}}
        }
    }
]

# ----------------------------------------------------- LLM -----------------------------------------------------

model = "gemma4:e2b"
messages = [{
    "role": "system",
    "content":
    "You are a friendly, helpful personal assistant. You must use the load_memory tool at the start of any conversation before responding to any user queries to retrieve historical information. You must use british english and spelling unless otherwise required by the task given. You should use the store_memory tool to record any pertinent information about the user that is not already in persistant storage."
    }]

def chat() -> str:
    response = ollama.chat(
        model = f"{model}",
        messages = messages,
        tools=tool_schema
        )
    return response

# ------------------------------------------------ Agentic Loop ------------------------------------------------

def run_agent() -> str:
    while True:

        response = chat()

        if not response.message.tool_calls:
            messages.append(response.message)
            # Exit if answer is given
            return f"Agent: {response.message.content}"
        else:
            # Loop through tool calls and add results to context
            messages.append(response.message)
            for call in response.message.tool_calls:
                if call.function.name in tools:
                    args = call.function.arguments or {}
                    result = tools[call.function.name](**args)
                    print(f"  [TOOL] {call.function.name}({args}) - {result[:25]}")
                    messages.append({"role": "tool", "content": result})
    
if __name__ == "__main__":
    print(r"Agent Running - \q to quit")
    # TODO: Implement memory storage prompt when chat is closed

    while True:
        next_message = input("> ")
        if next_message == r"\q":
            messages.append({
                "role": "user",
                "content": "I am closing the session. Please summarise the events of this session and store them in persistant memory for future reference."
            })
            run_agent()
            break

        try:        
            messages.append({"role": "user", "content": next_message})

            print("\n\n")
            print(run_agent())
            print("\n" + "-"*80)
        except ConnectionError:
            print("Error: Ollama is not accessible.")
            raise SystemExit
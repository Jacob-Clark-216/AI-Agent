import ollama
import json
import pathlib as pl
import time as t


# ---------------------------------------------------- Tools ----------------------------------------------------

workspace_folder = pl.Path(__file__).parent / "Workspace"

def list_files() -> str:
    # List files in the workspace folder or empty if none present
    return "\n".join(f.name for f in workspace_folder.iterdir()) or "(empty)"

def read_file(file_name:str) -> str:
    # Read contents of file in workspace folder
    path = workspace_folder / file_name
    if not path.is_file():
        return "Error: No such file exists within the workspace"
    else:
        return path.read_text(encoding="utf-8")

def write_file(file_name:str, content:str) -> str:
    # Create new file or overwrite existing file
    path = workspace_folder / file_name
    path.write_text(content, encoding="utf-8")
    return f"File {file_name} correctly written"

def get_current_time() -> str:
    # Get current time
    return f"{t.ctime()}"


tools = {"list_files": list_files, "read_file": read_file, "write_file": write_file, "get_current_time": get_current_time}

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
                    "name": "get_current_time",
                    "description": "Get current day, date, and time in the format [weekday] [month] [day] [hrs:mins:secs] [year]",
                    "parameters": {"type": "object", "properties": {}}
        }
    }
]

# ----------------------------------------------------- LLM -----------------------------------------------------

model = "gemma4:e2b"
messages = [{"role": "system", "content": "You are a friendly, helpful personal assistant."}]

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
                    args = json.loads(call.function.arguments or "{}")
                    result = tools[call.function.name](**args)
                    print(f"  [TOOL] {call.function.name}({args}) - {result}")
                    messages.append({"role": "tool", "content": result})
    
if __name__ == "__main__":
    print("Agent Running - ctrl+c to quit")

    while True:
        next_message = input("> ")
        if next_message == r"\q":
            break
        
        messages.append({"role": "user", "content": next_message})

        print(run_agent())
import ollama, requests, bs4, random, json
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
            try:
                path.unlink()
                return f"File {filename} has been successfully deleted"
            except FileNotFoundError:
                return f"File {filename} does not exist"
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

config_file = pl.Path("config.json")
with open(config_file, "r") as config:
    settings = json.load(config)
    profiles = settings["web_fetcher"]["user_agent_profiles"]

def fetch_web_content(url: str, retries: int = settings["web_fetcher"]["max_retries"], timeout: int = settings["web_fetcher"]["timeout_seconds"]) -> dict:
    # Make a get request to the target url
    decision = ""
    while decision.upper() not in ["Y", "N"]:
        decision = input(f"Agent wants to access {url} from the internet. Are you happy with this decision? (Y/N)")
    if decision.upper() == "Y":
        # Randomly select browser profile and format appropriate headers
        profile = random.choice(list(profiles.values()))
        headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": profile["User-Agent"],
            "Accept": profile["Accept"],
            "Accept-Language": "en,en-US;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }
        for r in range(retries):
            # Send get request to url using given timeout
            response = requests.get(url, headers=headers, timeout=timeout)
            # Check status code of response
            if response.status_code == 200:
                print("Successfully retrieved content (Status 200).")
                response = response.text
                soup = bs4.BeautifulSoup(response, "html.parser")
                # Remove potential XSS and malicious prompt injection
                for element in soup(["script", "style", "header", "footer", "nav", "iframe", "noscript"]):
                    element.decompose()
                data = {"status code": 200}
                data["title"] = soup.title.text
                description = soup.find("meta", attrs = {"name": "description"})
                if description != None:
                    data["description"] = description.get("content")
                data["links"] = []
                for link in soup.find_all("a"):
                    data["links"].append(link.get("href"))
                data["content"] =  "\n".join(line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip())
                return data
            elif response.status_code != 429:
                print(f"Error {response.status_code}: {response.text}")
                return {"status code": response.status_code, "Error": ""}
            else:
                wait = settings["web_fetcher"]["rate_limit_wait_base"]**r
                print(f"Rate limited. Waiting for {wait} seconds before retrying")
                t.sleep(wait)
        return {"status code": response.status_code, "Error": "Rate Limited. Failed to retrieve content after retries."}
    else:
        return {"Error": f"The user has rejected the request to access {url}"}


tools = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "delete_file": delete_file,
    "load_memory": load_memory,
    "store_memory": store_memory,
    "get_current_time": get_current_time,
    "fetch_web_content": fetch_web_content
    }

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
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_web_content",
            "description": "Make a request to get title, description, links, and content of a webpage. Exponential back-off and timeouts are included in the tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "retries": {"type": "integer"},
                    "timeout": {"type": "integer"}
                    },
                "required": ["url"]
                }
        }
    }
]

# ----------------------------------------------------- LLM -----------------------------------------------------

model = "gemma4:e2b"
messages = [{
    "role": "system",
    "content": """
You are a friendly, helpful, and proactive personal assistant working within an agentic harness the user has designed.
You must use the load_memory tool at the start of any conversation before responding to any user queries to retrieve historical information.
You must use british english and spelling unless otherwise required by the task given.
You should use the store_memory tool to record any pertinent information about the user that is not already in persistant storage.
You are encouraged to use tools implicitly rather than waiting for an explicit request from the user. For example, if the user mentions an event 'yesterday' you should implicitly identify that the get_current_time tool would provide you with useful context to complete the task rather than wait for the user to ask you to use that tool.
"""
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
                    if type(result) == dict:
                        result = json.dumps(result)
                    print(f"  [TOOL] {call.function.name}({args})")
                    messages.append({"role": "tool", "content": result})
    
if __name__ == "__main__":
    print(r"Agent Running - \q to quit")
    # TODO: Implement memory storage prompt when chat is closed

    while True:
        next_message = input("> ")
        if next_message == r"\q":
            messages.append({
                "role": "user",
                "content": """
I am closing this session. Please generate a structured summary of our session. Please organise the summary using the following categories:
1. **[Topic/Goal]**
2. **[Key Decisions Made]**
3. **[Key Learnings/Takeaways]**
4. **[Action Items for Next Session]**
5. **[Resource Log]** (This section must list all files **created**, **updated**, or **deleted** during this session, noting the file name and the change made.)

Store this summary in persistent memory.
"""
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
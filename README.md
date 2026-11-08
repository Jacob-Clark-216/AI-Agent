# Agentic Harness

## Overview

This repository documents the architecture and capabilities of the Agentic System that powers this interface. Designed for complex task execution, dynamic information retrieval, and structured output generation. This system leverages a modular approach to handle intricate requests, integrating various tools for comprehensive problem-solving.

---

## Agentic Harness Architecture

The core of this system is an Agentic Harness designed for dynamic task routing and tool orchestration.

*   **Core Logic:** The system operates by analysing user intent, decomposing complex requests into discrete sub-tasks, and dynamically selecting the appropriate tool(s) for execution. It accomplishes this by feeding user input to a Gemma 4 LLM via Ollama, processing assistant messages, and executing the tool calls returned.
*   **Memory Management:** Persistent memory is utilised to maintain context across sessions and store critical operational notes, thereby ensuring continuity and facilitating iterative learning. This is achieved by providing the model with a dedicated file that it can read and append notes to via specific tools, alongside a system prompt that checks this file at the start of each session before responding to any user query.
*   **Tool Integration Layer:** A standardised interface enables the agent to interact seamlessly with external functions, empowering it to perform real-world actions such as file management, external data retrieval, and system diagnostics.

---

## Tool Organisation and Capabilities

The available tools are systematically grouped to illustrate their function and their specific impact on the agent's operational scope.

### Group 1: Workspace Interaction Tools (Affecting the Local Environment)

These tools are essential for the agent to interact with and manage files within the workspace, making it an active participant in local file system operations.

| Tool Name | Description | Primary Use Case | Model Enhancement |
| :--- | :--- | :--- | :--- |
| `list_files` | Lists all files present in the workspace directory. | File system exploration, inventory management, and task scoping. | Enables context-aware navigation by providing the agent with a real-time map of its operational environment. |
| `read_file` | Reads the content of a specified file. | Retrieving necessary data, documentation, source code, or context for analysis. | Allows the model to ingest external knowledge directly into its working memory for accurate responses. |
| `write_file` | Creates a new file or overwrites an existing one with specified content. | Generating reports, saving structured output, documenting results, or creating new assets. | Empowers the model to produce tangible, persistent outputs that fulfil user requirements. |
| `delete_file` | Removes a specified file from the workspace. | Cleanup operations, removing outdated files, or executing specific clean-up commands. | Allows for safe and controlled modification of the environment based on defined tasks. |

### Group 2: Persistent Memory & State Tools (Affecting Context and Learning)

These tools manage the agent's long-term context, state persistence, and learning capabilities, which are crucial for maintaining coherence across multiple interactions.

| Tool Name | Description | Primary Use Case | Model Enhancement |
| :--- | :--- | :--- | :--- |
| `load_memory` | Retrieves stored information from the persistent memory file. | Context recall, retrieving historical session data, and accessing long-term operational notes. | Ensures statefulness, allowing the model to maintain context and build upon past interactions seamlessly. |
| `store_memory` | Saves new information or operational notes to persistent memory. | Logging key decisions, recording learned information, and saving critical operational context. | Facilitates continuous learning and robust session persistence, improving the agent's performance over time. |

### Group 3: System Utility Tools (Affecting Operational Status)

These tools provide system-level information and temporal context, which are necessary for logging, scheduling, and time-sensitive operations.

| Tool Name | Description | Primary Use Case | Model Enhancement |
| :--- | :--- | :--- | :--- |
| `get_current_time` | Retrieves the current date, time, and time zone information. | Time-sensitive operations, accurate logging, and scheduling context checks. | Provides the model with temporal context necessary for accurate logging and time-dependent queries. |

---

## Potential Use Cases

The Agentic Harness is highly versatile and can be applied across a broad spectrum of productivity and analytical tasks:

1.  **Project Management Assistance:** Users can request the agent to summarise project documents (`read_file`), generate status reports (`write_file`), and track file changes (`list_files`) for a given project folder.
2.  **Knowledge Synthesis:** For complex research tasks, the agent can be tasked to read multiple source documents, synthesise key findings, and save the summary into a dedicated knowledge base (`store_memory`).
3.  **Automated Data Processing:** Executing workflows where data files are input, processed (hypothetically via other tools), and final results are documented in a structured format.
4.  **System Debugging:** Using memory to recall past errors or logs and using file manipulation tools to inspect configuration files for troubleshooting.

---

## Safety Features and Guardrails

The tools provided to the agent are designed with robust safety mechanisms to minimise risks to the user's system:

*   **Workspace Scope Limitation:** The Agent's file manipulation capabilities are strictly confined to the designated "Workspace" folder. This constraint prevents the unintended alteration or deletion of files outside the defined scope.
*   **User Permission Guardrail:** For potentially destructive actions (e.g., `delete_file`), the agent's workflow is paused. A request is issued to the user, explicitly naming the file the agent intends to modify or delete, requiring explicit user approval before execution. If the user denies the request, the action is aborted, and the agent reports the denial.
*   **Read/Append Restriction:** Tools interacting with sensitive files, such as the persistent memory file, are intentionally limited to read and append operations. This mechanism prevents accidental or malicious overwriting or deletion of critical context.

---

## How to Interact

Simply provide a clear, detailed request. The Agentic Harness will automatically analyse the request, determine the necessary steps, and utilise the appropriate tools to deliver a precise and accurate result.

**Example Prompt:** "Analyse the contents of `project_plan.txt`, summarise the key risks, and save a summary report to `risk_assessment.md`."

---

## Development Roadmap

This roadmap outlines planned enhancements to expand the Agentic Harness's capabilities across broader domains.

| Proposal | Description | Potential Use Cases | Model Enhancement |
| :--- | :--- | :--- | :--- |
| **Web Fetcher** | A tool designed to provide the agent with basic internet access. Content from specified URLs will be retrieved for the agent. | Web research, gathering real-time data, accessing public documentation. | Enables the model to access up-to-date, external information, significantly expanding the agent's knowledge boundary. |
| **Gmail API** | A suite of tools enabling interaction with the Google Gmail API, allowing the agent to read and draft emails on the user's behalf. | Automated email triage, drafting replies, synchronising communication with professional inboxes. | Allows the agent to perform complex, real-world communication tasks, enhancing productivity in professional settings. |
| **Dictation Support** | Implementation of a feature allowing users to interact with the agent via speech rather than typing. | Hands-free operation, rapid query submission, interactive voice commands. | Improves user interaction speed and naturalness, making the agent significantly more accessible and efficient for rapid task execution. |
| **Model Switching** | A feature enabling the dynamic switching of the LLM model during sessions. | Optimising compute resources for simple tasks, selecting specialised models for complex reasoning tasks. | Optimises resource utilisation and allows for the selection of the most appropriate model for a given task complexity, improving response latency and accuracy. |
from langsmith import Client
import time

# Initialize the LangSmith client
# It will automatically pick up the LANGCHAIN_API_KEY from your terminal environment
client = Client()

DATASET_NAME = "SWE580_MCP_Evaluation"

# The 20-question dataset with expected answers and difficulty metadata
dataset_items = [
    # --- EASY ---
    {
        "question": "What does the acronym 'MCP' stand for in the context of AI engineering?",
        "expected": "Model Context Protocol.",
        "difficulty": "Easy"
    },
    {
        "question": "What is the primary problem that the Model Context Protocol was created to solve?",
        "expected": "Standardizing the connection and communication between AI models and external data sources or tools.",
        "difficulty": "Easy"
    },
    {
        "question": "In the MCP architecture, what is the role of the 'Client'?",
        "expected": "The host application (like an IDE or chat app) that initiates the connection and routes requests from the AI model to the server.",
        "difficulty": "Easy"
    },
    {
        "question": "In the MCP architecture, what is the role of an 'MCP Server'?",
        "expected": "To securely expose specific local data, tools, and prompts to the client application.",
        "difficulty": "Easy"
    },
    {
        "question": "Name the two primary transport mechanisms used by MCP to establish a connection.",
        "expected": "stdio (Standard Input/Output) and SSE (Server-Sent Events).",
        "difficulty": "Easy"
    },
    {
        "question": "True or False: The Model Context Protocol requires all servers to be written in TypeScript.",
        "expected": "False. MCP is language-agnostic and servers can be written in Python, TypeScript, Java, etc.",
        "difficulty": "Easy"
    },
    {
        "question": "What is the definition of an MCP 'Resource'?",
        "expected": "Data or context provided by the server that the AI can read, such as a file, API response, or database record.",
        "difficulty": "Easy"
    },
    {
        "question": "What is the definition of an MCP 'Tool'?",
        "expected": "Executable functions exposed by the server that the AI can trigger to take actions or produce side-effects.",
        "difficulty": "Easy"
    },

    # --- MEDIUM ---
    {
        "question": "Explain the functional difference between exposing data as an MCP 'Resource' versus exposing it via an MCP 'Tool'.",
        "expected": "Resources provide static, read-only data for AI context, while Tools execute actions or side-effects based on AI inputs.",
        "difficulty": "Medium"
    },
    {
        "question": "Describe the client-server handshake process. What happens when an MCP connection is first initialized?",
        "expected": "The client sends an 'initialize' request with its capabilities. The server responds with its capabilities. Finally, the client sends an 'initialized' notification to complete the handshake.",
        "difficulty": "Medium"
    },
    {
        "question": "How do MCP 'Prompts' help standardize user interactions with an AI model?",
        "expected": "They allow servers to define reusable, parameterized instruction templates that clients can easily render in their UI.",
        "difficulty": "Medium"
    },
    {
        "question": "Compare the `stdio` transport and the `SSE` transport. In what scenario would a developer choose one over the other?",
        "expected": "stdio is chosen for secure, local processes running on the same machine. SSE is chosen when the server needs to be hosted remotely or accessed over a network.",
        "difficulty": "Medium"
    },
    {
        "question": "Under the hood, what messaging protocol does MCP use to format the data being sent back and forth?",
        "expected": "JSON-RPC 2.0.",
        "difficulty": "Medium"
    },
    {
        "question": "If a user wants an AI to be able to read a static local configuration file, which MCP feature should the server developer use, and why?",
        "expected": "A Resource, because it is specifically designed for exposing read-only contextual data to the AI.",
        "difficulty": "Medium"
    },
    {
        "question": "If a user wants an AI to be able to write or update a database record, which MCP feature should be used, and why?",
        "expected": "A Tool, because writing to a database is an executable action that changes state.",
        "difficulty": "Medium"
    },
    {
        "question": "How does the host application (the client) discover which Tools and Resources a connected MCP server actually supports?",
        "expected": "By querying the server using specific listing endpoints, such as 'tools/list' or 'resources/list'.",
        "difficulty": "Medium"
    },

    # --- HARD ---
    {
        "question": "How does MCP's user-controlled, opt-in authorization model mitigate the security risks of granting a Large Language Model access to a local filesystem?",
        "expected": "It prevents the AI from autonomously browsing the filesystem. The user must explicitly approve or configure the server to only expose specific, sandboxed directories.",
        "difficulty": "Hard"
    },
    {
        "question": "Detail the exact sequence of events and messages exchanged when an LLM decides to execute an MCP Tool.",
        "expected": "The LLM generates a tool call -> Client sends a 'tools/call' request to the Server -> Server executes the logic -> Server returns the tool response -> Client passes the result back to the LLM.",
        "difficulty": "Hard"
    },
    {
        "question": "Discuss the security implications and potential vulnerabilities of exposing an MCP server over a network using SSE, compared to running it purely locally via stdio.",
        "expected": "SSE exposes the server to network interception, DDoS attacks, or unauthorized remote access, requiring robust authentication mechanisms (like API keys or OAuth). stdio avoids this by relying entirely on local OS-level process isolation.",
        "difficulty": "Hard"
    },
    {
        "question": "If you were building a custom MCP server to connect an LLM to a rate-limited external API, how would you implement rate limiting or error handling?",
        "expected": "You would implement a token bucket or request queue within the server's tool execution logic, and return standard JSON-RPC error codes (equivalent to HTTP 429) if the AI attempts to exceed the limits.",
        "difficulty": "Hard"
    }
]

def create_langsmith_dataset():
    """Uploads the questions and expected answers to LangSmith."""
    
    # Check if dataset already exists to avoid duplicates
    if client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Dataset '{DATASET_NAME}' already exists. Please delete it in the LangSmith UI if you want to recreate it.")
        return

    print(f"Creating new dataset: '{DATASET_NAME}'...")
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Evaluation dataset for SWE 580 RAG Assignment (Model Context Protocol). Contains Easy, Medium, and Hard questions."
    )

    print("Uploading 20 question-answer pairs...")
    inputs = [{"question": item["question"]} for item in dataset_items]
    outputs = [{"expected_answer": item["expected"]} for item in dataset_items]
    metadata = [{"difficulty": item["difficulty"]} for item in dataset_items]

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        metadata=metadata,
        dataset_id=dataset.id,
    )
    
    print("✅ Upload complete! Check your LangSmith dashboard.")

if __name__ == "__main__":
    create_langsmith_dataset()
# Top 3 most relevant chunks

## What does the acronym "MCP" stand for in the context of AI engineering?
Unfortunately, I don't know what "MCP" stands for based on the provided context. The text mentions "The use of MCP isn't just a concept; it's already a reality..." but doesn't explicitly define what MCP is.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/Model_Context_Protocol_Yusuf_Ozuysal.pdf (Page 18)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 40)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/Model_Context_Protocol_Yusuf_Ozuysal.pdf (Page 19)

## In the MCP architecture, what is the role of an "MCP Server"?
Based on the provided context, I do not see any information about the role of an "MCP Server" in the MCP (Model Context Protocol) architecture. The only information provided is about the MCP Client and its role as a communicator.

However, based on general principles of client-server architectures, it can be inferred that the MCP Server would likely play a complementary role to the MCP Client, possibly handling requests from the client, processing them, and sending responses back to the client.

But since I don't have explicit information about the MCP Server's role in the context provided, I'll say:

I do not know.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/Model_Context_Protocol_Yusuf_Ozuysal.pdf (Page 18)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/Model_Context_Protocol_Yusuf_Ozuysal.pdf (Page 19)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 4)



## Describe the client-server handshake process. What happens when an MCP connection is first initialized?
Based on the provided context, here's a description of the client-server handshake process:

The communication between the MCP client and server follows a structured process. When an MCP connection is first initialized, the client sends an initial request to query the server's functionalities. The server responds with an initial response listing the available tools, resources, and prompts that the client can leverage.

After this exchange, the system maintains a continuous exchange of notifications between the client and server to ensure that changes in server status or updates are communicated back to the client in real-time. This means that once the connection is established, there's ongoing communication between the client and server to keep each other informed of any updates or changes.

This process doesn't explicitly describe all the detailed steps involved in the handshake (e.g., the specific sequence of requests and responses), but it does provide a general overview of how the client-server interaction works.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 83)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/MCP_landscape_security_threats.pdf (Page 6)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 72)




## If a user wants an AI to be able to read a static local configuration file, which MCP feature (Resource, Tool, or Prompt) should the server developer use, and why?
Based on the context provided, if a user wants an AI to be able to read a static local configuration file, I would recommend using the "Tool" feature.

The context shows that Client A connects to a local filesystem MCP Server, which allows the Host to read the content of a highlighted function from the local file. This is an example of a tool (in this case, the `search_document` tool) being used to interact with the Notion server. To allow the AI to read a static local configuration file, the developer would need to declare a tool that can perform file reading operations on the local filesystem.

Using the Tool feature makes sense because it allows the server to execute custom tools with specific inputs, which in this case could be a function to read the local configuration file. The Resourcestab is focused on listing available resources and their metadata, while the Promptstab is for displaying prompt templates and argument schemas, so neither of those features seem directly applicable to reading a static local configuration file.

So, if the developer wants the AI to be able to read a static local configuration file, using the Tool feature would be the most suitable choice.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 25)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 68)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 26)




## How does MCP's user-controlled, opt-in authorization model mitigate the security risks of granting a Large Language Model access to a local filesystem?
Based on the context, I don't know how MCP's user-controlled, opt-in authorization model mitigates the security risks of granting a Large Language Model access to a local filesystem. The provided text only mentions operational recommendations and measures to reduce unauthorized access, but it doesn't specifically address the authorization model's impact on file-system access.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 65)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/MCP_landscape_security_threats.pdf (Page 24)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/MCP_landscape_security_threats.pdf (Page 23)



# Top 5 most relevant chunks

## What does the acronym "MCP" stand for in the context of AI engineering?
I can answer that! Based on the provided context, I don't see an explicit explanation of what "MCP" stands for. However, from the usage and description, it appears to be related to a protocol or interface for accessing tools and resources in an AI-powered coding environment.

If you need more information or clarification, please let me know!

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/Model_Context_Protocol_Yusuf_Ozuysal.pdf (Page 18)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 40)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/Model_Context_Protocol_Yusuf_Ozuysal.pdf (Page 19)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/MCP_landscape_security_threats.pdf (Page 2)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 44)

## In the MCP architecture, what is the role of an "MCP Server"?
Based on the context provided, in Chapter 3: The Host, Client, and Server: Deconstructing the MCP Architecture, it appears that a server plays a crucial role in the Model Context Protocol (MCP) architecture.

According to the text, the MCP architecture has three main components:

1. MCP Client – The Messenger
2. MCP Server (not explicitly mentioned as "the Host" but assumed based on the context)
3. And another component that is implied but not explicitly mentioned

However, it's explicitly stated in Chapter 6: Developing Your First MCP Server: A Practical Guide that an MCP Server is a critical component in building functional and secure integrations.

Assuming the third main component of the MCP architecture to be "the Host" (as implied by the title), I would say that an MCP Server is likely responsible for handling requests from the MCP Client, processing them, and sending responses back. The exact details are not explicitly stated, but based on the context, it's clear that a server plays a key role in the MCP architecture.

To give you a more precise answer, I'll refer to Chapter 3: "The Host, Client, and Server: Deconstructing the MCP Architecture", where it is written:

"The three main components of the MCP architecture are:

* The MCP Client (a.k.a. the Messenger)
* The Host
* The Server

Given that information, I can confidently say that an MCP Server's role in the Model Context Protocol architecture is to handle requests from the MCP Client and respond with processed data.

Therefore, the answer to your question is: In the MCP architecture, the role of an "MCP Server" is to process requests from the MCP Client and send responses back.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/Model_Context_Protocol_Yusuf_Ozuysal.pdf (Page 18)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/Model_Context_Protocol_Yusuf_Ozuysal.pdf (Page 19)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 4)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 11)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 18)


## Describe the client-server handshake process. What happens when an MCP connection is first initialized?
Based on the provided context, here's a description of the client-server handshake process:

The client-server handshake process in the Model Context Protocol (MCP) begins with an initial request from the client to query the server's functionalities. This request is sent by the MCP client to the MCP server. Upon receiving this request, the server responds with an initial response listing the available tools, resources, and prompts that the client can leverage.

This initial response marks the establishment of a connection between the client and the server. Once the connection is established, the system maintains a continuous exchange of notifications to ensure that changes in server status or updates are communicated back to the client in real-time.

In other words, when an MCP connection is first initialized:

1. The client sends an initial request to the server to query its functionalities.
2. The server responds with an initial response listing available tools, resources, and prompts.
3. A connection is established between the client and server.
4. A continuous exchange of notifications begins to keep the client informed of ongoing updates.

This handshake process allows the MCP client to discover and interact with the authorization endpoints on the MCP server, enabling secure communication and tool access through a unified interface.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 83)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/MCP_landscape_security_threats.pdf (Page 6)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 72)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/MCP_landscape_security_threats.pdf (Page 2)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 64)



## If a user wants an AI to be able to read a static local configuration file, which MCP feature (Resource, Tool, or Prompt) should the server developer use, and why?
Based on the context, if a user wants an AI to be able to read a static local configuration file, I would recommend using the "Resource" feature.

According to the text, the Resourcestab in the Inspector UI lists available resources with MIME types and metadata, and supports content inspection. This suggests that the Resource feature is designed for reading and inspecting data from local or remote sources.

The Tool feature is used for executing tools with custom inputs, which doesn't seem directly related to reading a configuration file. The Prompt feature is used for display prompt templates, argument schemas, and on-the-fly testing with arbitrary arguments, which also doesn't match the use case of reading a static local configuration file.

Therefore, using the Resource feature would allow the AI client to read the contents of the highlighted function from the local file, as mentioned in the Context Gathering step.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 25)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 68)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 26)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 44)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/the_model_context_protocol.pdf (Page 5)



## How does MCP's user-controlled, opt-in authorization model mitigate the security risks of granting a Large Language Model access to a local filesystem?
Based on the provided context, I can help answer your question. 

MCP's user-controlled, opt-in authorization model mitigates the security risks of granting a Large Language Model (LLM) access to a local filesystem by implementing measures such as requiring authentication for every connection, limiting network bindings to trusted local clients, and using HTTPS to serve file-system access points. These precautions reduce the risk of an attacker bypassing host sandbox protections and gaining unauthorized system control.

Furthermore, by applying fine-grained permissioning, including per-tool scopes, role-based access control, and temporal policies, MCP ensures that sensitive data remains hidden from standard users while being disclosed to authorized IT operators as needed. This balance between operational utility and confidentiality helps minimize the security risks associated with granting an LLM access to a local filesystem.

Additionally, by introducing redundant LLM agents in future iterations, MCP can mitigate its dependency on external services like Copilot Studio and ensure that there is always an agent available, thereby enhancing system resilience.

--- SOURCES USED ---
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 65)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/MCP_landscape_security_threats.pdf (Page 24)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/MCP_landscape_security_threats.pdf (Page 23)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 65)
- /Users/zeynep/Development/SWE/SWE 580 - Applied Large Language Models/HW/RAG/src/../docs/agent_engineering_enterprise.pdf (Page 98)
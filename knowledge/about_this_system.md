# About This System

This local AI assistant runs entirely on-premises using Ollama.
It does not send any data to external services.

## Capabilities

- General question answering and conversation
- Searching this local knowledge base for relevant information
- Reporting system resource status via the system_info tool
- Remembering context across the current session (short-term memory)
- Retaining important facts across sessions (long-term memory)

## Privacy

All data stays local. No cloud API keys are required.
The knowledge base is a set of plain text and Markdown files in the `knowledge/` directory.

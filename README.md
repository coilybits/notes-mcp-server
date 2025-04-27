# notes-mcp-server
A Model Context Protocol (MCP) server which provides AI assistants with a secure and structured way to CRUD simple notes. The notes are persisted using [apach ignite](https://ignite.apache.org/)

# Capabilities

* `list_resources` list all notes in database 
* `read_resource` reads a note from database
* `list_tools` list tools AI assistants can access
* `call_tool` executes a tool (create note, remove note)
* `list_prompts` list of helpful prompts
* `get_prompt` view prompt

# Configuration

* `--host` the database host
* `--port` the database port

# Usage

## Continue.dev
```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "/path/to/uv",
          "args": [
            "--directory",
            "/path/to/notes-mcp-server",
            "run",
            "main.py"
          ]
        }
      }
    ]
  }
}
```


## Claude Desktop

Configure the MCP server in Claude configuration file:

```json
{
  "mcpServers": {
    "messaging": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/notes-mcp-server",
        "run",
        "main.py", "--host=127.0.0.1", "--port=10800"
      ]
    }
  }
}
```

# License

MIT License - see [LICENSE](LICENSE).

## Prerequisites
- Python with `uv` package manager
- MCP server dependencies
- Apache Ignite

## Development

```
# Clone the repository
git clone https://github.com/coilybits/notes-mcp-server.git
cd notes-mcp-server

# Create virtual environment
uv venv
source venv/bin/activate 

# Install development dependencies
uv sync

```

[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) for debugging:

```bash
npx @modelcontextprotocol/inspector uv \
--directory \
/path/to/notes-mcp-server \
run \
main.py
```
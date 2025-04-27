import logging
import sys
from typing import Iterable

from mcp import stdio_server
from mcp.server import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.types import TextContent, Resource, Tool, PromptArgument, Prompt, GetPromptResult, PromptMessage
from pydantic import AnyUrl

from models.types import Tools, NoteExistsException, NoteNotExistsException
from services.notebook import Notebook
import click


async def run(logger: logging.Logger, ipaddress: str, port: int):
    prefix = "notes://"
    notebook_server: Notebook = Notebook(ipaddress, port)
    logger.info("-----starting server-----")

    async def list_resources():
        result: list[Resource] = []
        try:
            for note in notebook_server.notes():
                result.append(Resource(uri=f"{prefix}{note[0]}",
                                       name=note[0],
                                       description=note[1],
                                       mimeType="text/plain"))
        except Exception as ex:
            logger.error(f"could not load resources: {str(ex)}")
            raise Exception("Could not load resources.")
        return result

    async def list_prompts() -> list[Prompt]:
        return [
            Prompt(
                name=Tools.CREATE_NOTE,
                description="Explain how do I create a effective note.",
                arguments=[
                    PromptArgument(
                        name="name",
                        description="Name of the note to create",
                        required=True
                    ),
                    PromptArgument(
                        name="description",
                        description="Description of contents of note",
                        required=True
                    )
                ]
            ),
            Prompt(
                name=Tools.REMOVE_NOTE,
                description="Explain how do I remove an existing note.",
                arguments=[
                    PromptArgument(
                        name="name",
                        description="Name of the note to remove",
                        required=True
                    )
                ]
            )
        ]

    async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
        logger.info(f"-----loading prompt {name}-----")
        logger.info(arguments)
        match name:
            case Tools.CREATE_NOTE:
                name = str(arguments.get("name")) if arguments else ""
                description = str(arguments.get("description")) if arguments else ""
                if name.strip() == "" or description.strip() == "":
                    raise ValueError("name and description are required")
                return GetPromptResult(
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"Create a note or create a new note {name} add {description}."
                            )
                        )
                    ]
                )
            case Tools.REMOVE_NOTE:
                name = str(arguments.get("name")) if arguments else ""
                if name.strip() == "":
                    raise ValueError("Name is required.")
                return GetPromptResult(
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"Remove note {name}"
                            )
                        )
                    ]
                )
            case _:
                raise ValueError("Invalid command.")

    async def read_resource(uri: AnyUrl) -> Iterable[ReadResourceContents]:
        result: list[ReadResourceContents] = []
        logger.error(f"loading resources for {uri}")
        try:
            x = str(uri)
            if not x.startswith(prefix):
                raise ValueError(f"Invalid URI scheme: {x}")

            p = x[len(prefix):].split("/")
            notes = notebook_server.get(p[0])
            for note in notes:
                result.append(ReadResourceContents(content=note[1], mime_type="text/plain"))
        except Exception as ex:
            logger.error(f"could not read resource: {str(ex)}")
            raise Exception(f"Could not get resource {uri}.")
        return result

    async def list_tools():
        return [
            Tool(
                name=Tools.CREATE_NOTE,
                description="Creates a new note",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["name", "description"]
                }
            ),
            Tool(
                name=Tools.REMOVE_NOTE,
                description="Removes an existing note",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            )
        ]

    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        logger.error(f"loading tool for {name}")
        name = name.strip()
        match name:
            case Tools.CREATE_NOTE:
                result = create_note(arguments.get("description"), arguments.get("name"))
                return [TextContent(
                    type="text",
                    text=f"{result}"
                )]
            case Tools.REMOVE_NOTE:
                name = arguments.get("name")
                result = remove_note(name)
                return [TextContent(
                    type="text",
                    text=f"{result}"
                )]
            case _:
                raise ValueError(f"Unknown tool: {name}")

    def remove_note(name):
        try:
            if len(notebook_server.get(name)) == 0:
                raise NoteNotExistsException(f"Note {name} does not exists.")
            notebook_server.remove(name)
        except NoteNotExistsException as nnee:
            raise nnee
        except Exception as ex:
            logger.error(f"could not remove note {str(ex)}")
            raise Exception(f"Issue occurred removing note {name}.  Please try again.")
        return f"Note {name} removed."

    def create_note(description, name):
        try:
            if len(notebook_server.get(name)) != 0:
                raise NoteExistsException(f"Note {name} already exists.")
            notebook_server.create(name, description)
        except NoteExistsException as nee:
            raise nee
        except Exception as ex:
            logger.error(f"could not create note {str(ex)}")
            raise Exception(f"Issue occurred creating note {name}.  Please try again.")
        return f"Note {name} created."

    server = Server("notebook-server", version="1.0.0")

    server.list_resources()(list_resources)
    server.read_resource()(read_resource)
    server.list_tools()(list_tools)
    server.call_tool()(call_tool)
    server.list_prompts()(list_prompts)
    server.get_prompt()(get_prompt)

    async with stdio_server() as (read_stream, write_stream):
        try:
            await server.run(read_stream, write_stream, server.create_initialization_options(),
                             raise_exceptions=True)
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise


@click.command()
@click.option('--host', default="127.0.0.1", help='apache ignite ip address.')
@click.option('--port', default=10800, help='apache ignite port.')
def main(host: str, port: int):
    import asyncio

    lgr = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    asyncio.run(run(lgr, host, port))


if __name__ == "__main__":
    main()

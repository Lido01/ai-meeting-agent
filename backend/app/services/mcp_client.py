import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


BACKEND_DIR = Path(__file__).resolve().parents[2]

load_dotenv(dotenv_path=BACKEND_DIR / ".env")


MCP_TOOL_NAME = "get_meeting_context"


class MCPClientError(Exception):
    """Raised when the MCP protocol client cannot retrieve context."""


def _server_env() -> dict[str, str]:
    env: dict[str, str] = {
        "PYTHONPATH": str(BACKEND_DIR),
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
    }

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        env["DATABASE_URL"] = database_url

    return env


def _parse_json_documents(text: str) -> object:
    decoder = json.JSONDecoder()
    documents = []
    offset = 0
    raw = (text or "").strip()

    while offset < len(raw):
        while offset < len(raw) and raw[offset].isspace():
            offset += 1

        if offset >= len(raw):
            break

        try:
            value, end = decoder.raw_decode(raw, offset)
        except json.JSONDecodeError:
            break

        documents.append(value)
        offset = end

    if not documents:
        return raw

    if len(documents) == 1:
        return documents[0]

    return documents


def _extract_tool_payload(result) -> object:
    if getattr(result, "is_error", False):
        raise MCPClientError("MCP tool returned an error.")

    structured = getattr(result, "structured_content", None)
    if isinstance(structured, list):
        return structured

    parsed_parts = []
    for item in getattr(result, "content", None) or []:
        text = getattr(item, "text", None)
        if not text:
            continue

        parsed = _parse_json_documents(text)
        if isinstance(parsed, list):
            parsed_parts.extend(parsed)
        else:
            parsed_parts.append(parsed)

    if parsed_parts:
        if all(isinstance(part, dict) for part in parsed_parts):
            return parsed_parts
        if len(parsed_parts) == 1:
            return parsed_parts[0]
        return parsed_parts

    if structured is not None:
        return structured

    return []


async def retrieve_meeting_context(
    user_id: int,
    query: str = "",
    limit: int = 5
):
    """
    Call the MCP server over stdio and invoke get_meeting_context.

    This spawns `python -m app.mcp.server` as a subprocess and uses
    the MCP protocol. It does not query PostgreSQL directly.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
        cwd=str(BACKEND_DIR),
        env=_server_env(),
    )

    print(
        "===== MCP CLIENT: spawning stdio server ====="
    )
    print(
        f"tool={MCP_TOOL_NAME} user_id={user_id} query={query!r}"
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                tool_names = [
                    tool.name for tool in tools.tools
                ]

                print("===== MCP CLIENT: tools =====")
                print(tool_names)

                if MCP_TOOL_NAME not in tool_names:
                    raise MCPClientError(
                        "MCP server did not expose get_meeting_context."
                    )

                result = await session.call_tool(
                    MCP_TOOL_NAME,
                    arguments={
                        "user_id": user_id,
                        "query": query or "",
                        "limit": limit,
                    },
                    read_timeout_seconds=30,
                )

                payload = _extract_tool_payload(result)

                print("===== MCP CLIENT: context received =====")
                if isinstance(payload, list):
                    print(f"meetings={len(payload)}")
                else:
                    print(type(payload).__name__)

                return payload

    except MCPClientError:
        raise
    except Exception as exc:
        raise MCPClientError(
            "Could not complete the MCP retrieval."
        ) from exc

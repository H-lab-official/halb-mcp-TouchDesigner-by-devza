"""Local stdio MCP server; TouchDesigner uses no third-party packages or sockets."""
import asyncio
import json
import os
from pathlib import Path
import time
import uuid

from mcp.server.fastmcp import FastMCP, Image

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / 'queue'
QUEUE.mkdir(parents=True, exist_ok=True)
mcp = FastMCP('TouchDesigner Local Control')


def heartbeat():
    try:
        value = json.loads((QUEUE / 'heartbeat.json').read_text(encoding='utf-8'))
    except (FileNotFoundError, ValueError):
        raise RuntimeError('TouchDesigner bridge is not installed. Run install_td.py in its Python Textport.')
    if time.time() - value['time'] > 8:
        raise RuntimeError('TouchDesigner bridge is offline or not processing frames. Open the bridged project.')
    return value


async def request(action, args=None):
    state = heartbeat()
    ident = uuid.uuid4().hex
    payload = {'id': ident, 'action': action, 'args': args or {},
               'session': state['session'], 'expires': time.time() + 25}
    final = QUEUE / (ident + '.request.json')
    temp = QUEUE / (ident + '.tmp')
    response = QUEUE / (ident + '.response.json')
    temp.write_text(json.dumps(payload), encoding='utf-8')
    os.replace(temp, final)
    deadline = time.monotonic() + 30
    try:
        while time.monotonic() < deadline:
            if response.exists():
                reply = json.loads(response.read_text(encoding='utf-8'))
                response.unlink()
                if not reply['ok']:
                    raise RuntimeError(reply['error'] + '\n' + reply.get('traceback', ''))
                return reply['result']
            await asyncio.sleep(0.05)
        raise TimeoutError('TouchDesigner did not respond. Operation outcome is unknown; inspect before retrying mutations.')
    finally:
        final.unlink(missing_ok=True)


@mcp.tool()
def connection_status() -> dict:
    """Check the current bridge heartbeat without changing the project."""
    return heartbeat()


@mcp.tool()
async def get_project() -> dict:
    """Inspect the active TouchDesigner project and its root operators."""
    return await request('get_project')


@mcp.tool()
async def list_nodes(path: str = '/project1', depth: int = 1, limit: int = 200) -> dict:
    """List operators beneath an absolute component path (depth 1-6)."""
    return await request('list_nodes', dict(path=path, depth=depth, limit=limit))


@mcp.tool()
async def get_node(path: str, parameters: list[str] | None = None) -> dict:
    """Read a node's parameters, connections, errors and DAT text. Parameter names may use TD wildcards."""
    return await request('get_node', dict(path=path, parameters=parameters))


@mcp.tool()
async def create_node(parent: str, operator_type: str, name: str) -> dict:
    """Create an operator, e.g. noiseTOP, levelTOP, textDAT or baseCOMP. Refuses existing names."""
    return await request('create_node', dict(parent=parent, operator_type=operator_type, name=name))


@mcp.tool()
async def set_parameters(path: str, values: dict) -> dict:
    """Set parameter values or {expression: '...'} objects; returns previous values."""
    return await request('set_parameters', dict(path=path, values=values))


@mcp.tool()
async def pulse_parameter(path: str, parameter: str) -> dict:
    """Pulse an action parameter. Check its meaning before using it."""
    return await request('pulse_parameter', dict(path=path, parameter=parameter))


@mcp.tool()
async def connect_nodes(source: str, target: str, input_index: int = 0, output_index: int = 0) -> dict:
    """Connect two operators; replaces any connection at the selected input."""
    return await request('connect_nodes', dict(source=source, target=target,
                         input_index=input_index, output_index=output_index))


@mcp.tool()
async def set_dat_text(path: str, text: str) -> dict:
    """Replace a DAT's text and return its previous text. Executable DATs may run immediately."""
    return await request('set_dat_text', dict(path=path, text=text))


@mcp.tool()
async def execute_python(code: str) -> dict:
    """Execute trusted Python on TouchDesigner's main thread with full application/local-file access.

    Use only for the user's requested work. Available: op, ops, project, app, ui, me.
    Set result to a JSON-compatible value; stdout is returned. Do not run long/blocking loops.
    """
    return await request('execute_python', dict(code=code))


@mcp.tool()
async def save_project(file_path: str, overwrite: bool = False) -> dict:
    """Save the project to an absolute .toe path; existing files require explicit overwrite=true."""
    return await request('save_project', dict(file_path=file_path, overwrite=overwrite))


@mcp.tool()
async def snapshot_top(path: str) -> Image:
    """Capture a TOP output as an image for visual inspection."""
    reply = await request('snapshot_top', dict(path=path))
    image_path = Path(reply['file_path']).resolve()
    if image_path.parent != (ROOT / 'previews').resolve():
        raise RuntimeError('Unexpected preview path')
    try:
        return Image(data=image_path.read_bytes(), format='png')
    finally:
        image_path.unlink(missing_ok=True)


if __name__ == '__main__':
    mcp.run(transport='stdio')

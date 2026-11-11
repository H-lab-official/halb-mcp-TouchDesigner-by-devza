"""Run this once in TouchDesigner's Python Textport."""
from pathlib import Path
import shutil
import datetime
from td import baseCOMP, textDAT, executeDAT

root = Path(__file__).resolve().parent if '__file__' in globals() else Path('D:/MCP/TD')
existing = op('/codex_mcp')
if existing is not None and 'codex-mcp-bridge' not in existing.tags:
    raise RuntimeError('/codex_mcp already exists and is not our bridge')
source = Path(project.folder) / project.name
if source.is_file():
    backups = root / 'backups'
    backups.mkdir(exist_ok=True)
    backup = backups / (source.stem + '-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.toe')
    shutil.copy2(source, backup)
    print('Original project file backed up:', backup)
comp = existing or op('/').create(baseCOMP, 'codex_mcp')
comp.tags.add('codex-mcp-bridge')
comp.nodeX = -600
comp.nodeY = 300
bridge = comp.op('bridge') or comp.create(textDAT, 'bridge')
bridge.text = 'BRIDGE_ROOT = ' + repr(str(root)) + '\n' + (root / 'td_runtime.py').read_text(encoding='utf-8')
callbacks = comp.op('callbacks') or comp.create(executeDAT, 'callbacks')
callbacks.par.active = False
callbacks.text = '''def onStart():
    parent().op('bridge').module.tick()
    return

def onFrameStart(frame):
    parent().op('bridge').module.tick()
    return
'''
callbacks.par.start = True
callbacks.par.framestart = True
callbacks.par.active = True
bridge.module.tick()
print('TouchDesigner MCP connected. Save your project to retain /codex_mcp after reopening.')

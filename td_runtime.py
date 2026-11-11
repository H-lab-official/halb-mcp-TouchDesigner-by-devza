"""Runs inside TouchDesigner, exclusively on the application's main thread."""
import contextlib
import io
import json
import os
from pathlib import Path
import time
import traceback
import uuid

ROOT = Path(globals().get('BRIDGE_ROOT') or os.environ.get('TD_MCP_HOME') or
            (Path(__file__).resolve().parent if '__file__' in globals() else project.folder))
QUEUE = ROOT / 'queue'
QUEUE.mkdir(parents=True, exist_ok=True)
SESSION = uuid.uuid4().hex
_last_tick = 0.0
_last_heartbeat = 0.0


def atomic_json(path, value):
    temp = path.with_suffix('.tmp-' + uuid.uuid4().hex)
    temp.write_text(json.dumps(value, default=str), encoding='utf-8')
    os.replace(str(temp), str(path))


def node(path):
    if not isinstance(path, str) or not path.startswith('/'):
        raise ValueError('Use an absolute operator path, e.g. /project1/noise1')
    result = op(path)
    if result is None:
        raise ValueError('Operator does not exist: ' + path)
    return result


def summary(n):
    return {'path': n.path, 'type': n.OPType, 'family': n.family,
            'name': n.name, 'position': [n.nodeX, n.nodeY]}


def dispatch(action, args):
    if action == 'get_project':
        return {'name': project.name, 'folder': project.folder,
                'version': str(app.version), 'build': str(app.build),
                'roots': [summary(n) for n in op('/').children], 'session': SESSION}
    if action == 'list_nodes':
        root = node(args.get('path', '/project1'))
        depth = max(1, min(int(args.get('depth', 1)), 6))
        limit = max(1, min(int(args.get('limit', 200)), 2000))
        result = []
        pending = [(root, 0)]
        while pending:
            current, level = pending.pop(0)
            if level >= depth:
                continue
            for child in getattr(current, 'children', []):
                if len(result) >= limit:
                    return {'nodes': result, 'truncated': True}
                result.append(summary(child))
                pending.append((child, level + 1))
        return {'nodes': result, 'truncated': False}
    if action == 'get_node':
        n = node(args['path'])
        result = summary(n)
        names = args.get('parameters')
        pars = n.pars(*names) if names else n.pars()
        result['parameters'] = [{'name': p.name, 'label': p.label, 'value': str(p.eval()),
                                 'mode': str(p.mode), 'expression': p.expr,
                                 'menu_names': list(p.menuNames) if p.isMenu else []}
                                for p in pars]
        result['inputs'] = [i.path if i else None for i in n.inputs]
        result['errors'] = n.errors()
        result['warnings'] = n.warnings()
        if n.family == 'DAT':
            result['text'] = n.text[:100000]
        return result
    if action == 'create_node':
        parent_op = node(args['parent'])
        name = args['name']
        if not name or '/' in name or parent_op.op(name) is not None:
            raise ValueError('Choose a new, unused operator name')
        import td
        operator_type = getattr(td, args['operator_type'], None)
        if operator_type is None:
            raise ValueError('Unknown operator class: ' + args['operator_type'])
        created = parent_op.create(operator_type, name)
        return summary(created)
    if action == 'set_parameters':
        n = node(args['path'])
        changes = args['values']
        for name, value in changes.items():
            p = getattr(n.par, name, None)
            if p is None:
                raise ValueError('Unknown parameter: ' + name)
            if p.isPulse:
                raise ValueError('Use pulse_parameter for pulse parameters')
            if isinstance(value, dict) and set(value) != {'expression'}:
                raise ValueError('Expression objects must contain only expression')
        before = {name: {'value': str(getattr(n.par, name).eval()),
                         'mode': str(getattr(n.par, name).mode),
                         'expression': getattr(n.par, name).expr} for name in changes}
        for name, value in changes.items():
            p = getattr(n.par, name)
            if isinstance(value, dict):
                p.expr = value['expression']
            else:
                p.val = value
        return {'path': n.path, 'before': before, 'changed': list(changes)}
    if action == 'pulse_parameter':
        p = getattr(node(args['path']).par, args['parameter'], None)
        if p is None or not p.isPulse:
            raise ValueError('Not a pulse parameter')
        p.pulse()
        return {'pulsed': args['parameter']}
    if action == 'connect_nodes':
        source = node(args['source'])
        target = node(args['target'])
        target.inputConnectors[int(args.get('input_index', 0))].connect(
            source.outputConnectors[int(args.get('output_index', 0))])
        return {'source': source.path, 'target': target.path}
    if action == 'set_dat_text':
        n = node(args['path'])
        if n.family != 'DAT':
            raise ValueError('Target must be a DAT')
        before = n.text
        n.text = args['text']
        return {'path': n.path, 'previous_text': before, 'characters': len(n.text)}
    if action == 'execute_python':
        scope = {'op': op, 'ops': ops, 'project': project, 'app': app,
                 'ui': ui, 'me': me, 'result': None}
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(compile(args['code'], '<touchdesigner-mcp>', 'exec'), scope, scope)
        return {'stdout': output.getvalue()[:100000], 'result': scope.get('result')}
    if action == 'save_project':
        dest = Path(args['file_path'])
        if not dest.is_absolute() or dest.suffix.lower() != '.toe':
            raise ValueError('Provide an absolute .toe path')
        if dest.exists() and not args.get('overwrite', False):
            raise ValueError('File exists; use a new path or explicitly set overwrite=true')
        dest.parent.mkdir(parents=True, exist_ok=True)
        saved = project.save(str(dest))
        if not saved:
            raise RuntimeError('TouchDesigner did not save the project')
        return {'saved': str(dest), 'exists': dest.exists()}
    if action == 'snapshot_top':
        n = node(args['path'])
        if n.family != 'TOP':
            raise ValueError('Target must be a TOP')
        dest = ROOT / 'previews' / (uuid.uuid4().hex + '.png')
        dest.parent.mkdir(exist_ok=True)
        n.save(str(dest))
        return {'file_path': str(dest)}
    raise ValueError('Unknown action: ' + action)


def tick():
    global _last_tick, _last_heartbeat
    now = time.time()
    if now - _last_tick < 0.05:
        return
    _last_tick = now
    if now - _last_heartbeat >= 1:
        atomic_json(QUEUE / 'heartbeat.json', {'time': now, 'session': SESSION,
                    'project': project.name, 'folder': project.folder,
                    'pid': os.getpid()})
        _last_heartbeat = now
    for path in sorted(QUEUE.glob('*.request.json'))[:1]:
        request = None
        claimed = path.with_suffix('.working')
        try:
            path.rename(claimed)
            request = json.loads(claimed.read_text(encoding='utf-8'))
            ident = request['id']
            if ident != path.name.split('.')[0] or len(ident) != 32:
                raise ValueError('Invalid request id')
            if request['expires'] < now or request['session'] != SESSION:
                raise ValueError('Expired request or changed TouchDesigner session; no action taken')
            result = dispatch(request['action'], request.get('args', {}))
            reply = {'ok': True, 'result': result}
        except Exception as exc:
            reply = {'ok': False, 'error': str(exc), 'traceback': traceback.format_exc()[-6000:]}
        if request and request.get('id') == path.name.split('.')[0]:
            atomic_json(QUEUE / (path.name.split('.')[0] + '.response.json'), reply)
        claimed.unlink(missing_ok=True)

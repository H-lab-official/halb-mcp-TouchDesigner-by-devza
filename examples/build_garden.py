"""Build the demo from a plain-text manifest; contains no personal .toe data."""
import json
from pathlib import Path


def build(repo_root, parent_path='/project1', name='Flower_Person', activate=True):
    import td
    root=Path(repo_root).resolve()
    data=json.loads((root/'examples/flower_person.json').read_text(encoding='utf-8'))
    parent=td.op(parent_path)
    if parent is None:
        raise RuntimeError('Open a project with '+parent_path+' first')
    if not name or '/' in name or parent.op(name) is not None:
        raise RuntimeError('Choose a new component name; '+name+' already exists')
    c=parent.create(td.baseCOMP,name)
    c.nodeX=850; c.nodeY=-500
    c.store('asset_root',str(root))
    pages={}
    for item in data['custom_parameters']:
        if item['page'] not in pages:
            pages[item['page']]=c.appendCustomPage(item['page'])
        page=pages[item['page']]
        method={'Float':'appendFloat','Toggle':'appendToggle','File':'appendFile'}[item['style']]
        p=getattr(page,method)(item['name'],label=item['label'])[0]
        p.default=item['value']; p.val=item['value']
        if item['style']=='Float':
            p.min=item['minimum']; p.max=item['maximum']
            p.normMin=p.min; p.normMax=p.max; p.clampMin=True; p.clampMax=True
    for item in data['nodes']:
        n=c.op(item['name']) or c.create(getattr(td,item['type']),item['name'])
        n.nodeX=item['x']; n.nodeY=item['y']
        if 'vectors' in item:
            n.seq.vec.numBlocks=item['vectors']
    for item in data['nodes']:
        n=c.op(item['name'])
        for name,value in item['params'].items():
            p=getattr(n.par,name,None)
            if p is None:
                raise RuntimeError(n.path+' has no parameter '+name)
            if isinstance(value,dict):
                p.expr=value['expression']
            else:
                p.val=value
        if 'text' in item:
            n.text=item['text']
    for item in data['nodes']:
        n=c.op(item['name'])
        for index,source in enumerate(item['inputs']):
            n.inputConnectors[index].connect(c.op(source).outputConnectors[0])
    c.op('interaction_logic').text=(root/'interaction_logic.py').read_text(encoding='utf-8')
    c.par.Backgroundimage=str(root/'assets/landscape_lake.png')
    if activate:
        camera=c.op('camera1')
        devices=list(camera.par.device.menuNames or [])
        labels=list(camera.par.device.menuLabels or [])
        # Prefer a physical USB camera; virtual cameras remain selectable manually.
        selected=next((d for d in devices if 'usb#' in d.lower()),None)
        if selected is None:
            selected=next((d for d,label in zip(devices,labels) if 'webcam' in label.lower() and 'utility' not in label.lower()),None)
        if selected:
            camera.par.device=selected
        camera.par.active=True
        c.op('interaction_tick').par.active=True
        c.op('OUT').viewer=True
        c.op('OUT').openViewer()
    return c

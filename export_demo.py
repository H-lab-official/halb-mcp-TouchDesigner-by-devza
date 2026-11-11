"""Execute in TouchDesigner to export a camera-neutral, text-only example."""
from pathlib import Path
import json

c=op('/project1/Flower_Person')
root=Path(c.fetch('asset_root',project.folder))
(root/'examples').mkdir(exist_ok=True)

def plain(value):
    if isinstance(value,(str,int,float,bool)) or value is None:
        return value
    if hasattr(value,'path'):
        path=value.path
        return path.replace(c.path+'/','') if path.startswith(c.path+'/') else path
    return str(value)

custom=[]
for p in c.customPars:
    item={'name':p.name,'label':p.label,'style':p.style,'page':p.page.name,'value':plain(p.eval())}
    if p.style=='Float':item.update(minimum=p.min,maximum=p.max)
    custom.append(item)
nodes=[]
for n in c.children:
    if n.name=='body_tracking':continue
    params={}
    for p in n.pars():
        if p.isPulse or getattr(p,'readOnly',False) or p.name=='device' or p.style=='Sequence':continue
        if str(p.mode)=='ParMode.EXPRESSION':
            params[p.name]={'expression':p.expr}
        else:
            val=plain(p.val)
            if val!=plain(p.default) and isinstance(val,(str,int,float,bool)):
                params[p.name]=val
    if n.name in ['camera1','interaction_tick']:params['active']=False
    item={'name':n.name,'type':n.OPType,'x':n.nodeX,'y':n.nodeY,'params':params,'inputs':[src.name for src in n.inputs]}
    if n.family=='DAT' and n.OPType in ['textDAT','executeDAT']:item['text']=n.text
    if n.OPType=='glslTOP':item['vectors']=n.seq.vec.numBlocks
    nodes.append(item)
data={'schema':1,'component':'Flower_Person','custom_parameters':custom,'nodes':nodes}
path=root/'examples/flower_person.json'
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for name,dest in [('flower_shader','flower_person_interactive.frag'),('particle_sim','particle_trails_interactive.frag')]:
    (root/dest).write_text(c.op(name).par.pixeldat.eval().text,encoding='utf-8')
result={'manifest':str(path),'nodes':len(nodes)}

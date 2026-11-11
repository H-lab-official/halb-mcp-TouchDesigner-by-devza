"""Main-thread gesture controller. All camera inference stays on this computer."""
import math
import time
import json
import os
from pathlib import Path
import subprocess
_state={'tracked':0.,'stillness':0.,'burst':0.,'hue':0.,'growth':0.,'motion':0.,
        'left_x':.35,'left_y':.5,'right_x':.65,'right_y':.5,'left_valid':0.,'right_valid':0.,
        'ls_x':.4,'ls_y':.6,'le_x':.35,'le_y':.5,'rs_x':.6,'rs_y':.6,'re_x':.65,'re_y':.5,
        'center_x':.5,'center_y':.55}
_prev={}
_filtered={}
_worker=None
_worker_log=None
_last=0.
_status_time=0.

def value(key,default=0.):
    return _state.get(key,default)

def advance(points,dt,sensitivity=1.0,bloom_time=3.0):
    global _prev,_filtered
    dt=max(.005,min(.15,dt))
    blend=1.-math.exp(-dt*8.)
    _filtered={joint:tuple(old+(new-old)*blend for old,new in zip(_filtered.get(joint,p),p)) for joint,p in points.items()}
    points=dict(_filtered)
    tracked=bool(points.get('shoulder_l') or points.get('shoulder_r'))
    speeds={}
    for joint,point in points.items():
        if joint in _prev:
            speeds[joint]=min(3.,math.dist(point,_prev[joint])/dt)
    _prev=dict(points)
    wrist_speed=max(speeds.get('wrist_l',0.),speeds.get('wrist_r',0.))
    motion=max([speeds.get(j,0.) for j in ['wrist_l','wrist_r','elbow_l','elbow_r','shoulder_l','shoulder_r']]+[0.])
    signal=max(0.,min(1.,(wrist_speed-.18)*sensitivity*1.4)) if tracked else 0.
    _state['burst']=max(_state['burst']*math.exp(-dt*2.5),signal)
    _state['motion']+=(min(1.,motion)-_state['motion'])*(1.-math.exp(-dt*8.))
    if tracked and motion < .12/max(.25,sensitivity):
        _state['stillness']=min(1.,_state['stillness']+dt/max(.5,bloom_time))
    else:
        _state['stillness']=max(0.,_state['stillness']-dt*1.5)
    _state['tracked']=1. if tracked else 0.
    _state['growth']=min(1.,_state['growth']+dt/4.) if tracked else max(0.,_state['growth']-dt)
    for side,prefix in [('l','left'),('r','right')]:
        wrist=points.get('wrist_'+side)
        _state[prefix+'_valid']=1. if wrist else 0.
        _state[prefix+'_arm_valid']=1. if wrist and 'elbow_'+side in points and 'shoulder_'+side in points else 0.
        if wrist:
            for axis,val in zip(['x','y'],wrist):
                key=prefix+'_'+axis
                _state[key]+=(val-_state[key])*(1.-math.exp(-dt*12.))
        for joint,key in [('shoulder_',side+'s'),('elbow_',side+'e')]:
            point=points.get(joint+side)
            if point:
                for axis,val in zip(['x','y'],point):
                    k=key+'_'+axis
                    _state[k]+=(val-_state[k])*(1.-math.exp(-dt*12.))
    wrists=[p for j,p in points.items() if j.startswith('wrist_')]
    target_hue=(sum(p[1] for p in wrists)/len(wrists)-.5)*.65 if wrists else 0.
    _state['hue']+=(target_hue-_state['hue'])*(1.-math.exp(-dt*3.))
    shoulders=[p for j,p in points.items() if j.startswith('shoulder_')]
    if shoulders:
        _state['center_x']=sum(p[0] for p in shoulders)/len(shoulders)
        _state['center_y']=sum(p[1] for p in shoulders)/len(shoulders)+.08
    return dict(_state)

def read_points(chop):
    channels={ch.name.lower().replace(':','_').replace('/','_'):float(ch[0]) for ch in chop.chans()}
    points={}
    for joint in ['shoulder_l','shoulder_r','elbow_l','elbow_r','wrist_l','wrist_r']:
        stem,side=joint.rsplit('_',1)
        aliases=[joint,('left_' if side=='l' else 'right_')+stem,stem+('_left' if side=='l' else '_right')]
        values={}
        for name,v in channels.items():
            if not any(a in name for a in aliases):continue
            tail=name.rsplit('_',1)[-1]
            if tail in ['u','x','tx']:values['x']=v
            if tail in ['v','y','ty']:values['y']=v
            if tail in ['confidence','conf','c']:values['confidence']=v
        if 'x' in values and 'y' in values and values.get('confidence',1.)>=.25:
            x,y=values['x'],values['y']
            if -.15<x<1.15 and -.15<y<1.15:points[joint]=(x,y)
    return points

def tick():
    global _last,_status_time,_worker,_worker_log
    now=time.perf_counter()
    if _last and now-_last<1./15.:return
    dt=now-_last if _last else 1./30.
    _last=now
    comp=me.parent()
    root=Path(comp.fetch('asset_root', project.folder))
    runtime=root/'runtime_pose'
    runtime.mkdir(exist_ok=True)
    points={}
    fresh=False
    try:
        data=json.loads((runtime/'pose.json').read_text(encoding='utf-8'))
        fresh=time.time()-data['time']<1.5
        if fresh: points={j:tuple(p) for j,p in data['points'].items()}
    except (OSError,ValueError,KeyError): pass
    if not fresh and (_worker is None or _worker.poll() is not None):
        python=root/'.pose-venv/Scripts/python.exe'
        script=root/'pose_worker.py'
        if python.exists() and script.exists():
            if _worker_log: _worker_log.close()
            _worker_log=(runtime/'worker.log').open('ab')
            _worker=subprocess.Popen([str(python),str(script),'--root',str(root)],
                 stdin=subprocess.DEVNULL,stdout=_worker_log,stderr=_worker_log,
                 creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    source=comp.op('pose_input')
    if source is not None:
        temp=runtime/'frame.incoming.png'
        try:
            source.save(str(temp))
            os.replace(temp,runtime/'frame.png')
        except OSError: pass
    advance(points,dt,comp.par.Gesturesensitivity.eval(),comp.par.Stillbloomtime.eval())
    if now-_status_time>.25:
        table=comp.op('interaction_status')
        table.clear();table.appendRow(['signal','value'])
        for key in ['tracked','motion','burst','stillness','hue','growth','left_valid','right_valid']:
            table.appendRow([key,round(_state[key],3)])
        _status_time=now

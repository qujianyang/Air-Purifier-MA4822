import sys,runpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.argv=['cad_assembly.py','--step-only']
m=runpy.run_path(str(ROOT/'cad_assembly.py'),run_name='acceptance_checks')
results={}
for config in ['household','bench']:
 m['build'](config)
 # Function global dictionary holds the live parts list after build.
 parts=m['build'].__globals__['parts'];by={p['name']:p['shape'] for p in parts}
 def shape(prefix):return next(s for n,s in by.items() if n.startswith(prefix))
 bell=shape('A07');deck=shape('A04');ring=shape('A09');cq=m['cq']
 taps=[shape('A08 throat static tap '+str(i)) for i in range(4)]
 gaps=[t.distance(ring) for t in taps]
 assert max(gaps)<1e-6,gaps
 assert bell.intersect(deck).Volume()<1e-5
 assert bell.isInside((281,130,392)) and not bell.isInside((0,0,500))
 assert not bell.isInside((200,130,390))
 # The static bores and annular gallery must remain open, rather than a solid ring.
 bore=[]
 for i in range(4):
  th=i*math.pi/2
  probe=m['radial_cyl'](79,11,.3,th,390)
  v=bell.intersect(probe).Volume()+taps[i].intersect(probe).Volume()+ring.intersect(probe).Volume()
  bore.append(v)
 assert max(bore)<1e-5,bore
 assert not ring.isInside((200+90/math.sqrt(2),130+90/math.sqrt(2),390))
 connections={}
 for key,a,b in [('reference_T','P04','P02'),('reference_port','P04','E02G flow plenum'),('throat_port','P05','E02G flow throat'),('manifold_outlet','P05','A09')]:
  gap=shape(a).distance(shape(b));assert gap<1e-6,(key,gap);connections[key]=gap
 tube_wire=[]
 for p in parts:
  if p['name'].startswith(('P04','P05')):
   for q in parts:
    if q['group']=='wiring':
     gap=p['shape'].distance(q['shape']);tube_wire.append(gap)
 assert min(tube_wire)>0,min(tube_wire)
 check=json.loads((ROOT/'generated'/config/'cad_checks.json').read_text())
 assert check['all_valid'] and check['all_parts_within_envelope'] and check['step_roundtrip_valid'] and not check['unexpected_interferences']
 results[config]={'tap_to_manifold_max_gap_mm':max(gaps),'four_static_bores_clear':True,'gallery_hollow':True,'deck_to_bell_intersection_mm3':bell.intersect(deck).Volume(),'pressure_connection_gaps_mm':connections,'new_pressure_tubes_to_wiring_min_clearance_mm':min(tube_wire),'shape_and_step_checks_pass':True}
(ROOT/'geometry_acceptance.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))

"""Parametric packaging study. Millimetres; front is -Y; Z is vertical.

Run with CadQuery 2.6.1. Neutral STEP and the three report views share parts.
Fan and sensor solids are clearance envelopes, not supplier CAD models.
"""
from pathlib import Path
import sys, json, math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tmp/cad_runtime'))
import cadquery as cq
import vtk
from PIL import Image, ImageDraw, ImageFont
import numpy as np

OUT=ROOT/'generated/sensors'; OUT.mkdir(parents=True,exist_ok=True)
parts=[]
def box(x,y,z,w,d,h):
    return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z)).val()
def cyl(x,y,z,r,h):
    return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z)).val()
def ring(x,y,z,w,d,h,b):
    return box(x,y,z,w,d,h).cut(box(x+b,y+b,z-1,w-2*b,d-2*b,h+2))
def add(name,shape,col=(.73,.76,.78),group='internal',move=(0,0,0),sensor=None):
    assert shape.isValid(),name
    parts.append(dict(name=name,shape=shape,color=col,group=group,move=move,sensor=sensor))
    return shape
def pipe(name,pts,r=2,col=(.15,.38,.54),group='pressure_tube'):
    solids=[]
    for a,b in zip(pts,pts[1:]):
        v=cq.Vector(*b).sub(cq.Vector(*a))
        solids.append(cq.Solid.makeCylinder(r,v.Length,cq.Vector(*a),v.normalized()))
    add(name,cq.Compound.makeCompound(solids),col,group)
def wire(name,pts,col=(.2,.24,.27)):
    pipe(name,pts,1.1,col,'wiring')
def board(name,x,y,z,w,h,col=(.11,.4,.30),group='electronics'):
    sh=box(x,y,z,w,1.6,h)
    for xx,zz in [(x+4,z+4),(x+w-4,z+4),(x+4,z+h-4),(x+w-4,z+h-4)]:
        sh=sh.cut(cq.Solid.makeCylinder(1.2,3,cq.Vector(xx,y-.5,zz),cq.Vector(0,1,0)))
        add(name+' nylon standoff '+str((xx,zz)),cq.Solid.makeCylinder(2.4,4,cq.Vector(xx,y-4,zz),cq.Vector(0,1,0)),(.78,.78,.73),group)
    add(name,sh,col,group)

# Housing: service cover replaces the lower front wall; rear tray is independent.
shell=box(0,0,10,400,300,630).cut(box(4,4,14,392,292,630))
shell=shell.cut(box(8,-1,50,384,7,340))
shell=shell.cut(box(40,-1,402,320,7,205))
shell=shell.cut(box(8,295,40,384,7,570))
add('H01 cabinet shell',shell,(.78,.81,.82),'housing')
panel=box(8,0,50,384,4,340)
for z in range(70,171,14): panel=panel.cut(box(30,-1,z,340,7,7))
panel=panel.cut(box(156,-1,352,88,7,12))
add('H02 removable inlet and service cover',panel,(.85,.87,.87),'cover',(-430,0,0))
add('H03 upper front fascia',box(40,0,402,320,4,205).cut(box(115,-1,550,170,7,36)),(.81,.84,.85),'housing')
add('H04 top plate',box(0,0,640,400,300,10).cut(box(125,80,639,150,100,12)),(.75,.79,.8),'housing')
for i in range(7): add(f'H05 outlet guard {i}',box(125+i*23,80,641,4,100,7),(.25,.3,.33),'housing')
add('H06 display bezel',box(115,0,550,170,5,36),(.12,.17,.2),'housing')
for i,(x,y) in enumerate([(25,25),(355,25),(25,255),(355,255)]):
    add(f'H07 foot {i}',box(x,y,0,20,20,10),(.15,.17,.18),'housing')
add('H08 rear electronics partition',box(5,255,14,390,4,625),(.6,.64,.66))
add('H09 removable rear electronics cover',box(8,296,40,384,4,570),(.75,.79,.80),'housing')
board('E01 controller PCB',200,263,455,140,90)
add('E01A controller processor',box(260,264.6,490,20,4,20),(.10,.12,.14),'electronics',sensor='controller')
for x,z in [(215,465),(215,525),(300,465),(300,525)]:
    add(f'E01B controller connector {x} {z}',box(x,264.6,z,18,10,8),(.74,.74,.68),'electronics')
board('E02 pressure conditioning PCB',275,263,295,90,80,(.13,.42,.33))
add('E02A raw differential pressure module allowance',box(310,265,325,30,17,20),(.20,.30,.44),'electronics',sensor='pressure')
for x,tag in [(318,'Pplus'),(332,'Pminus')]:
    port=cq.Solid.makeCylinder(3,8,cq.Vector(x,275,317),cq.Vector(0,0,1)).cut(cq.Solid.makeCylinder(1.7,9,cq.Vector(x,275,316.5),cq.Vector(0,0,1)))
    add('E02B '+tag+' pressure nipple',port,(.58,.62,.66),'electronics')
add('E02C INA333 conditioning IC',box(286,264.6,351,8,3,8),(.12,.14,.16),'electronics')
for x in [302,310,318]:add('E02D passives '+str(x),box(x,264.6,355,4,2,2),(.64,.57,.42),'electronics')
add('E02E pressure electrical header',box(280,264.6,300,16,10,8),(.77,.77,.69),'electronics')
board('E04 DC conversion PCB allowance',70,263,90,80,45,(.13,.38,.40))
add('E04A DC converter inductor allowance',box(95,264.6,104,12,10,12),(.20,.22,.24),'electronics')
add('E04B low voltage input terminal',box(85,278,70,22,18,12),(.2,.4,.55),'electronics')
add('E03 cover interlock body',box(345,9,362,20,15,14),(.76,.49,.14),'switch',sensor='cover_switch')
add('E03A interlock lever',box(350,4,372,15,8,1),(.42,.48,.52),'switch')

# Horizontal cartridge and separate, compressed gasket on the fixed seat.
frame=ring(20,15,220,360,230,60,10)
add('F01 removable cartridge frame',frame,(.35,.4,.42),'cartridge',(0,-300,-4))
add('F02 pleated media envelope',box(30,25,224,340,210,52),(.89,.83,.62),'cartridge',(0,-300,-4))
for x in range(34,369,12):
    add(f'F03 pleat indication {x}',box(x,26,275,1,208,1),(.62,.56,.39),'cartridge',(0,-300,-4))
add('F04 pull handle',box(150,7,240,100,8,18),(.23,.28,.3),'cartridge',(0,-300,-4))
add('F05 compressed perimeter gasket 3mm',ring(20,15,280,360,230,3,10),(.15,.17,.18),'seal',(0,0,30))
seat=ring(10,5,283,380,250,5,20)
add('F06 fixed sealing seat',seat,(.57,.61,.62))
for x in [10,370]: add(f'F07 slide rail {x}',box(x,8,210,20,240,6),(.47,.52,.55))
for x in [60,320]: add(f'F08 cam clamp envelope {x}',box(x,16,199,20,20,18),(.19,.23,.26))

# Fan is a reserved mixed-flow assembly; not a selected fan performance claim.
fan=cyl(200,130,400,100,90).cut(cyl(200,130,399,86,92))
add('A01 fan casing clearance diameter200 h90',fan,(.37,.42,.46))
add('A02 motor hub clearance',cyl(200,130,420,34,50),(.19,.24,.27))
for i in range(8):
    blade=box(202,126,440,80,8,6).rotate((200,130,440),(200,130,441),45*i)
    add(f'A03 impeller indication {i}',blade,(.49,.55,.58))
# Support deck seals the clean plenum to the fan inlet; no unmodelled open perimeter.
deck=box(5,5,395,390,250,5).cut(cyl(200,130,394,86,7))
add('A04 fan inlet support deck',deck,(.56,.62,.64))
# Rectangular transition from the fan exit to an instrumented 150x100 throat.
outer=cq.Workplane('XY').workplane(offset=490).center(200,130).rect(204,204).workplane(offset=40).rect(158,108).loft().val()
inner=cq.Workplane('XY').workplane(offset=489).center(200,130).rect(196,196).workplane(offset=42).rect(150,100).loft().val()
add('A05 outlet transition',outer.cut(inner),(.55,.62,.65))
add('A06 flow neck internal150x100',ring(121,76,530,158,108,110,4),(.62,.68,.7))
# FS3000: 9 X by 8 Z by 4 Y envelope; its channel follows +Z.
board('S01 flow carrier PCB proposed',184,163,565,30,36,(.82,.45,.13),'flow_mount')
base=box(194,161.4,578,9,1.6,8)
hood=box(194,159,578,9,1.2,8).fuse(box(194,160.2,578,1.2,1.2,8)).fuse(box(201.8,160.2,578,1.2,1.2,8))
add('S01A FS3000 substrate 9x8',base,(.21,.24,.27),'flow_sensor',sensor='airflow')
add('S01B FS3000 channel hood',hood,(.68,.73,.76),'flow_sensor')
add('S01C flow carrier connector',box(187,158,591,12,5,6),(.3,.32,.34),'flow_mount')
add('S01D duct mounting bracket',box(181,164.6,563,36,15.4,3),(.68,.69,.65),'flow_mount')
for x in [185,213]:add('S01G duct wall fixing '+str(x),cq.Solid.makeCylinder(1.3,8,cq.Vector(x,176,564.5),cq.Vector(0,1,0)),(.84,.84,.76),'flow_mount')
for x in [188,210]:add('S01E nylon fastener '+str(x),cq.Solid.makeCylinder(1.7,7,cq.Vector(x,159,569),cq.Vector(0,1,0)),(.85,.85,.77),'flow_mount')
grommet=cq.Solid.makeCylinder(4,8,cq.Vector(198,176,597),cq.Vector(0,1,0)).cut(cq.Solid.makeCylinder(1.1,10,cq.Vector(198,175,597),cq.Vector(0,1,0)))
add('S01F sealed duct cable grommet',grommet,(.19,.21,.23),'flow_mount')

# SPS30 simplified geometry: paired inlet grilles, separate exhaust and rear header.
for z,tag,col in [(145,'pm_up',(.16,.43,.73)),(325,'pm_down',(.12,.60,.43))]:
    group='pocket_'+tag
    add('S02 '+tag+' pocket base',box(6,90,z-6,65,78,3),(.60,.65,.67),group)
    add('S02 '+tag+' pocket back',box(6,164,z-3,65,4,38),(.60,.65,.67),group)
    add('S02 '+tag+' left shield',box(6,90,z-3,4,74,38),(.60,.65,.67),group)
    add('S02 '+tag+' removable shield roof',box(6,90,z+35,65,78,4),(.60,.65,.67),group)
    cradle=ring(12,106,z-3,47.2,47.2,3,3)
    add('S03 '+tag+' insulating cradle',cradle,(.82,.80,.70),'sensor_'+tag)
    body=box(15,109,z,41.2,41.2,12.2)
    for dz in [3.0,6.5]:body=body.cut(box(28,108.5,z+dz,14.8,2,1.1))
    body=body.cut(box(18,108.5,z+2.2,6.6,2,3.5))
    add('S03 '+tag+' SPS30 body',body,col,'sensor_'+tag,sensor=tag)
    add('S03 '+tag+' top shield plate',box(16,110,z+12.2,39.2,39.2,.1),(.76,.79,.80),'sensor_'+tag)
    add('S03 '+tag+' rear five pin connector',box(43,150.2,z+2,10.8,5,6),(.30,.32,.34),'sensor_'+tag)
    for x in [44.5,46.5,48.5,50.5,52.5]:add('S03 '+tag+' contact '+str(x),box(x,153,z+3,0.7,2.5,2),(.78,.68,.39),'sensor_'+tag)
    add('S02 '+tag+' mouth separator',box(25,94,z,2,15,14),(.80,.78,.67),group)
    for x in [14,58]:add('S02 '+tag+' cradle fixing '+str(x),cyl(x,155,z-3,1.6,4),(.79,.78,.72),group)

# SHT40 chip is distinct from the proposed 20x20mm carrier; aperture faces room inlet.
board('S04 environmental carrier PCB proposed',320,19,137,20,20,(.82,.46,.15),'rht_mount')
sht=box(329.25,18.46,146.25,1.5,.54,1.5).cut(cq.Solid.makeCylinder(.3,.22,cq.Vector(330,18.45,147),cq.Vector(0,1,0)))
add('S04A SHT40 package 1.5x1.5x0.54',sht,(.08,.10,.13),'rht_sensor',sensor='rht')
add('S04B environmental carrier connector',box(323,15,139,10,4,4),(.27,.29,.31),'rht_mount')

# P+ and P- are only pressure lines, terminating at separate module nipples.
pipe('P01 upstream tube',[(386,170,180),(386,246,180),(386,275,180),(318,275,180),(318,275,317)],2,(.76,.28,.19))
pipe('P02 downstream tube',[(386,170,340),(386,246,340),(386,275,340),(350,275,340),(350,275,307),(332,275,307),(332,275,317)],2,(.16,.40,.75))
for z,tag in [(180,'Pplus'),(340,'Pminus')]:
    fitting=cq.Solid.makeCylinder(4,8,cq.Vector(386,170,z),cq.Vector(0,1,0)).cut(cq.Solid.makeCylinder(1.7,10,cq.Vector(386,169,z),cq.Vector(0,1,0)))
    add('P03 '+tag+' static fitting',fitting,(.63,.65,.66),'pressure_tube')
wire('W01 upstream UART and 5V harness',[(48,155,150),(80,155,150),(80,246,150),(80,279,150),(240,279,150),(240,279,470),(223,274,470)],(.20,.32,.50))
wire('W02 downstream UART and 5V harness',[(48,155,330),(80,155,330),(80,246,330),(80,281,330),(242,281,330),(242,281,530),(223,274,530)],(.16,.46,.34))
wire('W03 FS3000 power and I2C harness',[(193,163,596),(198,177,597),(198,188,597),(240,200,597),(240,283,597),(240,283,536),(308,274,530)],(.62,.38,.13))
wire('W04 SHT40 power and I2C harness',[(328,19,141),(350,25,141),(350,246,141),(350,279,141),(244,279,141),(244,279,476),(308,274,470)],(.65,.43,.15))
wire('W05 cover interlock harness',[(355,24,369),(355,246,369),(355,283,369),(246,283,369),(246,283,470),(225,274,470)])
wire('W06 pressure ADC and excitation harness',[(288,274,304),(250,279,304),(250,279,525),(225,274,525)])
wire('W07 low voltage input',[(96,287,82),(96,278,105),(120,273,105)],(.70,.2,.18))
wire('W08 regulated rails to controller',[(140,274,110),(252,282,110),(252,282,465),(310,274,465)],(.58,.23,.19))
for x,z in [(80,150),(80,330),(350,141),(355,369),(240,597)]:
    add('W09 partition feedthrough '+str((x,z)),cq.Solid.makeCylinder(3.2,6,cq.Vector(x,253,z),cq.Vector(0,1,0)),(.18,.20,.22),'wiring')

assembly=cq.Assembly(name='MA4822_Purifier_Packaging_Study')
for p in parts: assembly.add(p['shape'],name=p['name'].replace(' ','_'),color=cq.Color(*p['color']))
assembly.save(str(OUT/'purifier_assembly.step'))

font_path='C:/Windows/Fonts/arial.ttf';bold_path='C:/Windows/Fonts/arialbd.ttf'
visibility={}
def label(d,xy,text,size=35,bold=False,fill='#17252d'):
    d.text(xy,text,font=ImageFont.truetype(bold_path if bold else font_path,size),fill=fill)
def view_shapes(mode):
    chosen=[]
    for p in parts:
        shape=p['shape'];name=p['name'];group=p['group']
        if mode=='sensor_cut':
            if any(n in name for n in ['H02','H03','H06','removable shield roof']):continue
            if 'H01' in name:shape=shape.cut(box(-2,-2,20,410,78,620)).cut(box(385,0,20,20,301,620))
            if 'H04' in name:shape=shape.cut(box(-2,-2,639,410,210,15))
            if 'A06' in name:shape=shape.cut(box(115,70,529,170,12,113)).cut(box(274,70,529,9,120,113))
            if 'A05' in name:shape=shape.cut(box(90,20,489,220,70,43))
            if 'A01' in name:shape=shape.cut(box(90,20,399,220,100,93))
        elif mode=='rear':
            if 'H09' in name:continue
            if group not in ['electronics','pressure_tube','wiring','housing','cover'] and 'H08' not in name:continue
        elif mode=='detail_pm':
            if 'pm_up' not in name or 'removable shield roof' in name:continue
        elif mode=='detail_pm_back':
            if group!='sensor_pm_up':continue
        elif mode=='detail_flow':
            if group not in ['flow_sensor','flow_mount'] and not any(n in name for n in ['A06','W03']):continue
            if 'A06' in name:
                shape=shape.intersect(box(178,150,560,42,35,47))
            if 'W03' in name:
                shape=shape.intersect(box(178,150,560,42,40,47))
        elif mode=='service':
            if group=='housing' and any(n in name for n in ['H03','H06']):continue
            if group=='housing' and 'H01' in name:shape=shape.cut(box(-2,-2,40,410,135,355))
            shape=shape.translate(p['move'])
        elif mode=='exterior':
            if group not in ['housing','cover']:continue
        if shape.Volume()>1e-7:chosen.append((p,shape))
    return chosen

def render_raw(mode,w,h,camera,focal,zoom=1.08):
    ren=vtk.vtkRenderer();ren.SetBackground(1,1,1)
    ren.SetUseDepthPeeling(True)
    selected=view_shapes(mode)
    visibility[mode]={p['sensor']:{'part':p['name'],'retained_volume_ratio':shape.Volume()/p['shape'].Volume()}for p,shape in selected if p['sensor']}
    for p,shape in selected:
        vertices,triangles=shape.tessellate(.6,.2)
        pts=vtk.vtkPoints()
        for v in vertices:pts.InsertNextPoint(v.x,v.y,v.z)
        cells=vtk.vtkCellArray()
        for tri in triangles:
            cells.InsertNextCell(3)
            for j in tri:cells.InsertCellPoint(j)
        pd=vtk.vtkPolyData();pd.SetPoints(pts);pd.SetPolys(cells)
        normals=vtk.vtkPolyDataNormals();normals.SetInputData(pd);normals.ComputePointNormalsOn();normals.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
        actor=vtk.vtkActor();actor.SetMapper(mapper)
        prop=actor.GetProperty();prop.SetColor(*p['color']);prop.SetAmbient(.33);prop.SetDiffuse(.67);prop.SetSpecular(.08)
        # Real CAD edges, not triangle mesh edges.
        ren.AddActor(actor)
        edges=vtk.vtkFeatureEdges();edges.SetInputData(pd);edges.BoundaryEdgesOn();edges.FeatureEdgesOn();edges.NonManifoldEdgesOff();edges.ManifoldEdgesOff();edges.SetFeatureAngle(30)
        em=vtk.vtkPolyDataMapper();em.SetInputConnection(edges.GetOutputPort());em.ScalarVisibilityOff()
        ea=vtk.vtkActor();ea.SetMapper(em);ea.GetProperty().SetColor(.2,.25,.28);ea.GetProperty().SetLineWidth(1.2);ren.AddActor(ea)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.AddRenderer(ren);win.SetSize(w,h);win.SetMultiSamples(4)
    cam=ren.GetActiveCamera();cam.SetPosition(*camera);cam.SetFocalPoint(*focal);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn()
    ren.ResetCamera();cam.Zoom(zoom);win.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/(mode+'_raw.png')));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
    zc=vtk.vtkWindowToImageFilter();zc.SetInput(win);zc.SetInputBufferTypeToZBuffer();zc.ReadFrontBufferOff();zc.Update()
    from vtk.util.numpy_support import vtk_to_numpy
    zbuf=vtk_to_numpy(zc.GetOutput().GetPointData().GetScalars()).reshape(h,w)
    def proj(pt):
        ren.SetWorldPoint(*pt,1);ren.WorldToDisplay();u,v,zz=ren.GetDisplayPoint()
        ix,iy=int(round(u)),int(round(v));delta=None
        if 0<=ix<w and 0<=iy<h:
            area=zbuf[max(0,iy-2):min(h,iy+3),max(0,ix-2):min(w,ix+3)]
            delta=float(np.min(np.abs(area-zz)))
        return (int(u),int(h-v)),delta
    raw=Image.open(OUT/(mode+'_raw.png')).copy()
    return raw,proj,win

def arrow2(d,a,b,color='#247591',width=5):
    d.line([a,b],fill=color,width=width)
    angle=math.atan2(b[1]-a[1],b[0]-a[0]);l=20
    d.polygon([b,(b[0]-l*math.cos(angle-.4),b[1]-l*math.sin(angle-.4)),(b[0]-l*math.cos(angle+.4),b[1]-l*math.sin(angle+.4))],fill=color)

def render(name,mode):
    camera=(1100,-1500,1050);focal=(200,110,320);zoom=1.08
    if mode=='sensor_cut':camera=(820,-1600,860)
    if mode=='rear':camera=(650,1800,850);focal=(200,270,325)
    if mode=='service':camera=(1100,-1650,1050);focal=(200,-20,320);zoom=1.03
    raw,project,win=render_raw(mode,1300,1450,camera,focal,zoom)
    canvas=Image.new('RGB',(1900,1640),'white');canvas.paste(raw,(40,100))
    d=ImageDraw.Draw(canvas)
    titles={'exterior':'Exterior isometric view','sensor_cut':'Sensor placement cutaway','rear':'Rear electronics compartment','service':'Filter service view'}
    label(d,(40,20),titles[mode],46,True)
    if mode=='exterior':
        items=[((200,130,648),'Top outlet guard'),((200,0,568),'Local display'),((390,0,310),'Removable service cover'),((200,0,125),'Louvred room air inlet')]
        label(d,(1300,820),'Overall envelope',34,True);label(d,(1300,875),'400 W × 300 D',36);label(d,(1300,927),'× 650 H mm',36)
    elif mode=='sensor_cut':
        items=[((198.5,159,582),'1  FS3000 on carrier'),((355,9,369),'2  Cover interlock'),((50,109,331),'3  Outlet SPS30 optional'),((386,170,344),'4  P− clean static tap'),((50,109,151),'5  Inlet SPS30'),((329.45,18.46,147),'6  SHT40 on carrier'),((386,170,184),'7  P+ dirty static tap')]
        label(d,(1300,1190),'Sensors are not sectioned',32,True)
        label(d,(1300,1240),'Housing and pocket roofs',30);label(d,(1300,1280),'removed for visibility',30)
    elif mode=='rear':
        items=[((270,268.6,500),'1  Controller and UARTs'),((290,267.6,355),'2  Pressure conditioning IC'),((330,282,335),'3  Raw ΔP module allowance'),((318,278,320),'4  P+ red pressure tube'),((332,278,320),'5  P− blue pressure tube'),((244,280,220),'6  Signal harness routes'),((101,274.6,110),'7  5 V and 3.3 V rails'),((96,296,76),'8  Low voltage input')]
        label(d,(1300,1270),'Rear cover removed',32,True);label(d,(1300,1320),'PCB layouts are proposed',30)
    else:
        items=[((-230,0,180),'1  Cover removed first'),((200,-170,246),'2  Slide cartridge forward'),((200,130,311),'3  Inspect perimeter seal'),((65,30,204),'4  Release cam clamps')]
        label(d,(1300,850),'Service allowance',34,True);label(d,(1300,905),'300 mm forward',34);label(d,(1300,958),'4 mm release drop',34)
    for i,(pt,txt) in enumerate(items):
        yy=150+i*(145 if mode in ['sensor_cut','rear'] else 150)
        xy,delta=project(pt);a=(xy[0]+40,xy[1]+100)
        if mode in ['sensor_cut','rear']:
            visibility[mode].setdefault('anchors',[]).append({'label':txt,'point':pt,'depth_difference':delta})
        d.line([a,(1260,yy+18),(1290,yy+18)],fill='#40535e',width=3);d.ellipse((a[0]-6,a[1]-6,a[0]+6,a[1]+6),fill='#40535e')
        # Wrap long labels in the reserved annotation column.
        words=txt.split();line='';rows=[]
        for w in words:
            if len(line+' '+w)>27:rows.append(line);line=w
            else:line=(line+' '+w).strip()
        rows.append(line)
        for j,row in enumerate(rows): label(d,(1300,yy+j*42),row,34)
    label(d,(40,1550),'Parametric solid model  |  mm  |  nominal packaging only',31)
    canvas.save(OUT/(name+'.png'))
    win.Finalize()

def detail_pm():
    im=Image.new('RGB',(1900,1760),'white');d=ImageDraw.Draw(im)
    label(d,(35,20),'PM pocket and sensor interfaces',46,True)
    raw,proj,win=render_raw('detail_pm',1200,1000,(80,-250,260),(35,129,155),1.0);im.paste(raw,(20,90));d=ImageDraw.Draw(im)
    calls=[((35,109,149),'Paired sampling inlet grilles'),((21,109,149),'Separate exhaust opening'),((26,94,151),'Mouth separator'),((35,107.5,145),'Insulating cradle'),((35,164,170),'Pocket back shield')]
    for i,(pt,txt) in enumerate(calls):
        xy,_=proj(pt);a=(xy[0]+20,xy[1]+90);yy=170+i*150
        d.line([a,(1190,yy+15),(1230,yy+15)],fill='#40535e',width=3);d.ellipse((a[0]-5,a[1]-5,a[0]+5,a[1]+5),fill='#40535e')
        for j,t in enumerate([txt] if len(txt)<27 else ['Paired sampling inlet','grilles']):label(d,(1240,yy+42*j),t,34)
    # Both sample and exhaust arrows remain in the same local plenum.
    for a,b in [((35,96,150),(35,108,150)),((21,108,149),(21,96,149))]:
        aa,_=proj(a);bb,_=proj(b);arrow2(d,(aa[0]+20,aa[1]+90),(bb[0]+20,bb[1]+90))
    win.Finalize()
    back,pb,wb=render_raw('detail_pm_back',850,520,(90,240,220),(35,132,151),1.0);im.paste(back,(40,1110));d=ImageDraw.Draw(im)
    label(d,(900,1150),'Opposite face',38,True)
    label(d,(900,1210),'Five pin power and UART header',35)
    label(d,(900,1270),'5 V supply; separate local sampling ports',32)
    xy,_=pb((48,155.2,150));a=(xy[0]+40,xy[1]+1110)
    d.line([a,(875,1230),(895,1230)],fill='#40535e',width=3);d.ellipse((a[0]-6,a[1]-6,a[0]+6,a[1]+6),fill='#40535e')
    wb.Finalize()
    label(d,(35,1600),'SPS30 41 mm class body; modeled allowance 41.2 × 41.2 × 12.3 mm',33)
    label(d,(35,1650),'Roof removed in upper view; shields omitted in rear inset. No sensor-body cuts.',31)
    label(d,(35,1700),'Simplified geometry from [11]; cradle and baffle are proposed. Sampling performance is unvalidated.',29)
    im.save(OUT/'cad_pm_detail.png')

def detail_flow():
    raw,proj,win=render_raw('detail_flow',1250,1270,(420,-400,820),(200,135,585),1.0)
    im=Image.new('RGB',(1900,1480),'white');im.paste(raw,(20,90));d=ImageDraw.Draw(im)
    label(d,(35,20),'Airflow module and mounting detail',46,True)
    calls=[((198.5,159,582),'FS3000 channel hood'),((194,161.4,582),'9 × 8 × 4 mm module'),((206,163,590),'Proposed carrier PCB'),((193,158,594),'Power and I2C connector'),((216,174,566),'Removable mounting bracket'),((198,180,597),'Sealed cable exit')]
    for i,(pt,txt) in enumerate(calls):
        xy,_=proj(pt);a=(xy[0]+20,xy[1]+90);yy=150+i*145
        d.line([a,(1220,yy+15),(1260,yy+15)],fill='#40535e',width=3);d.ellipse((a[0]-6,a[1]-6,a[0]+6,a[1]+6),fill='#40535e')
        words=txt.split();rows=[];line=''
        for w in words:
            if len(line+' '+w)>28:rows.append(line);line=w
            else:line=(line+' '+w).strip()
        rows.append(line)
        for j,t in enumerate(rows):label(d,(1270,yy+j*40),t,34)
    for x,y in [(180,158),(220,158)]:
        a,_=proj((x,y,568));b,_=proj((x,y,600));arrow2(d,(a[0]+20,a[1]+90),(b[0]+20,b[1]+90))
    label(d,(1270,1080),'Flow and channel axis +Z',33,True)
    label(d,(35,1340),'Local wall patch in the 150 × 100 mm neck. Complete sensing module retained.',32)
    label(d,(35,1390),'Module size and channel principle follow [12]; carrier and fasteners are proposed.',31)
    label(d,(35,1440),'Mounting blockage and velocity profile require installed calibration.',31)
    win.Finalize();im.save(OUT/'cad_flow_detail.png')

for name,mode in [('cad_exterior','exterior'),('cad_sensor_cutaway','sensor_cut'),('cad_rear','rear'),('cad_service','service')]:render(name,mode)
detail_pm();detail_flow()
report=[]
for p in parts:
    bb=p['shape'].BoundingBox()
    report.append(dict(name=p['name'],valid=p['shape'].isValid(),volume_mm3=p['shape'].Volume(),bbox=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]))
contained=all(all(p['bbox'][i]>=-1e-4 and p['bbox'][i+3]<=limit+1e-4 for i,limit in enumerate([400,300,650]))for p in report)
roundtrip=cq.importers.importStep(str(OUT/'purifier_assembly.step')).val()
assert contained
assert roundtrip.isValid() and roundtrip.Volume()>0
required={'airflow','pm_up','pm_down','rht','cover_switch'}
assert required.issubset(visibility['sensor_cut'])
assert all(abs(visibility['sensor_cut'][s]['retained_volume_ratio']-1)<1e-9 for s in required)
assert all(s in visibility['rear'] for s in ['controller','pressure'])
(OUT/'sensor_visibility.json').write_text(json.dumps(visibility,indent=2))
(OUT/'cad_checks.json').write_text(json.dumps({'part_count':len(parts),'all_valid':all(p['valid'] for p in report),'all_parts_within_envelope':contained,'step_roundtrip_valid':roundtrip.isValid(),'complete_sensor_cutaway':True,'envelope_mm':[400,300,650],'plenum_nominal_area_m2':.095,'neck_area_m2':.015,'parts':report},indent=2))
print(json.dumps({'parts':len(parts),'step_bytes':(OUT/'purifier_assembly.step').stat().st_size,'all_valid':all(p['valid'] for p in report)},indent=2))

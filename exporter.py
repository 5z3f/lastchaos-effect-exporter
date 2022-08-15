__author__          = 'agsvn'

from enum import Enum
from rich import print as rprint
from rich.tree import Tree
from rich.progress import track
from lib.binary import BinaryReader

class PARTICLE_RENDER_TYPE(Enum):
	PRT_QUAD            = 0
	PRT_LINE            = 1
	PRT_TRAIL           = 2
	PRT_TRAIL_VELOCITY  = 3
	PRT_FORCE_DWORD     = 0xFFFFFFFF # -1

class PARTICLE_BLEND_TYPE(Enum):
	PBT_OPAQUE      = 201    # ZW
	PBT_TRANSPARENT = 202    # ZW, AT
	PBT_BLEND       = 203    # S*Sa + D*(1-Sa)    
	PBT_SHADE       = 204    # S*D  + D*S   (mul x2)
	PBT_ADD         = 205    # S    + D
	PBT_ADDALPHA    = 206    # S*Sa + D
	PBT_MULTIPLY    = 207    # S*D  + 0
	PBT_INVMULTIPLY = 208    # 0    + D*(1-Sa)

class PARTICLES_ABSORPTION_TYPE(Enum):
    PAT_NONE    = 0
    PAT_DEFAULT = 1
    PAT_SPHERE  = 2

class PARTICLE_MOVE_TYPE(Enum):
	PMT_NONMOVE                 = 0
	PMT_VELOCITY                = 1
	PMT_ACCELERATION            = 2
	PMT_LOCALPOS_NONMOVE        = 3
	PMT_LOCALPOS_VELOCITY       = 4
	PMT_LOCALPOS_ACCELERATION   = 5

class PARTICLES_EMITTER_TYPE(Enum):
	PET_NONE	    = 0
	PET_SPHERE	    = 1
	PET_CONE	    = 2
	PET_CYLINDER    = 3

class PARTICLES_COMMON_PROCESS_TYPE(Enum):
	PCPT_NONE			= 0
	PCPT_DYNAMIC_STATE	= 1
	PCPT_FORCE			= 2
	PCPT_POINT_GOAL		= 3
	PCPT_CONTROL		= 4
	PCPT_VELOCITY		= 5

class EFFECT_TYPE(Enum):
    ET_NOTHING			= 0
    ET_TERRAIN          = 1
    ET_LIGHT            = 2
    ET_PARTICLE         = 3
    ET_SKA              = 4
    ET_MDL              = 5
    ET_TRACE            = 6
    ET_SOUND            = 7
    ET_SPLINEBILLBOARD  = 8
    ET_ORBIT            = 9
    ET_SHOCKWAVE        = 10
    ET_SPLINEPATH       = 11
    ET_CAMERA           = 12
    ET_ENTITY           = 13
    ET_COUNT            = 14

def ByteToInt(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

def dfnm(br):
    magic = br.ReadBytes(4) #DFNM
    len = br.ReadLong()
    str = br.ReadBytes(len)
    return str

def readConeDoubleSpace(br, treeNode):
    magic = br.ReadBytes(4) # CDSP
    treeNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    heightUpper = br.ReadFloat()
    treeNode.add(f'Height Upper: {round(heightUpper, 3)}')

    heightLower = br.ReadFloat()
    treeNode.add(f'Height Lower: {round(heightLower, 3)}')

    hotspot = br.ReadFloat()
    treeNode.add(f'Hotspot: {round(hotspot, 3)}')

    falloff = br.ReadFloat()
    treeNode.add(f'Falloff: {round(falloff, 3)}')

    temp = treeNode.add(f'Center')
    temp.add(f'X: {round(br.ReadFloat(), 3)}')
    temp.add(f'Y: {round(br.ReadFloat(), 3)}')
    temp.add(f'Z: {round(br.ReadFloat(), 3)}')

    closeRange = br.ReadFloat()
    treeNode.add(f'Close Range: {round(closeRange, 3)}')

    lerpRatio = br.ReadFloat()
    treeNode.add(f'Lerp Ratio: {round(lerpRatio, 3)}')

def readCylinderDoubleSpace(br, treeNode):
    magic = br.ReadBytes(4) # CDSP
    treeNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    height = br.ReadFloat()
    treeNode.add(f'Height: {round(height, 3)}')

    radiusInner = br.ReadFloat()
    treeNode.add(f'Radius Inner: {round(radiusInner, 3)}')

    radiusOuter = br.ReadFloat()
    treeNode.add(f'Radius Outer: {round(radiusOuter, 3)}')

    temp = treeNode.add(f'Center')
    temp.add(f'X: {round(br.ReadFloat(), 3)}')
    temp.add(f'Y: {round(br.ReadFloat(), 3)}')
    temp.add(f'Z: {round(br.ReadFloat(), 3)}')

def readSphereDoubleSpace(br, treeNode):
    magic = br.ReadBytes(4) # SDSP
    treeNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    radiusOuter = br.ReadFloat()
    treeNode.add(f'Radius Outer: {round(radiusOuter, 3)}')

    radiusInner = br.ReadFloat()
    treeNode.add(f'Radius Inner: {round(radiusInner, 3)}')

    temp = treeNode.add(f'Center')
    temp.add(f'X: {round(br.ReadFloat(), 3)}')
    temp.add(f'Y: {round(br.ReadFloat(), 3)}')
    temp.add(f'Z: {round(br.ReadFloat(), 3)}')

def readParticleEmitterCone(br, treeNode):
    coneNode = treeNode.add('Cone')

    magic = br.ReadBytes(4) # PECN
    coneNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    coneNode.add(f'Version: {ver}')

    speedLower = br.ReadFloat()
    coneNode.add(f'Speed Lower: {round(speedLower, 3)}')

    speedUpper = br.ReadFloat()
    coneNode.add(f'Speed Upper: {round(speedUpper, 3)}')

    useShapePosition = br.ReadInt32()
    coneNode.add(f'Use Shape Position: {bool(useShapePosition)}')

    useShapeSpeed = br.ReadInt32()
    coneNode.add(f'Use Shape Speed: {bool(useShapeSpeed)}')

    temp = coneNode.add(f'Double Space')
    readConeDoubleSpace(br, temp)


def readForce(br, treeNode):
    forceNode = treeNode.add('Force')

    magic = br.ReadBytes(4) # FOCE
    forceNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    forceNode.add(f'Version: {ver}')

    forceType = br.ReadULong()
    forceNode.add(f'Force Type: {forceType}')

    power = br.ReadFloat()
    forceNode.add(f'Power: {round(power, 3)}')

    temp = forceNode.add(f'Position')
    temp.add(f'X: {round(br.ReadFloat(), 3)}')
    temp.add(f'Y: {round(br.ReadFloat(), 3)}')
    temp.add(f'Z: {round(br.ReadFloat(), 3)}')

    temp = forceNode.add(f'Direction')
    temp.add(f'X: {round(br.ReadFloat(), 3)}')
    temp.add(f'Y: {round(br.ReadFloat(), 3)}')
    temp.add(f'Z: {round(br.ReadFloat(), 3)}')


def readParticleEmitterSphere(br, treeNode):
    sphereNode = treeNode.add('Sphere')

    magic = br.ReadBytes(4) # PEMS
    sphereNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    sphereNode.add(f'Version: {ver}')

    readForce(br, sphereNode)

    delayTime = br.ReadFloat()
    sphereNode.add(f'Delay Time: {round(delayTime, 3)}')

    temp = sphereNode.add(f'Double Space')
    readSphereDoubleSpace(br, temp)

def readParticleEmitterCylinder(br, treeNode):
    cylinderNode = treeNode.add('Cylinder')

    magic = br.ReadBytes(4) # PECN
    cylinderNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    cylinderNode.add(f'Version: {ver}')

    speedLower = br.ReadFloat()
    cylinderNode.add(f'Speed Lower: {round(speedLower, 3)}')

    speedUpper = br.ReadFloat()
    cylinderNode.add(f'Speed Upper: {round(speedUpper, 3)}')

    useShapePosition = br.ReadInt32()
    cylinderNode.add(f'Use Shape Position: {bool(useShapePosition)}')

    useShapeSpeed = br.ReadInt32()
    cylinderNode.add(f'Use Shape Speed: {bool(useShapeSpeed)}')

    emitAllDirections = br.ReadInt32()
    cylinderNode.add(f'Emit All Directions: {bool(emitAllDirections)}')

    temp = cylinderNode.add(f'Double Space')
    readCylinderDoubleSpace(br, temp)

def particleProcessPointGoal(br, treeNode):
    magic = br.ReadBytes(4)
    treeNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    lerpRatio = br.ReadFloat()
    treeNode.add(f'Lerp Ratio: {round(lerpRatio, 3)}')

    lerpSpeed = br.ReadFloat()
    treeNode.add(f'Lerp Speed: {round(lerpSpeed, 3)}')

    speed = br.ReadFloat()
    treeNode.add(f'Speed: {round(speed, 3)}')

    temp = treeNode.add('Goal Point')
    temp.add(f'X: {round(br.ReadFloat(), 3)}')
    temp.add(f'Y: {round(br.ReadFloat(), 3)}')
    temp.add(f'Z: {round(br.ReadFloat(), 3)}')
    
    goalTagName = br.ReadString(br.ReadLong())
    treeNode.add(f'Goal Tag Name: {goalTagName}')

def particleProcessControl(br, treeNode):
    magic = br.ReadBytes(4)
    treeNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    type = br.ReadULong()
    treeNode.add(f'Type: {type}')

    useParticlePos = br.ReadInt32()
    treeNode.add(f'Use Particle Pos: {bool(useParticlePos)}')

    angleSpeed = br.ReadFloat()
    treeNode.add(f'Angle Speed: {round(angleSpeed, 3)}')

    heightSpeed = br.ReadFloat()
    treeNode.add(f'Height Speed: {round(heightSpeed, 3)}')

    dependRadius = br.ReadInt32()
    treeNode.add(f'Depend Radius: {bool(dependRadius)}')

def particleProcessVelocity(br, treeNode):
    magic = br.ReadBytes(4)
    treeNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    temp = treeNode.add('Velocity Direction')
    temp.add(f'X: {round(br.ReadFloat(), 3)}')
    temp.add(f'Y: {round(br.ReadFloat(), 3)}')
    temp.add(f'Z: {round(br.ReadFloat(), 3)}')

    speed = br.ReadFloat()
    treeNode.add(f'Speed: {round(speed, 3)}')

def particleProcessForce(br, treeNode):
    magic = br.ReadBytes(4)
    treeNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    size = br.ReadULong()
    treeNode.add(f'Size: {size}')

    for i in range(size):
        readForce(br, treeNode)

def particleProcessDynamicState(br, treeNode):
    magic = br.ReadBytes(4)
    treeNode.add(f'Magic: {magic}')

    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    twinklePeriod = br.ReadFloat()
    treeNode.add(f'Twinkle Period: {twinklePeriod}')

    fadeInTime = br.ReadFloat()
    treeNode.add(f'Fade In Time: {round(fadeInTime, 3)}')

    fadeOutTime = br.ReadFloat()
    treeNode.add(f'Fade Out Time: {round(fadeOutTime, 3)}')

    # color
    b = br.ReadInt32()
    colorNode = treeNode.add('Color')
    if b:
        size = br.ReadULong()
        colorNode.add(f'Size: {size}')
        for i in range(size):
            key = br.ReadFloat()
            value = br.ReadULong()
            colorNode.add(f'Key: {key}')
            colorNode.add(f'Value: {value}')

    
    # alpha
    b = br.ReadInt32()
    alphaNode = treeNode.add('Alpha')
    if b:
        size = br.ReadULong()
        alphaNode.add(f'Size: {size}')
        for i in range(size):
            key = br.ReadFloat()
            value = br.ReadByte()
            alphaNode.add(f'Key: {key}')
            alphaNode.add(f'Value: {value}')

    # Texture Position
    texpos = []
    b = br.ReadInt32()
    texturePositionNode = treeNode.add(f'Texture Position')
    if b:
        size = br.ReadULong()
        texturePositionNode.add(f'Size: {size}')
        for i in range(size):
            temp = texturePositionNode.add(f'Node {i}')
            key = br.ReadFloat()
            row = br.ReadByte()
            col = br.ReadByte()
            temp.add(f'Key: {key}')
            temp.add(f'Row: {row}')
            temp.add(f'Col: {col}')
            
        #print("\t\t\t\tTable:", texpos)

    # Particle Size 
    particlesize = []
    b = br.ReadInt32()
    particleSizeNode = treeNode.add('Particle Size')
    if b:
        size = br.ReadULong()
        particleSizeNode.add(f'Size: {size}')
        for i in range(size):
            temp = particleSizeNode.add(f'Node {i}')
            key = br.ReadFloat()
            width = br.ReadFloat()
            height = br.ReadFloat()

            #particlesize.append({ 'key': key, 'width': br.ReadFloat(), 'height': br.ReadFloat() })
            temp.add(f'Key: {key}')
            temp.add(f'Width: {round(width, 3)}')
            temp.add(f'Height: {round(height, 3)}')
            

        #print("\t\t\t\tTable:", particlesize)

    # Mass
    mass = []
    b = br.ReadInt32()
    massNode = treeNode.add('Mass')
    if b:
        size = br.ReadULong()
        massNode.add(f'Size: {size}')
        for i in range(size):
            key = br.ReadFloat()
            value = br.ReadFloat()
            massNode.add(f'Key: {key}')
            massNode.add(f'Value: {round(value, 3)}')
        #print("\t\t\t\tTable:", mass)

    # DeltaPos
    deltapos = []
    b = br.ReadInt32()
    deltaPositionNode = treeNode.add('Delta Position')
    if b:
        size = br.ReadULong()
        deltaPositionNode.add(f'Size: {size}')
        for i in range(size):
            temp = deltaPositionNode.add(f'Node: {i}')
            key = round(br.ReadFloat(), 3)
            x = round(br.ReadFloat(), 3)
            y = round(br.ReadFloat(), 3)
            z = round(br.ReadFloat(), 3)
            
            temp.add(f'Key: {key}')
            temp.add(f'X: {x}')
            temp.add(f'Y: {y}')
            temp.add(f'Z: {z}')
            
            #deltapos.append({ 'key': round(key,3), 'x': round(br.ReadFloat(),3), 'y': round(br.ReadFloat(),3), 'z': round(br.ReadFloat(),3) })

        #print("\t\t\t\tTable:", deltapos)
    
    # Angle
    angle = []
    b = br.ReadInt32()
    angleNode = treeNode.add('Angle')
    if b:
        size = br.ReadULong()
        angleNode.add(f'Size: {size}')
        for i in range(size):
            temp = angleNode.add(f'Node: {i}')
            key = br.ReadFloat()
            x = round(br.ReadFloat(), 3)
            y = round(br.ReadFloat(), 3)
            z = round(br.ReadFloat(), 3)

            temp.add(f'Key: {key}')
            temp.add(f'X: {x}')
            temp.add(f'Y: {y}')
            temp.add(f'Z: {z}')

        #print("\t\t\t\tTable:", angle)

def readParticlePrototype(br, treeNode):
    particlePrototypeNode = treeNode.add('Particle Prototype')

    magic = br.ReadBytes(4) # PTPT
    particlePrototypeNode.add(f'Magic: {magic}')
    
    lowerNode = particlePrototypeNode.add('Lower')
    upperNode = particlePrototypeNode.add('Upper')

    ver = br.ReadByte()
    particlePrototypeNode.add(f'Version: {ver}')

    lowerLifeTime = br.ReadFloat()
    lowerNode.add(f'Life Time: {round(lowerLifeTime, 3)}')

    upperLifeTime = br.ReadFloat()
    upperNode.add(f'Life Time: {round(upperLifeTime, 3)}')

    lowerWidth = br.ReadFloat()
    lowerNode.add(f'Width: {round(lowerWidth, 3)}')

    upperWidth = br.ReadFloat()
    upperNode.add(f'Width: {round(upperWidth, 3)}')

    lowerHeight = br.ReadFloat()
    lowerNode.add(f'Height: {round(lowerHeight, 3)}')

    upperHeight = br.ReadFloat()
    upperNode.add(f'Height: {round(upperHeight, 3)}')

    lowerRow = br.ReadByte()
    lowerNode.add(f'Row: {lowerRow}')

    lowerCol = br.ReadByte()
    lowerNode.add(f'Col: {lowerCol}')

    lowerMass = br.ReadFloat()
    lowerNode.add(f'Mass: {round(lowerMass, 3)}')

    upperMass = br.ReadFloat()
    upperNode.add(f'Mass: {round(upperMass, 3)}')

    lowerColor = br.ReadULong()
    lowerNode.add(f'Color (ULONG): {lowerColor}')

    upperColor = br.ReadULong()
    upperNode.add(f'Color (ULONG): {upperColor}')

    lowerQuatW = br.ReadFloat()
    UpperQuatW = br.ReadFloat()

    lowerQuatX = br.ReadFloat()
    UpperQuatX = br.ReadFloat()

    lowerQuatY = br.ReadFloat()
    UpperQuatY = br.ReadFloat()

    lowerQuatZ = br.ReadFloat()
    UpperQuatZ = br.ReadFloat()

    lowerQuaternionNode = lowerNode.add(f'Quaternion')
    lowerQuaternionNode.add(f'W: {lowerQuatW}')
    lowerQuaternionNode.add(f'X: {lowerQuatX}')
    lowerQuaternionNode.add(f'Y: {lowerQuatY}')
    lowerQuaternionNode.add(f'Z: {lowerQuatZ}')

    upperQuaternionNode = upperNode.add(f'Quaternion')
    upperQuaternionNode.add(f'W: {UpperQuatW}')
    upperQuaternionNode.add(f'X: {UpperQuatX}')
    upperQuaternionNode.add(f'Y: {UpperQuatY}')
    upperQuaternionNode.add(f'Z: {UpperQuatZ}')

def readEmitter(br, treeNode):
    type = br.ReadULong()
    emitterNode = treeNode.add('Emitter')
    emitterNode.add(f'Type: {PARTICLES_EMITTER_TYPE(type).name} ({type})')
    
    magic = br.ReadBytes(4) # PTEM
    emitterNode.add(f'Magic: {magic}')
    
    ver = br.ReadByte()
    emitterNode.add(f'Version: {ver}')

    totalCount = br.ReadULong()
    emitterNode.add(f'Total Count: {totalCount}')

    countPerSec = br.ReadFloat()
    emitterNode.add(f'Count Per Sec: {countPerSec}')

    readParticlePrototype(br, emitterNode)

    localType = br.ReadInt32()
    emitterNode.add(f'Local Type: {localType}')

    if type == PARTICLES_EMITTER_TYPE.PET_CONE.value:
        readParticleEmitterCone(br, emitterNode)
    elif type == PARTICLES_EMITTER_TYPE.PET_CYLINDER.value:
        readParticleEmitterCylinder(br, emitterNode)
    elif type == PARTICLES_EMITTER_TYPE.PET_SPHERE.value:
        readParticleEmitterSphere(br, emitterNode)
    
def readAbsorption(br, treeNode):
    absorptionNode = treeNode.add('Absorption')
    type = br.ReadULong()

    magic = br.ReadBytes(4) # PTAB
    absorptionNode.add(f'Magic: {magic}')
    absorptionNode.add(f'Type: {PARTICLES_ABSORPTION_TYPE(type).name} ({type})')
    
    ver = br.ReadByte()
    absorptionNode.add(f'Version: {ver}')

    particleMovementType = br.ReadULong()
    absorptionNode.add(f'Movement Type: {PARTICLE_MOVE_TYPE(particleMovementType).name} ({particleMovementType})')

    dependLife = br.ReadInt32()
    absorptionNode.add(f'Depend Life: {dependLife}')

    if type == PARTICLES_ABSORPTION_TYPE.PAT_DEFAULT.value:
        magic = br.ReadBytes(4) # PADF
        ver = br.ReadByte()
        # ???
    elif type == PARTICLES_ABSORPTION_TYPE.PAT_SPHERE.value:
        magic = br.ReadBytes(4) # PASP
        ver = br.ReadByte()
        temp = absorptionNode.add('Double Space')
        readSphereDoubleSpace(br, temp)


def readParticleGroup(br, treeNode):
    magic = br.ReadBytes(4) # PTGR
    ver = br.ReadByte()

    treeNode.add(f'Version: {ver}')

    name = br.ReadLine()
    treeNode.add(f'Particle Name: {name}')

    texPath = dfnm(br)
    treeNode.add(f'Texture Path: {texPath}')

    renderType = br.ReadULong()
    blendType = br.ReadULong()

    treeNode.add(f'Render Type: {PARTICLE_RENDER_TYPE(renderType).name} ({renderType})')
    treeNode.add(f'Blend Type: {PARTICLE_BLEND_TYPE(blendType).name} ({blendType})')

    width = br.ReadLong()
    height = br.ReadLong()

    treeNode.add(f'Width: {width}')
    treeNode.add(f'Height: {height}')

    col = br.ReadLong()
    row = br.ReadLong()

    treeNode.add(f'Col: {col}')
    treeNode.add(f'Row: {row}')

    size = br.ReadULong()
    
    treeNode.add(f'Size: {size}')
    for i in range(size):
        treeParticleProcessNode = treeNode.add(f'Particle {i}')
        
        processType = br.ReadULong()
        treeParticleProcessNode.add(f'Process Type: {PARTICLES_COMMON_PROCESS_TYPE(processType).name}')

        if processType == PARTICLES_COMMON_PROCESS_TYPE.PCPT_DYNAMIC_STATE.value:
            particleProcessDynamicState(br, treeParticleProcessNode)
        elif processType == PARTICLES_COMMON_PROCESS_TYPE.PCPT_POINT_GOAL.value:
            particleProcessPointGoal(br, treeParticleProcessNode)
        elif processType == PARTICLES_COMMON_PROCESS_TYPE.PCPT_CONTROL.value:
            particleProcessControl(br, treeParticleProcessNode)
        elif processType == PARTICLES_COMMON_PROCESS_TYPE.PCPT_VELOCITY.value:
            particleProcessVelocity(br, treeParticleProcessNode)
        elif processType == PARTICLES_COMMON_PROCESS_TYPE.PCPT_FORCE.value:
            particleProcessForce(br, treeParticleProcessNode)

def readParticleGroupManager(br, pgm):
    ver = br.ReadByte()
    pgm.add(f'Version: {ver}')

    size = br.ReadULong()
    pgm.add(f'Size: {size}')

    for i in track(range(size), description='Reading Particle Groups'):
        treeNode = pgm.add(f'Particle Group {i}')
        readParticleGroup(br, treeNode)

        emitterExists = br.ReadInt32()
        if emitterExists:
            readEmitter(br, treeNode)

        absorptionExists = br.ReadInt32()
        if absorptionExists:
            readAbsorption(br, treeNode)

    return size

def readEffect(br, treeNode):
    effectType = br.ReadULong()
    # TODO
    pass

def readEffectManager(br, treeNode):
    ver = br.ReadByte()
    treeNode.add(f'Version: {ver}')

    size = br.ReadULong()
    treeNode.add(f'Size: {size}')

    for i in track(range(size), description='Reading Effects'):
        treeNode = treeNode.add(f'Effect {i}')
        readEffect(br, treeNode)


def effect(file):
    data = []
    with open(file, "rb") as f:
        fileTree = Tree("File Tree")

        br = BinaryReader(f)
        magic1 = br.ReadBytes(4) # EFTB
        magic2 = br.ReadBytes(4) # EPGM
        magic3 = br.ReadBytes(4) # PGMG

        pgm = fileTree.add('Particle Group Manager')

        size = readParticleGroupManager(br, pgm)

        magic4 = br.ReadBytes(4) # EEFM        
        magic5 = br.ReadBytes(4) # EFMG

        egm = fileTree.add("Effect Manager")

        #readEffectManager()

        print("Exporting...")

        with open('Effect.dat.tree.txt', 'w', encoding="utf8") as f:
            rprint(fileTree, file=f)

        print(f"Exported { size } particle groups to effect.txt")


effect("..\..\Data\Effect\Effect.dat")

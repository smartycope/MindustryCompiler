from EasyRegex import *
from Cope import *

_print = print
_set = set

def convertCondition(string):
    string = str(string).strip()
    ops = {
        '==': "equal",
        '!=': "notEqual",
        '<': "lessThan",
        '<=': "lessThanEq",
        '>': "greaterThan",
        '>=': "greaterThanEq",
        '===': "strictEqual",
        'true': "always"
    }

    if ' ' not in string:
        return f'equal {string} true'

    erParser = group(word()) + optional(whiteChunk()) + group(anyOf(*ops.keys())) + optional(whiteChunk()) + group(word())
    # erParser.debug()
    found = re.match(erParser.str(), string)
    if found:
        # debug(found)
        # debug(found.groups())
        op = ops[found.groups()[3]]
        a  = found.groups()[0]
        b  = found.groups()[5]
    else:
        SyntaxError(f"Can't parse condition '{string}'")

    return f'{op} {a} {b}'

def options(param, *values):
    if param not in values:
        raise TypeError(f"Error: {param} must be one of: {tuple(values)}")



unitTypes = "any", "enemy", "ally", "boss", "player", "attacking", "flying", "ground"

def read(var, memorycell, index):
    return f"read {memorycell} {index}"

def write(var, memorycell, index):
    return f"write {memorycell} {index}"

# sensor result block1 @copper
def sensor(var, building, detect):
    return f"sensor {var} {building} {detect}"

def set(var, val):
    return f"set {var} {val}"

def end():
    return f"end"

def jump(to, condition):
    return f"jump {to} {convertCondition(condition)}"

# getlink result 0
def getlink(var, index:int):
    return f"getlink {var} {index}"


def draw(command, a=0, b=0, c=0, d=0, e=0, f=0):
    return f"draw {command} {a} {b} {c} {d} {e} {f}"

def drawclear(r, g, b):
    return f"draw clear {r} {g} {b}"

def drawcolor(r, g, b, a):
    return f"draw color {r} {g} {b} {a}"

def drawstroke(size):
    return f"draw stroke {size}"

def drawline(x1, y1, x2, y2):
    return draw('line', x1, y1, x2, y2)

def drawrect(x, y, width, height):
    return draw('rect', x, y, width, height)

# draw lineRect 0 0 0 0 0 0
def drawlinerect(x, y, width, height):
    return draw('lineRect', x, y, width, height)

# draw linePoly 0 0 0 0 0 0
def drawpoly(x, y, sides, radius, rotation):
    return draw('poly', x, y, sides, radius, rotation)

def drawlinepoly(x, y, sides, radius, rotation):
    return draw('linePoly', x, y, sides, radius, rotation)

def drawtriangle(x1, y1, x2, y2, x3, y3):
    return draw('triangle', x1, y1, x2, y2, x3, y3)

def drawimage(x, y, image, size, rotation):
    return draw('image', x, y, image, size, rotation)

def drawflush(display='display1'):
    return f"drawflush {display}"


def print(thing):
    return f"print {thing}"

def printflush(building='message1'):
    return f"printflush {building}"


# radar any enemy ally distance turret1 order var
def bradar(var, building, unitType1='any', unitType2='any', unitType3='any', prioritize='distance', unitTypeOrderReversed=False):
    options(unitType1, unitTypes)
    options(unitType2, unitTypes)
    options(unitType3, unitTypes)
    options(prioritize, 'distance', 'health', 'shield', 'armor', 'maxHealth')
    return f"radar {unitType1} {unitType2} {unitType3} {prioritize} {building} {'0' if unitTypeOrderReversed else '1'} {var}"

def bcontrol(command, building, a=0, b=0, c=0, d=0):
    return f"control {command} {building} {a} {b} {c} {d}"

def bshoot(building, x, y, shots=1):
    return buildingControl('shoot', building, x, y, shots)

def bshootp(building, unit, shots=1):
    return buildingControl('shootp', building, unit, shots)

def benable(building, set=True):
    return buildingControl('enable', building, '1' if set else '0')

def bdisable(building):
    return buildingControl('enable', building, '0')

def bconfig(building, configuration):
    return buildingControl('config', building, confguration)

def bcolor(building, r, g, b):
    return buildingControl('color', building, r, g, b)


def add(var, a, b):
    return f"op add {var} {a} {b}"

def sub(var, a, b):
    return f"op sub {var} {a} {b}"

def mul(var, a, b):
    return f"op mul {var} {a} {b}"

def div(var, a, b):
    return f"op div {var} {a} {b}"

def idiv(var, a, b):
    return f"op idiv {var} {a} {b}"

def mod(var, a, b):
    return f"op mod {var} {a} {b}"

def pow(var, a, b):
    return f"op pow {var} {a} {b}"

def equal(var, a, b):
    return f"op equal {var} {a} {b}"

def notEqual(var, a, b):
    return f"op notEqual {var} {a} {b}"

def _and(var, a, b):
    return f"op land {var} {a} {b}"

def lessThan(var, a, b):
    return f"op lessThan {var} {a} {b}"

def lessThanEq(var, a, b):
    return f"op lessThanEq {var} {a} {b}"

def greaterThan(var, a, b):
    return f"op greaterThan {var} {a} {b}"

def greaterThanEq(var, a, b):
    return f"op greaterThanEq {var} {a} {b}"

def strictEqual(var, a, b):
    return f"op strictEqual {var} {a} {b}"

# op shl result a b
# op shr result a b
# op land result a b
# op and result a b
# op xor result a b
# op not result a b
def bitShiftLeft(var, a, b):
    return f"op shl {var} {a} {b}"

def bitShiftRight(var, a, b):
    return f"op shr {var} {a} {b}"

def bitor(var, a, b):
    return f"op or {var} {a} {b}"

def bitand(var, a, b):
    return f"op and {var} {a} {b}"

def bitxor(var, a, b):
    return f"op xor {var} {a} {b}"

def bitnot(var, a):
    return f"op not {var} {a} {b}"

def max(var, a, b):
    return f"op max {var} {a} {b}"

def min(var, a, b):
    return f"op min {var} {a} {b}"

def angle(var, a, b):
    return f"op angle"

def vlen(var, a, b):
    return f"op len {var} {a} {b}"

def noise(var, a, b):
    return f"op noise {var} {a} {b}"

def abs(var, a):
    return f"op abs {var} {a}"

def log(var, a):
    return f"op log {var} {a}"

def log10(var, a):
    return f"op log10 {var} {a}"

def sin(var, a):
    return f"op sin {var} {a}"

def cos(var, a):
    return f"op cos {var} {a}"

def tan(var, a):
    return f"op tan {var} {a}"

def floor(var, a):
    return f"op floor {var} {a}"

def ceil(var, a):
    return f"op ceil {var} {a}"

def sqrt(var, a):
    return f"op sqrt {var} {a}"

def rand(var, seed):
    return f"op rand {var} {seed}"

def operation(var, op, a, b='0'):
    return f"op {op} {var} {a} {b}"


def ubind(unitType):
    return f"ubind {unitType}"

def ucontrol(command, a=0, b=0, c=0, d=0, e=0):
    return f"ucontrol {command} {a} {b} {c} {d} {e}"

def uidle():
    return unitControl('idle')

def ustop():
    return unitControl('stop')

def umove(x, y):
    return unitControl('move', x, y)

def uapproach(x, y, radius):
    return unitControl('approach', x, y, radius)

def uboost(enable=True):
    return unitControl('boost', '1' if enable else '0')

def utarget(x, y, shoot=1):
    return unitControl('target', x, y, shoot)

def utargetp(unit, shoot=1):
    return unitControl('targetp', unit, shoot)

# ucontrol itemDrop 0 0 0 0 0
# ucontrol itemTake 0 0 0 0 0
# ucontrol payDrop 0 0 0 0 0
# ucontrol payTake 0 0 0 0 0
# ucontrol getBlock 0 0 0 0 0
def udropitem(to, amount):
    return unitControl('itemDrop', to, amount)

def utakeitem(building, item, amount):
    return unitControl('itemTake', building, item, amount)

def udroppayload():
    return unitControl('payDrop')

def utakepayload(numUnits):
    return unitControl('payTake', numUnits)

def umine(x, y):
    return unitControl('mine', x, y)

def uflag(value):
    return unitControl('flag', value)

def ubuild(x, y, block, rotation, configuration):
    return unitControl('build', x, y, block, rotation, configuration)

def ugetblock(x, y, type, building):
    return unitControl('getBlock', x, y, type, building)

def uwithin(x, y, radius, var):
    return unitControl('within')

# uradar any any any distance 0 order var
def uradar(var, unitType1='any', unitType2='any', unitType3='any', prioritize='distance', unitTypeOrderReversed=False):
    options(unitType1, unitTypes)
    options(unitType2, unitTypes)
    options(unitType3, unitTypes)
    options(prioritize, 'distance', 'health', 'shield', 'armor', 'maxHealth')
    return f"radar {unitType1} {unitType2} {unitType3} {prioritize} 0 {'0' if unitTypeOrderReversed else '1'} {var}"

# ulocate ore core true @copper outx outy found building
def ulocate(command, a, b, c, d, e, f, g):
    return f"ulocate {command} {a} {b} {c} {d} {e} {f} {g}"

# ulocate ore core true @copper outx outy found building
def ulocateore(ore, xvar, yvar, foundVar):
    return f"ulocate ore 0 0 {ore} {xvar} {yvar} {foundVar} 0"

# ulocate building core isEnemy @copper outx outy found var
def ulocatebuilding(type, isEnemy, xvar, yvar, foundVar, buildingVar):
    options(type, 'core', 'storage', 'generator', 'turret', 'factory', 'repair', 'rally', 'battery', 'resupply', 'reactor')
    return f"ulocate building {type} {'1' if isEnemy else 0} 0 {xvar} {yvar} {foundVar} {buildingVar}"

# ulocate spawn core isEnemy @copper outx outy found var
def ulocatespawn(xvar, yvar, foundVar, buildingVar):
    return f"ulocate spawn 0 0 0 {xvar} {yvar} {foundVar} {buildingVar}"

# ulocate damaged core isEnemy @copper outx outy found var
def ulocatedamaged(xvar, yvar, foundVar, buildingVar):
    return f"ulocate damaged 0 0 0 {xvar} {yvar} {foundVar} {buildingVar}"





mono     = '@mono'
poly     = '@poly'
mega     = "@mega"
risso    = "@risso"
minke    = "@minke"
bryde    = "@bryde"
alpha    = "@alpha"
beta     = "@beta"
gamma    = "@gamma"
flare    = "@flare"
horizon  = "@horizon"
zenith   = "@zenith"
dagger   = "@dagger"
mace     = "@mace"
fortress = "@fortress"
nova     = "@nova"
pulsar   = "@pulsar"
quasar   = "@quasar"
crawler  = "@crawler"
atrax    = "@atrax"
spiroct  = "@spiroct"

copper = '@copper'
lead = '@lead'
thorium = '@thorium'
titanium = '@titanium'
metaglass = '@metaglass'
sand = '@sand'
graphite = '@graphite'
coal = '@coal'
scrap = '@scrap'
silicon = '@silicon'
plastanium = '@plastanium'
phaseFabric = '@phase-fabric'
surgeAlloy = '@surge-alloy'
sporePod = '@spore-pod'
blastCompound = '@blast-compound'
pyratite = '@pyratite'

water = '@water'
slag = '@slag'
oil = '@oil'
cryofluid = '@cryofluid'

totalItems       = "@totalItems"
firstItem        = "@firstItem"
totalLiquids     = "@totalLiquids"
totalPower       = "@totalPower"
itemCapacity     = "@itemCapacity"
liquidCapacity   = "@liquidCapacity"
powerCapacity    = "@powerCapacity"
powerNetStored   = "@powerNetStored"
powerNetCapacity = "@powerNetCapacity"
powerNetIn       = "@powerNetIn"
powerNetOut      = "@powerNetOut"
ammo             = "@ammo"
ammoCapacity     = "@ammoCapacity"
health           = "@health"
maxHealth        = "@maxHealth"
heat             = "@heat"
efficiency       = "@efficiency"
timescale        = "@timescale"
rotation         = "@rotation"
x                = "@x"
y                = "@y"
shootX = shootx  = "@shootX"
shootY = shooty  = "@shootY"
size             = "@size"
dead             = "@dead"
range            = "@range"
shooting         = "@shooting"
boosting         = "@boosting"
mineX = minex    = "@mineX"
mineY = miney    = "@mineY"
mining           = "@mining"
team             = "@team"
type             = "@type"
flag             = "@flag"
controlled       = "@controlled"
controller       = "@controller"
name             = "@name"
config           = "@config"
payloadCount     = "@payloadCount"
payloadType      = "@payloadType"
enabled          = "@enabled"
configure        = "@configure"

unit = '@unit'
null = 'null'
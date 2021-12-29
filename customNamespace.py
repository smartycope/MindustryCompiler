from namespace import *

def printf(thing, to='message1'):
    return f"""
    print {thing}
    printflush {to}
    """
    # print(thing)
    # printFlush(to)

def getLinkOfType(type, buildingVar='building'):
    return """
    set('linkCounter', 0)
    getlink(var, 'linkCounter')
    sensor('buildingType', var, '@type')
    jump(-3, f"buildingType == @{type}")
    """

def getNormalLink(buildingVar='building'):
    return """
    set('linkCounter', 0)
    getlink(var, 'linkCounter')
    sensor('buildingType', var, '@type')
    jump(-3, f"buildingType == @message")
    jump(-4, f"buildingType == @processor")
    jump(-5, f"buildingType == @memorycell")
    """
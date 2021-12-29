#!/usr/bin/env python3
""" Cope.py
A bunch of generic functions and classes useful in multiple projects
"""
__version__ = '3.1.0'
__author__ = 'Copeland Carter'
__email__ = 'smartycope@gmail.com'
__license__ = 'GPL 3.0'
__copyright__ = '(c) 2021, Copeland Carter'


################################### Imports ###################################
import atexit
from math import tau, pi as PI
import re
from ctypes import pointer, py_object
from inspect import stack
from os.path import basename, dirname, join
from random import randint
from time import process_time
from typing import Any, Callable, Iterable, Optional, Union
from enum import Enum, auto

# try:
#     from varname import (ImproperUseError, VarnameRetrievingError, argname, nameof)
# except ImportError:
#     Warning("Can't import debug from Cope.py. Try running pip install varname.")
#     varnameImported = False
# else:
#     varnameImported = True


################################### Constants ###################################
# This is because I write a lot of C/C++ code
true, false = True, False

_debugCount = 0

# Override the debug parameters and display the file/function for each debug call
#   (useful for finding debug calls you left laying around and forgot about)
DISPLAY_FILE = False
DISPLAY_PATH = False
DISPLAY_FUNC = False
DISPLAY_LINK = False
HIDE_TODO    = False
# FORCE_TODO_LINK = False

# Default color constants
DEFAULT_COLOR = (204, 204, 204)
ALERT_COLOR =   (220, 0, 0)
WARN_COLOR =    (150, 30, 30)

#* A set of distinct characters for debugging
_colors = [(43, 142, 213), (19, 178, 118), (163, 61, 148), (255, 170, 0), (255, 170, 255), (170, 0, 255)]

# Default colors for debugging -- None for using the previously set color
NOTE_CALL_COLOR =     (211, 130, 0)
EMPTY_COLOR =         NOTE_CALL_COLOR
CONTEXT_COLOR =       None
COUNT_COLOR =         (34, 111, 157)
DEFAULT_DEBUG_COLOR = (34, 179, 99)
TODO_COLOR          = (128, 64, 64)
STACK_TRACE_COLOR   = (159, 148, 211)
CONFIDENCE_WARNING_COLOR = (255, 190, 70)
DEPRICATED_WARNING_COLOR = WARN_COLOR

DEBUG_METADATA_DARKEN = 60
DEBUG_TYPE_DARKEN     = 20
DEBUG_NAME_DARKEN     = -30
DEBUG_EQUALS_COLOR    = DEFAULT_COLOR
DEBUG_VALUE_DARKEN    = 0

#* Convenience commonly used paths. ROOT can be set by the setRoot() function
DIR  = dirname(__file__)
ROOT = dirname(DIR) if basename(DIR) in ('src', 'source') else DIR

# Yes, this is not strictly accurate.
MAX_INT_SIZE = 2147483645

VERBOSE = False

# A unique dummy class for parameters
class _None: pass

alphabet = 'abcdefghijklmnopqrstuvwxyz'

# todo make a todo override for the disable parameter just like displayALlFiles


################################### Setters for Globals ###################################
def displayAllFiles(to=True):
    global DISPLAY_FILE
    DISPLAY_FILE = to

def displayAllPaths(to=True):
    global DISPLAY_PATH
    DISPLAY_PATH = to

def displayAllFuncs(to=True):
    global DISPLAY_FUNC
    DISPLAY_FUNC = to

def displayAllLinks(to=True):
    global DISPLAY_LINK
    DISPLAY_LINK = to

def hideAllTodos(to=True):
    global HIDE_TODO
    HIDE_TODO = to

def setRoot(path):
    global ROOT
    ROOT = path

def setVerbose(to=True):
    global VERBOSE
    VERBOSE = to

def verbose():
    global VERBOSE
    return VERBOSE


################################### Enums ###################################
class CommonResponses:
    """ A collection of default responses for inputs. Make sure to use .lower() when testing agaisnt these.
        Note: There is some overlap between them, so testing order matters.
    """
    YES   = ('y', 'yes', 'ya', 'yeah', 'si', 'true', 'definitely', 'accurate', 'totally')
    NO    = ('n', 'no', 'not', 'nien', 'false', 'nope', 'not really', 'nah')
    MAYBE = ('sure', 'kinda', 'i guess', 'kind of', 'maybe', 'ish', 'sorta')
    NA    = ('none', 'na', 'n/a', 'not applicable')
    HIGH_AMOUNT = ('very', 'much', 'very much', 'extremely', 'quite', 'quite a bit', 'lot', 'a lot', 'lots',
                   'super', 'high', 'ton', 'a ton', 'bunch', 'a bunch')
    MODERATE_AMOUNT = ('fairly', 'somewhat', 'enough')
    SOME_AMOUNT = ('a little bit', 'a bit', 'a little', 'ish', 'not a lot', 'not a ton', 'some', 'mostly')
    LOW_AMOUNT  = ("not at all", 'not very', 'not much', 'low', 'none', 'none at all', 'not terribly')


################################### Color Utilites ###################################
def resetColor():
    print('\033[0m',  end='')
    print('\033[39m', end='')
    print('\033[49m', end='')
    # print('', end='')

#todo Add support for openGL colors (-1.0 to 1.0
#todo Consider changing the param paradigm to *rgba instead of all seperate parameters
def parseColorParams(r, g=None, b=None, a=None, bg=False) -> "((r, g, b, a), background)":
    """ Parses given color parameters and returns a tuple of equalized
        3-4 item tuple of color data, and a bool for background.
        Can take 3-4 tuple/list of color data, or r, g, and b as induvidual parameters,
        and a single int (0-5) representing a preset unique color id.
        a and bg are always available as optional or positional parameters.

        Note: Seperate color specifications for foreground and background are not currently
        supported. bg is just a bool.
    """
    #* We've been given a list of values
    if type(r) in (tuple, list):
        if len(r) not in (3, 4):
            raise SyntaxError(f'Incorrect number ({len(r)}) of color parameters given')
        else:
            return (tuple(r), (False if g is None else g) if not bg else bg)

    #* We've been given a single basic value
    elif type(r) is int and b is None:
        return (_colors[r] + ((a,) if a is not None else ()), (False if g is None else g) if not bg else bg)

    #* We've been given 3 seperate parameters
    elif type(r) is int and g is not None and b is not None:
        if type(a) is int:
            return ((r, g, b, a), bg)
        elif type(a) is bool or a is None:
            return ((r, g, b), bool(a) if not bg else bg)

    #* We've been given None
    elif r is None:
        return (DEFAULT_COLOR, bg)

    #* We're not sure how to interpret the parameters given
    else:
        raise SyntaxError(f'Incorrect color parameters {tuple(type(i) for i in (r, g, b, a, bg))} given')

class coloredOutput:
    """ A class to be used with the 'with' command to print colors.
        Resets after it's done.
        @Parameters:
            Takes either a 3 or 4 list/tuple of color arguements, 3 seperate
            color arguements, or 1 color id between 0-5 representing a distinct
            color. Set the curColor parameter (must be a 3 or 4 item list/tuple)
            to have the terminal reset to that color instead of white.
        https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
    """
    def __init__(self, r, g=None, b=None, foreground=True, curColor=DEFAULT_COLOR):
        color, bg = parseColorParams(r, g, b, bg=foreground)
        self.fg = bg
        self.r, self.g, self.b = color
        self.doneColor = curColor

    def __enter__(self):
        try:
            if self.fg:
                print(f'\033[38;2;{self.r};{self.g};{self.b}m', end='')
            else:
                print(f'\033[48;2;{self.r};{self.g};{self.b}m', end='')
        except:
            self.reset()

    def __exit__(self, *args):
        self.reset()

    def reset(self):
        print(f'\033[38;2;{self.doneColor[0]};{self.doneColor[1]};{self.doneColor[2]}m', end='')

def rgbToHex(rgb):
    """ Translates an rgb tuple of int to a tkinter friendly color code """
    return f'#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}'

def darken(amount, r, g=None, b=None, a=None):
    """ Returns the given color, but darkened. Make amount negative to lighten """
    # Constrain isn't defined yet and I don't feel like moving it
    return tuple([min(255, max(0, i - amount)) for i in parseColorParams(r, g, b, a)[0]])

def lighten(amount, r, g=None, b=None, a=None):
    """ Returns the given color, but darkened. Make amount negative to darken """
    return tuple([constrain(i + amount, 0, 255) for i in parseColorParams(r, g, b, a)[0]])

def clampColor(r, g=None, b=None, a=None):
    """ Clamp a 0-255 color to a float between 1 and 0.
        Helpful for openGL commands.
    """
    rgba = parseColorParams(r, g, b, a)[0]
    return tuple(c / 255 for c in rgba)

def invertColor(r, g=None, b=None, a=None):
    """ Inverts a color """
    rgba = parseColorParams(r, g, b, a)[0]
    return tuple(255 - c for c in rgba[0])

################################### Import Utilities ###################################
def checkImport(package:str, specificModules=[], _as=None,
                fatal:bool=False, printWarning:Union[str, bool]=True,
                _globals=globals(), _locals=locals(), level=0
                ) -> "(Union[package, (packages,)], worked)":
    if type(specificModules) is str:
        specificModules = [specificModules]
    try:
        _temp = __import__(package, _globals, _locals, specificModules, level)
    except ImportError:
        if type(printWarning) is str:
            print(printWarning)
        elif printWarning:
            if len(specificModules):
                print(f'Can\'t import {tuple(specificModules)} from {package}. Have you installed the associated pip package?')
            else:
                print(f'Can\'t import {package}. Have you installed the associated pip package?')
        if fatal:
            raise ImportError(package)
        return False
    else:
        if len(specificModules):
            for i in specificModules[:-1]:
                globals()[i] = _temp.__getattribute__(i)
            globals()[_as if _as else specificModules[-1]] = _temp.__getattribute__(specificModules[-1])
        else:
            globals()[_as if _as else package] = _temp
        return True

def dependsOnPackage(package:str, specificModules=[], _as=None,
                fatal:bool=True, printWarning:Union[str, bool]=True,
                _globals=globals(), _locals=locals(), level=0):
    def wrap(func):
        def innerWrap(*funcArgs, **funcKwArgs):
            if checkImport(package, specificModules, _as, fatal,
                           printWarning, globals, locals, level):
                return func(*funcArgs, **funcKwArgs)
            else:
                return None
        return innerWrap
    return wrap


################################### Debug ###################################
varnameImported = checkImport('varname', ('ImproperUseError', 'VarnameRetrievingError', 'argname', 'nameof'), fatal=False)

def _debugGetMetaData(calls=1):
    """ Gets the meta data of the line you're calling this function from.
        Calls is for how many function calls to look back from.
    """
    try:
        s = stack()[calls]
        return s
    except IndexError:
        return None

def _debugGetLink(calls=0, full=False, customMetaData=None):
    if customMetaData is not None:
        d = customMetaData
    else:
        d = _getMetaData(calls+2)

    _printLink(d.filename, d.lineno, d.function if full else None)

#todo This doesn't work right
#todo somehow round any float to a given length, including those printed in iterables
def _debugGetListStr(v: Union[tuple, list, set, dict], limitToLine: bool=True, minItems: int=2, maxItems: int=10) -> str:
    """ "Cast" a tuple, list, set or dict to a string, automatically shorten
        it if it's long, and display how long it is.

        Params:
            limitToLine: if True, limit the length of list to a single line
            minItems: show at least this many items in the list
            maxItems: show at most this many items in the list
            color: a simple int color

        Note:
            If limitToLine is True, it will overrule maxItems, but *not* minItems
    """
    if type(v) in (tuple, list, set) and len(v) > minItems:
        from copy import deepcopy
        from os import get_terminal_size
        if type(v) is set:
            v = tuple(v)

        ellipsis = f', ... '
        length = f'(len={len(v)})'

        if limitToLine:
            firstHalf  = str(v[0:round(minItems/2)])[:-1]
            secondHalf = str(v[-round(minItems/2)-1:-1])[1:]
            prevFirstHalf = firstHalf
            prevSecondHalf = secondHalf
            index = 0

            # The 54 is a fugde factor. I don't know why it needs to be there, but it works.
            while (6 + 54 + len(length) + len(firstHalf) + len(secondHalf)) < get_terminal_size().columns:
                index += 1
                firstHalf  = str(v[0:round((minItems+index)/2)])[:-1]
                secondHalf = str(v[-round((minItems+index)/2)-1:-1])[1:]
                prevFirstHalf = firstHalf
                prevSecondHalf = secondHalf
                if index > 6:
                    break

            firstHalf = prevFirstHalf
            secondHalf = prevSecondHalf

        else:
            firstHalf  = str(v[0:round(maxItems/2)])[:-1]
            secondHalf = str(v[-round(maxItems/2)-1:-1])[1:]

        return firstHalf + ellipsis + secondHalf + length

    else:
        return str(v) + f'(len={len(v)})'

def _debugGetTypename(var):
    if type(var) in (tuple, list, set):
        returnMe = type(var).__name__
        while type(var) in (tuple, list, set):
            try:
                var = var[0]
            except (KeyError, IndexError, TypeError):
                returnMe += '('
                break
            returnMe += '(' + type(var).__name__

        cnt = 0
        for i in returnMe:
            if i == '(':
                cnt += 1
        return returnMe + (')'*cnt)
    else:
        return type(var).__name__

def _debugPrintLink(filename, lineNum, function=None):
    """ Print a VSCodium clickable file and line number
        If function is specified, a full python error message style line is printed
    """
    try:
        _printColor(40, 43, 46)
        if function is None: #    \|/  Oddly enough, this double quote is nessicary
            print('\t', filename, '", line ', lineNum, '\033[0m', sep='')
        else:
            print('\tFile "', filename, '", line ', lineNum, ', in ', function, sep='')

        _resetColor()
    finally:
        _resetColor()
    _resetColor()
    print('\033[0m', end='')

def _printDebugCount(leftAdjust=2, color: int=COUNT_COLOR):
    global _debugCount
    _debugCount += 1
    with coloredOutput(color):
        print(f'{str(_debugCount)+":":<{leftAdjust+2}}', end='')

def _debugManualGetVarName(var, full=True, calls=2, metadata=None):
    try:
        return re.search(r'(?<=debug\().+(?=,(\s)?[name color showFunc showFile showPath useRepr calls background limitToLine minItems maxItems stackTrace raiseError clr _repr trace bg throwError throw \) ])',
                         metadata.code_context[0]).group()
    except:
        return '?'

def _debugGetVarName(var, full=True, calls=1, metadata=None):
    try:
        return argname('var', frame=calls+1)
    # It's a *likely* string literal
    except Exception as e:
        if type(var) is str:
            return None
        else:
            try:
                # print('var:', var)
                # print('var type:', type(var))
                return nameof(var, frame=calls+1)
            except Exception as e:
                if VERBOSE and not isinstance(var, Exception):
                    raise e
                else:
                    return _debugManualGetVarName(var, full, calls+1, metadata)
    except VarnameRetrievingError as e:
        if VERBOSE:
            raise e
        else:
            return _debugManualGetVarName(var, full, calls+1, metadata)

def _debugGetAdjustedFilename(filename):
    return filename[len(ROOT)+1:]

def _debugGetContext(metadata, useVscodeStyle, showFunc, showFile, showPath):
    #* Set the stuff in the [] (the "context")
    if metadata is not None:
        if useVscodeStyle:
            s = f'["{metadata.filename if showPath else _debugGetAdjustedFilename(metadata.filename)}", line {metadata.lineno}'
            if showFunc:
                if metadata.function.startswith('<'):
                    s += ', in Global Scope'
                else:
                    s += f', in {metadata.function}()'
            s += '] '
            return s
        else:
            context = str(metadata.lineno)
            if showFunc:
                if metadata.function.startswith('<'):
                    context = 'Global Scope' + context
                else:
                    context = metadata.function + '()->' + context

            if showFile:
                context = (metadata.filename if showPath else basename(metadata.filename)) + '->' + context

            return f'[{context}] '
    else:
        return ' '

def _debugPrintStackTrace(calls, useVscodeStyle, showFunc, showFile, showPath):
    for i in reversed(stack()[3:]):
        print('\t', _debugGetContext(i, useVscodeStyle, showFunc, showFile, showPath))

def _debugBeingUsedAsDecorator(funcName, metadata=None, calls=1) -> 'Union[1, 2, 3, False]':
    """ Return 1 if being used as a function decorator, 2 if as a class decorator, 3 if not sure, and False if neither. """
    if metadata is None:
        metadata = _debugGetMetaData(calls+1)

    # print(metadata.code_context)
    line = metadata.code_context[0]

    if funcName not in line:
        if 'def ' in line:
            return 1
        elif 'class ' in line:
            return 2
        elif '@' in line:
            return 3
    elif '@' in line:
        return 3

    return False

def printContext(calls=1, color=CONTEXT_COLOR, showFunc=True, showFile=True, showPath=True):
    _printDebugCount()
    with coloredOutput(color):
        print(_debugGetContext(_debugGetMetaData(1 + calls), True,
                               showFunc or DISPLAY_FUNC,
                               showFile or DISPLAY_FILE,
                               showPath or DISPLAY_PATH), end='')

def debug(var=_None,                # The variable to debug
          name: str=None,           # Don't try to get the name, use this one instead
          color=_None,              # A number (0-5), a 3 item tuple/list, or None
          showFunc: bool=True,      # Expressly show what function we're called from
          showFile: bool=True,      # Expressly show what file we're called from
          showPath: bool=False,     # Show just the file name, or the full filepath
          useRepr: bool=False,      # Whether we should print the repr of var instead of str
          calls: int=1,             # Add extra calls
          background: bool=False,   # Whether the color parameter applies to the forground or the background
          limitToLine: bool=True,   # When printing iterables, whether we should only print items to the end of the line
          minItems: int=50,         # Minimum number of items to print when printing iterables (overrides limitToLine)
          maxItems: int=-1,         # Maximum number of items to print when printing iterables, use None or negative to specify no limit
          stackTrace: bool=False,   # Print a stack trace
          raiseError: bool=False,   # If var is an error type, raise it
          clr=_None,                # Alias of color
          _repr: bool=False,        # Alias of useRepr
          trace: bool=False,        # Alias of stackTrace
          bg: bool=False,           # Alias of background
          throwError: bool=False,   # Alias of raiseError
          throw: bool=False         # Alias of raiseError
    ) -> "var":
    """ Print variable names and values for easy debugging.

        Usage:
            debug()          -> Prints a standard message to just tell you that it's getting called
            debug('msg')     -> Prints the string along with metadata
            debug(var)       -> Prints the variable name, type, and value
            foo = debug(bar) -> Prints the variable name, type, and value, and returns the variable
            @debug           -> Use as a decorator to make note of when the function is called

        Args:
            var: The variable or variables to print
            name: Manully specify the name of the variable
            color: A number between 0-5, or 3 or 4 tuple/list of color data to print the debug message as
            showFunc: Ensure that the function the current call is called from is shown
            showFile: Ensure that the file the current call is called from is shown
            showPath: Show the full path of the current file, isntead of it's relative path
            useRepr: Use __repr__() instead of __str__() on the given variable
            limitToLine: If var is a list/tuple/dict/set, only show as many items as will fit on one terminal line, overriden by minItems
            minItems: If var is a list/tuple/dict/set, don't truncate more than this many items
            maxItems: If var is a list/tuple/dict/set, don't show more than this many items
            stackTrace: Prints a neat stack trace of the current call
            calls: If you're passing in a return from a function, say calls=2
            background: Changes the background color instead of the forground color
            clr: Alias of color
            _repr: Alias of useRepr
            trace: Alias of stackTrace
            bg: Alias of background
    """
    stackTrace = stackTrace or trace
    useRepr = useRepr or _repr
    background = background or bg
    throwError = throw or throwError or raiseError
    useColor = (DEFAULT_DEBUG_COLOR if clr is _None else clr) if color is _None else color

    if maxItems < 0 or maxItems is None:
        maxItems = 1000000

    if isinstance(var, Warning):
        useColor = WARN_COLOR
    elif isinstance(var, Exception):
        useColor = ALERT_COLOR

    # +1 call because we don't want to get this line, but the one before it
    metadata = _debugGetMetaData(calls+1)

    #* First see if we're being called as a decorator
    if callable(var) and _debugBeingUsedAsDecorator('debug', metadata):
        def wrap(*args, **kwargs):
            # +1 call because we don't want to get this line, but the one before it
            metadata = _debugGetMetaData(2)

            _printDebugCount()

            if stackTrace:
                with coloredOutput(STACK_TRACE_COLOR):
                    _debugPrintStackTrace(2, True, showFunc, showFile, showPath)


            with coloredOutput(NOTE_CALL_COLOR):
                print(_debugGetContext(metadata, True, showFunc or DISPLAY_FUNC, showFile or DISPLAY_FILE, showPath or DISPLAY_PATH), end='')
                print(f'{var.__name__}() called!')

            return var(*args, **kwargs)

        return wrap

    _printDebugCount()

    if stackTrace:
        with coloredOutput(STACK_TRACE_COLOR):
            _debugPrintStackTrace(calls+1, True, showFunc, showFile, showPath)

    #* Only print the "HERE! HERE!" message
    if var is _None:
        with coloredOutput(useColor if color is not _None else EMPTY_COLOR, not background):
            print(_debugGetContext(metadata, True, showFunc or DISPLAY_FUNC, showFile or DISPLAY_FILE, showPath or DISPLAY_PATH), end='')
            if not metadata.function.startswith('<'):
                print(f'{metadata.function}() called ', end='')
            print('HERE!')
        return


    metadataColor = darken(DEBUG_METADATA_DARKEN,  useColor)
    typeColor     = darken(DEBUG_TYPE_DARKEN,  useColor)
    nameColor     = darken(DEBUG_NAME_DARKEN, useColor)
    equalsColor   = DEBUG_EQUALS_COLOR
    valueColor    = darken(DEBUG_VALUE_DARKEN, useColor)
    #* Print the standard line
    with coloredOutput(metadataColor, not background):
        print(_debugGetContext(metadata, True,
                                showFunc or DISPLAY_FUNC,
                                showFile or DISPLAY_FILE,
                                showPath or DISPLAY_PATH), end='')

    #* Seperate the variables into a tuple of (typeStr, varString)
    varType = _debugGetTypename(var)
    if useRepr:
        varVal = repr(var)
    else:
        if type(var) in (tuple, list, set, dict):
            varVal  = _debugGetListStr(var, limitToLine, minItems, maxItems)
        else:
            varVal  = str(var)

    with coloredOutput(nameColor, not background):
        #* Actually get the name
        varName = _debugGetVarName(var, calls=calls, metadata=metadata) if name is None else name
        # It's a string literal
        if varName is None:
            print(var)
            return

    with coloredOutput(typeColor, not background):
        print(varType, end=' ')
    with coloredOutput(nameColor, not background):
        print(varName, end=' ')
    with coloredOutput(equalsColor, not background):
        print('=', end=' ')
    with coloredOutput(valueColor, not background):
        print(varVal)

    if isinstance(var, Exception) and throwError:
        raise var

    # Does the same this as debugged used to
    return var


################################### Decorators ###################################
def todo(featureName=None, enabled=True, blocking=True, showFunc=True, showFile=True, showPath=False):
    """ Leave reminders for yourself to finish parts of your code.
        Can be manually turned on or off with hideAllTodos(bool).
        Can also be used as a decorator (function, or class) to print a reminder
        and also throw a NotImplemented error on being called/constructed.
    """
    metadata  = _debugGetMetaData(2)
    situation = _debugBeingUsedAsDecorator('todo', metadata)
    # def decorator(*decoratorArgs, **decoratorKwArgs):
    #     def wrap(func):
    #         def innerWrap(*funcArgs, **funcKwArgs):
    #             return func(*funcArgs, **funcKwArgs)
    #         return innerWrap
    #     return wrap

    def printTodo(disableFunc):
        if not HIDE_TODO and enabled:
            _printDebugCount()
            with coloredOutput(TODO_COLOR):
                print(_debugGetContext(metadata, True,
                                      (showFunc or DISPLAY_FUNC) and not disableFunc,
                                       showFile or DISPLAY_FILE,
                                       showPath or DISPLAY_PATH), end='')
                # This is coincidental, but it works
                print(f'TODO: {featureName.__name__ if disableFunc else featureName}')

    # Being used as a function decorator, or we're not sure
    if situation in (1, 3):
        def wrap(func):
            def innerWrap(*funcArgs, **funcKwArgs):
                printTodo(True)
                if blocking:
                    raise NotImplementedError()
                return featureName(*funcArgs, **funcKwArgs)
            return innerWrap
        return wrap

    elif situation == 2:
        def wrap(clas):
            def raiseErr(*_, **kw_):
                raise NotImplementedError()
            printTodo(True)
            if blocking:
                featureName.__init__ = raiseErr
        return featureName
    else:
        printTodo(False)

def confidence(level):
    def wrap(func):
        def innerWrap(*funcArgs, **funcKwArgs):
            def definiteFail():
                raise UserWarning(f"{func.__name__} is going to fail.")

            def probablyFail():
                printContext(2, darken(80, ALERT_COLOR), showFunc=False)
                with coloredOutput(ALERT_COLOR):
                    print(f"Warning: {func.__name__} will probably fail")

            def possiblyFail():
                printContext(2, darken(80, CONFIDENCE_WARNING_COLOR), showFunc=False)
                with coloredOutput(CONFIDENCE_WARNING_COLOR):
                    print(f"Warning: {func.__name__} might not work")

            def unknownInput():
                raise TypeError(f"I don't recognize {level} as a confidence level.")

            if type(level) is int:
                if level > 100:
                    raise TypeError(f"You can't be {level}% confident, that's not how it works.")
                elif level < 0:
                    definiteFail()
                elif level < 20:
                    probablyFail()
                elif level < 50:
                    possiblyFail()
            elif type(level) is str:
                l = level.lower()
                if l in CommonResponses.NO or l in CommonResponses.LOW_AMOUNT:
                    probablyFail()
                elif l in CommonResponses.MAYBE or l in CommonResponses.SOME_AMOUNT:
                    possiblyFail()
                elif l not in CommonResponses.YES and l not in CommonResponses.HIGH_AMOUNT and \
                     l not in CommonResponses.NA  and l not in CommonResponses.MODERATE_AMOUNT:
                    unknownInput()
            else:
                unknownInput()

            return func(*funcArgs, **funcKwArgs)
        return innerWrap
    return wrap
confident = confidence

def depricated(why=''):
    def wrap(func):
        def innerWrap(*funcArgs, **funcKwArgs):
            printContext(2, darken(80, DEPRICATED_WARNING_COLOR))
            with coloredOutput(DEPRICATED_WARNING_COLOR):
                print(f"{func.__name__} is Depricated{': ' if len(why) else '.'}{why}")
            return func(*funcArgs, **funcKwArgs)
        return innerWrap
    return wrap

def reprise(obj, *args, **kwargs):
    """ Sets the __repr__ function to the __str__ function of a class.
        Useful for custom classes with overloaded string functions
    """
    obj.__repr__ = obj.__str__
    return obj


################################### Iterable Utilities ###################################
def isiterable(obj):
    return isinstance(obj, Iterable)

def ensureIterable(obj, useList=False):
    if not isinstance(obj, Iterable):
        return [obj, ] if useList else (obj, )
    else:
        return obj

def ensureNotIterable(obj, emptyBecomes=_None):
    if isinstance(obj, Iterable):
        if len(obj) == 1:
            try:
                return obj[0]
            except TypeError:
                return list(obj)[0]
        elif len(obj) == 0:
            return obj if emptyBecomes is _None else emptyBecomes
        else:
            return obj
    else:
        return obj

def flattenList(iterable, recursive=False, useList=True):
    if recursive:
        raise NotImplementedError

    useType = list if useList else type(iterable)
    rtn = useType()
    for i in iterable:
        rtn += useType(i)
    return rtn
    # print(flattenList(('a', 'b', [1, 2, 3]), useList=False))

def removeDuplicates(iterable):
    return type(iterable)(set(iterable))

def normalizeList(iterable, ensureList=False):
    if ensureList:
        return removeDuplicates(flattenList(ensureIterable(list(iterable), True)))
    else:
        return ensureNotIterable(removeDuplicates(flattenList(ensureIterable(list(iterable), True))))

def getIndexWith(obj, key):
    """ Returns the index of the first object in a list in which key returns true to.
    Example: getIndexWith([ [5, 3], [2, 3], [7, 3] ], lambda x: x[0] + x[1] == 10) -> 2
    If none are found, returns None
    """
    for cnt, i in enumerate(obj):
        if key(i):
            return cnt
    return None

def invertDict(d):
    """ Returns the dict given, but with the keys as values and the values as keys. """
    return dict(zip(d.values(), d.keys()))

@todo
class LoopingList(list):
    """ It's a list, that, get this, loops!
    """
    def __getitem__(self, index):
        if index > self.__len__():
            return super().__getitem__(index % self.__len__())
        else:
            return super().__getitem__(index)


################################### Timing Utilities ###################################
timingData = {}
def timeFunc(func, accuracy=5):
    """ A function decorator that prints how long it takes for a function to run """
    def wrap(*params, **kwparams):
        global timingData

        t = process_time()

        returns = func(*params, **kwparams)

        t2 = process_time()

        elapsed_time = round(t2 - t, accuracy)
        name = func.__name__

        try:
            timingData[name] += (elapsed_time,)
        except KeyError:
            timingData[name] = (elapsed_time,)

        _printDebugCount()
        # print(name, ' ' * (10 - len(name)), 'took', elapsed_time if elapsed_time >= 0.00001 else 0.00000, '\ttime to run.')
        print(f'{name:<12} took {elapsed_time:.{accuracy}f} seconds to run.')
        #  ' ' * (15 - len(name)),
        return returns
    return wrap

def _printTimingData(accuracy=5):
    """ I realized *after* I wrote this that this is a essentially profiler. Oops. """
    global timingData
    if len(timingData):
        print()

        maxName = len(max(timingData.keys(), key=len))
        maxNum  = len(str(len(max(timingData.values(), key=lambda x: len(str(len(x)))))))
        for name, times in reversed(sorted(timingData.items(), key=lambda x: sum(x[1]))):
            print(f'{name:<{maxName}} was called {len(times):<{maxNum}} times taking {sum(times)/len(times):.{accuracy}f} seconds on average for a total of {sum(times):.{accuracy}f} seconds.')
atexit.register(_printTimingData)

class getTime:
    """ A class to use with a with statement like so:
        with getTime('sleep'):
            time.sleep(10)
        It will then print how long the enclosed code took to run.
    """
    def __init__(self, name, accuracy=5):
        self.name = name
        self.accuracy = accuracy

    def __enter__(self):
        self.t = process_time()

    def __exit__(self, *args):
        # args is completely useless, not sure why it's there.
        t2 = process_time()
        elapsed_time = round(t2 - self.t, self.accuracy)
        print(self.name, ' ' * (15 - len(self.name)), 'took', f'{elapsed_time:.{self.accuracy}f}', '\ttime to run.')


################################### Misc. Useful Functions ###################################
@todo('Make this use piping and return the command output', False)
def runCmd(args):
    """ Run a command and terminate if it fails. """
    try:
        ec = subprocess.call(' '.join(args), shell=True)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        ec = 1
    if ec:
        sys.exit(ec)

def percent(percentage):
    ''' Usage:
        if (percent(50)):
            <code that has a 50% chance of running>
    '''
    return randint(1, 100) < percentage

def randbool():
    """ Returns, randomly, either True or False """
    return bool(randint(0, 1))

def closeEnough(a, b, tolerance):
    """ Returns True if a is within tolerance range of b """
    return a <= b + tolerance and a >= b - tolerance

def findClosestValue(target, comparatorList) -> "value":
    """ Finds the value in comparatorList that is closest to target """
    # dist = max_distance
    # value = None
    # index = 0
    # for cnt, current in enumerate(comparatorList):
    #     currentDist = abs(target - current)
    #     if currentDist < dist:
    #         dist = currentDist
    #         value = current
    #         index = cnt
    # return (value, index)
    return min(comparatorList, key=lambda x: abs(target - x))

def findFurthestValue(target, comparatorList) -> "value":
    """ Finds the value in comparatorList that is furthest from target """
    return max(comparatorList, key=lambda x: abs(target - x))

def absdeg(angle):
    """ If an angle (in degrees) is not within 360, then this cuts it down to within 0-360 """
    angle = angle % 360.0
    if angle < 0:
        angle += 360
    return angle

def absrad(angle):
    """ If an angle (in radians) is not within 2Pi, then this cuts it down to within 0-2Pi """
    angle = angle % math.tau
    if angle < 0:
        angle += math.tau
    return angle

def center(string):
    """ Centers a string for printing in the terminal """
    from os import get_terminal_size
    for _ in range(int((get_terminal_size().columns - len(string)) / 2)): string = ' ' + string
    return string

def isPowerOf2(x):
    """ Returns true if x is a power of 2 """
    return (x != 0) and ((x & (x - 1)) == 0)

def isBetween(val, start, end, beginInclusive=False, endInclusive=False):
    """ Returns true if val is between start and end """
    return (val >= start if beginInclusive else val > start) and \
           (val <= end   if endInclusive   else val < end)

def insertChar(string, index, char):
    """ Returns the string with char inserted into string at index. Freaking python string are immutable. """
    return string[:index] + char + string[index+1:]

def constrain(val, low, high):
    """ Constrains val to be within low and high """
    return min(high, max(low, val))

def translate(value, fromStart, fromEnd, toStart, toEnd):
    return ((abs(value - fromStart) / abs(fromEnd - fromStart)) * abs(toEnd - toStart)) + toStart

def frange(start, stop, skip=1.0, accuracy=10000000000000000):
    return [x / accuracy for x in range(int(start*accuracy), int(stop*accuracy), int(skip*accuracy))]

def getDist(ax, ay, bx, by):
    return math.sqrt(((bx - ax)**2) + ((by - ay)**2))

def deg2rad(a, symbolic=False):
    if symbolic:
        if checkImport('sympy', 'pi', fatal=True):
            return (a * pi / 180).simplify()
    else:
        return a * PI / 180.0

def rad2deg(a, symbolic=False):
    if symbolic:
        if checkImport('sympy', 'pi', fatal=True):
            return (a * 180 / pi).simplify()
    else:
        return a * 180.0 / PI

def normalize2rad(a):
    while a < 0: a += math.tau
    while a >= math.tau: a -= math.tau
    return a

def normalize2deg(a):
    while a < 0: a += 360
    while a >= 360: a -= 360
    return a

def portFilename(filename):
    return join(*filename.split('/'))


################################### Misc. Useful Classes ###################################
class FunctionCall:
    """ A helpful class that represents an as-yet uncalled function call with parameters """
    def __init__(self, func=lambda: None, args=(), kwargs={}):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def call(self, *args, override_args=False, **kwargs):
        return self.__call__(*args, override_args, **kwargs)

    def __call__(self, *args, override_args=False, **kwargs):
        """ If you specify parameters and don't explicitly set override_args to True,
            then the given parameters are ignored and the previously set parameters are used.
        """
        if override_args:
            return self.func(*args, **kwargs)
        else:
            return self.func(*self.args, **self.kwargs)

class Signal:
    """ A custom Signal implementation. Connect with the connect() function """
    def __init__(self):
        self.funcs = []
        self.call = self.__call__

    def connect(self, func, *args, **kwargs):
        self.funcs.append(FunctionCall(func, args, kwargs))

    def __call__(self, *args, override_args=False, **kwargs):
        """ If you specify parameters and don't explicitly set override_args to True,
            then the given parameters are ignored and the previously set parameters are used.
            WARNING: If override_args is set to True, the given parameters will be passed into
            every function given with connect().
        """
        # rtns = ()
        for f in self.funcs:
            f(*args, override_args=override_args, **kwargs)

        # return rtns[0] if len(rtns) <= 1 else rtns

class _Key(Enum):
    unknown=0
    space=32; exclamation=33; doubleQuote=34; pound=hashtag=35; dollarSign=36; percent=37; andersand=38; singleQuote=39; openParen=40; closeParen=41; star=42; plus=43; comma=44; minus=45; period=46; slash=forwardSlash=47
    one=48; two=49; three=50; four=51; five=52; six=53; seven=54; eight=55; nine=56; zero=57
    colon=58; semicolon=59; lessThan=60; equals=61; greaterThan=62; question=63; attersand=64
    A=65; B=66; C=67; D=68; E=69; F=70; G=71; H=72; I=73; J=74; K=75; L=76; M=77; N=78; O=79; P=80; Q=81; R=82; S=83; T=84; U=85; V=86; W=87; X=88; Y=89; Z=90
    openSquareBracket=91; backslash=92; closeSquareBracket=93; exponent=94; underscore=95; sidilla=96
    a=97; b=98; c=99; d=100; e=101; f=102; g=103; h=104; i=105; j=106; k=107; l=108; m=109; n=110; o=111; p=112; q=113; r=114; s=115; t=116; u=117; v=118; w=119; x=120; y=121; z=122
    openCurlyBrace=123; orLine=124; closeCurlyBrace=125; tilde=126

    F1=131; F2=132; F3=133; F4=134; F5=135; F6=136; F7=137; F8=138; F9=139; F10=140; F11=141; F12=142; F13=143; F14=144; F15=145; F16=146
    F17=147; F18=148; F19=149; F20=150; F21=151; F22=152; F23=153; F24=154; F25=155; F26=156; F27=157; F28=158; F29=159; F30=160

    escape=27
    delete=127; backspace=auto()
    home=auto(); end=auto()
    enter=auto()
    shift=auto(); ctrl=auto(); win=command=auto(); alt=auto()
    insert=auto(); pageUp=auto(); pageDown=auto()
    up=auto(); down=auto(); left=auto(); right=auto()
    printScreen=auto(); scrollLock=auto();
    pause=auto(); break_=auto()
    numLock=auto()

class Key:
    """ A generalized Key class to bridge the gap between several standards.
        when possible, constants are set to their ascii values. The other keys use auto()
        F1-F30 are mapped to 131-160 arbitrarily
        Mouse buttons are not included.
    """
    _psuedonyms = {
        'spacebar': _Key.space,
        'windowskey': _Key.win,
        'at': _Key.attersand,
        'and': _Key.andersand,
        'questionmark': _Key.question,
        'exclamationmark': _Key.exclamation,
        'exclamationpoint': _Key.exclamation,
        "\'": _Key.singleQuote,
        "\"": _Key.doubleQuote,
        "\\": _Key.backslash,
        "`": _Key.sidilla,
        "~": _Key.tilde,
        "!": _Key.exclamation,
        "@": _Key.attersand,
        "#": _Key.pound,
        "$": _Key.dollarSign,
        "%": _Key.percent,
        "^": _Key.exponent,
        "&": _Key.andersand,
        "*": _Key.star,
        "(": _Key.openParen,
        ")": _Key.closeParen,
        "_": _Key.underscore,
        "+": _Key.plus,
        "{": _Key.openCurlyBrace,
        "}": _Key.closeCurlyBrace,
        "|": _Key.orLine,
        ":": _Key.colon,
        "<": _Key.lessThan,
        ">": _Key.greaterThan,
        "?": _Key.question,
        "1": _Key.one,
        "2": _Key.two,
        "3": _Key.three,
        "4": _Key.four,
        "5": _Key.five,
        "6": _Key.six,
        "7": _Key.seven,
        "8": _Key.eight,
        "9": _Key.nine,
        "0": _Key.zero,
        "-": _Key.minus,
        "=": _Key.equals,
        "[": _Key.openSquareBracket,
        "]": _Key.closeSquareBracket,
        ",": _Key.comma,
        ".": _Key.period,
        "/": _Key.forwardSlash,
        ';': _Key.semicolon,
        "backspace": _Key.backspace,
        "return": _Key.enter,
        "cmd": _Key.command,
    }

    @staticmethod
    def parseKey(key:str) -> int:
        err = TypeError(f'"{key}" is an invalid key')

        try:
            return getattr(_Key, key)
        except AttributeError:
            key = key.lower()
            try:
                return getattr(_Key, key)
            except AttributeError:
                if key in Key._psuedonyms.keys():
                    return Key._psuedonyms[key]
                else:
                    raise err

    def _parseParam(self, key)->int:
        if type(key) is _Key:
            key = _Key.key

        if type(key) is str:
            return self.parseKey(key)
        elif type(key) in int:
            if isBetween(key, 1, 9):
                return key + 48
            elif key == 0:
                return 57
            elif isBetween(key, 32, 127):
                return key
            else:
                raise TypeError(f'{key} is an invalid ascii character, or is not implemented')

    def __init__(self, key:Union[_Key, str, int]):
        self.key = self._parseParam(key)

    def __eq__(self, other):
        if type(other) is Key:
            return self.key == other.key
        elif type(other) is _Key:
            return self.key == other
        elif type(other) is str:
            return self.key == self._parseParam(other)
        else:
            return TypeError(f"Cannot compare types of {type(other).__name__} and Key")

    def __hash__(self):
        return hash(self.key)

    def __getattr__(self, key):
        debug()
        return Key(self._parseParam(key))

    def __str__(self):
        return str(self.key)
# modifierKeys = (Key.shift, Key.ctrl, Key.win, Key.alt)
modifierKeys = (Key("shift"), Key("ctrl"), Key("win"), Key("alt"))

class KeyShortcut:
    def __init__(self, *keys):
        self.triggered = Signal()
        self.keys = keys
        self.activeMods = dict(zip(modifierKeys, (False,) * len(modifierKeys)))

    def update(self, key, pressed):
        if key in modifierKeys:
           self.activeMods[key] = pressed

        valid = True
        for i in self.keys:
            if i in modifierKeys:
                if not self.activeMods[i]:
                    valid = False
            else:
                if key != i:
                    valid = False

        if valid:
            self.triggered.call()

# @todo
class KeyChord:
    pass

class KeySequence:
    triggered = Signal()
    def __init__(self, *keySequence):
        self.sequence = keySequence
        self.activeMods = dict(zip(modifierKeys, (False,) * len(modifierKeys)))
        self.currentSequence = []

    def update(self, key, pressed):
        todo('not finished', blocking=True)
        if key in modifierKeys:
           self.activeMods[key] = pressed

        self.currentSequence.append(key)

        valid = True
        for i in self.keys:
            if i in modifierKeys:
                if not self.activeMods[i]:
                    valid = False
            else:
                if key != i:
                    valid = False

        if valid:
            triggered.call()
        else:
            self.currentSequence = []


################################### API Specific functions ###################################
#* PrettyTable
@dependsOnPackage('prettytable', 'PrettyTable')
def quickTable(listOfLists, interpretAsRows=True, fieldNames=None, returnStr=False, sortByField:str=False, sortedReverse=False):
    """ A small, quick wrapper for the prettytable library """
    t = PrettyTable()
    if interpretAsRows:
        if fieldNames is not None:
            t.field_names = fieldNames
        t.add_rows(listOfLists)
    else:
        for i in listOfLists:
            t.add_column(str(i[0]), i[1:])
    if sortByField:
        t.sortby = sortByField
        t.reversesort = sortedReverse

    return t.get_string() if returnStr else t

#* My Own Point Classes
@dependsOnPackage('Point', 'Point')
def findClosestXPoint(target, comparatorList, offsetIndex = 0):
    """ I've forgotten what *exactly* this does. I think it finds the point in a list of
        points who's x point is closest to the target
    """
    finalDist = 1000000
    result = 0

    # for i in range(len(comparatorList) - offsetIndex):
    for current in comparatorList:
        # current = comparatorList[i + offsetIndex]
        currentDist = abs(target.x - current.x)
        if currentDist < finalDist:
            result = current
            finalDist = currentDist

    return result

@dependsOnPackage('Point', ('Point', 'Pointi', 'Pointf'))
def getPointsAlongLine(p1, p2):
    """ I don't remember what this does. """
    p1 = Pointi(p1)
    p2 = Pointi(p2)

    returnMe = []

    dx = p2.x - p1.x
    dy = p2.y - p1.y

    for x in range(p1.x, p2.x):
        y = p1.y + dy * (x - p1.x) / dx
        returnMe.append(Pointf(x, y))

    return returnMe

@dependsOnPackage('Point', 'Point')
def rotatePoint(p, angle, pivotPoint, radians = False):
    """ This rotates one point around another point a certain amount, and returns it's new position """
    if not radians:
        angle = math.radians(angle)
    # p -= pivotPoint
    # tmp = pygame.math.Vector2(p.data()).normalize().rotate(amount)
    # return Pointf(tmp.x, tmp.y) + pivotPoint

    dx = p.x - pivotPoint.x
    dy = p.y - pivotPoint.y
    newX = dx * math.cos(angle) - dy * math.sin(angle) + pivotPoint.x
    newY = dx * math.sin(angle) + dy * math.cos(angle) + pivotPoint.y

    return Pointf(newX, newY)

@dependsOnPackage('Point', 'Point')
def getMidPoint(p1, p2):
    """ Returns the halfway point between 2 given points """
    assert type(p1) == type(p2)
    # return Pointf((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    return p1._initCopy((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)

@dependsOnPackage('Point', 'Point')
def findClosestPoint(target, comparatorList):
    """ Finds the closest point in the list to what it's given"""
    finalDist = 1000000

    for i in comparatorList:
        current = getDist(target, i)
        if current < finalDist:
            finalDist = current

    return finalDist

@dependsOnPackage('Point', 'Point')
def collidePoint(topLeft: 'Point', size: Union[tuple, list, 'Size'], target, inclusive=True):
    """ Returns true if target is within the rectangle given by topLeft and size """
    return isBetween(target.x, topLeft.x, size[0], beginInclusive=inclusive, endInclusive=inclusive) and \
           isBetween(target.y, topLeft.y, size[1], beginInclusive=inclusive, endInclusive=inclusive)

@dependsOnPackage('Point', 'Point')
def getPointDist(a: 'Point', b: 'Point'):
    return math.sqrt(((b.x - a.x)**2) + ((b.y - a.y)**2))

#* Pygame
@dependsOnPackage('pygame')
def loadImage(filename):
    # if pygame.image.get_extended():
    filename = '/' + portableFilename(DATA + '/' + filename)

    image = pygame.image.load(filename)
    # self.image = self.image.convert()
    image = image.convert_alpha()
    # else:
    #     assert(not f"Cannot support the file extension {}")
    return image

def loadAsset(dir, name, extension='png'):
    return loadImage(dir + name + '.' + extension)

@dependsOnPackage('pygame')
def rotateSurface(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
    rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot+rotated_offset)
    return rotated_image, rect  # Return the rotated image and shifted rect.


################################### Old Functions I Don't Want to Delete ###################################
# I don't remember what this does and I'm scared to delete it
@confidence(45)
@dependsOnPackage('tkinter', _as='tk')
@dependsOnPackage('tkinter.ttk', _as='ttk')
@dependsOnPackage('contextlib', 'redirect_stdout')
@dependsOnPackage('ttkthemes')
def stylenameElementOptions(stylename):
    '''Function to expose the options of every element associated to a widget
       stylename.'''
    with open('tmp.del', 'a') as f:
        with redirect_stdout(f):
            print('\n-----------------------------------------------------------------------------\n')
            try:
                # Get widget elements
                style = ttk.Style()
                layout = str(style.layout(stylename))
                print('Stylename = {}'.format(stylename))
                print('Layout    = {}'.format(layout))
                elements=[]
                for n, x in enumerate(layout):
                    if x=='(':
                        element=""
                        for y in layout[n+2:]:
                            if y != ',':
                                element=element+str(y)
                            else:
                                elements.append(element[:-1])
                                break
                print('\nElement(s) = {}\n'.format(elements))
                # Get options of widget elements
                for element in elements:
                    print('{0:30} options: {1}'.format(
                        element, style.element_options(element)))
            except tk.TclError:
                print('_tkinter.TclError: "{0}" in function'
                    'widget_elements_options({0}) is not a regonised stylename.'
                    .format(stylename))

    # for i in ['TButton', 'TCheckbutton', 'TCombobox', 'TEntry', 'TFrame', 'TLabel', 'TLabelFrame', 'TMenubutton', 'TNotebook', 'TPanedwindow', 'Horizontal.TProgressbar', 'Vertical.TProgressbar', 'TRadiobutton', 'Horizontal.TScale', 'Vertical.TScale', 'Horizontal.TScrollbar', 'Vertical.TScrollbar', 'TSeparator', 'TSizegrip', 'Treeview', 'TSpinbox']:
    #     stylenameElementOptions('test.' + i)

    # stylenameElementOptions('me.TButton')

@depricated
def ref(obj):
    return pointer(py_object(obj))

@depricated
def deref(ptr):
    return ptr.contents.value


################################### Notes ###################################
""" DECORATOR SYNTAX:

def decorator(*decoratorArgs, **decoratorKwArgs):
    def wrap(functionBeingDecorated):
        def innerWrap(*decoratedArgs, **decoratedKwArgs):
            return functionBeingDecorated(*decoratedArgs, **decoratedKwArgs)
        return innerWrap
    return wrap

COPY version:

def decorator(*decoratorArgs, **decoratorKwArgs):
    def wrap(func):
        def innerWrap(*funcArgs, **funcKwArgs):
            return func(*funcArgs, **funcKwArgs)
        return innerWrap
    return wrap
"""


################################### Tests ###################################
#* parseColorParams tests
if False:
    # setVerbose(True)
    # debug(parseColorParams((5, 5, 5)) )
    # debug(parseColorParams((5, 5, 5), True) )
    # debug(parseColorParams((5, 5, 5, 6)) )
    # debug(parseColorParams((5, 5, 5, 6), True) )
    # debug(parseColorParams([5, 5, 5, 6]) )
    # debug(parseColorParams(5, 5, 5) )
    # debug(parseColorParams(5, 5, 5, True) )
    # debug(parseColorParams(5, 5, 5, 6) )
    # debug(parseColorParams(5, 5, 5, bg=True) )
    # debug(parseColorParams(5, 5, 5, 6, True) )
    # debug(parseColorParams(3) )
    # debug(parseColorParams(3, bg=True)
    # debug(parseColorParams((3,)) ) # Succeeded
    # debug(parseColorParams(3, a=6) )
    # debug(parseColorParams(3, a=6, bg=True) )
    # debug(parseColorParams(None) )
    # debug(parseColorParams(None, bg=True) )
    pass

#* debug tests
if False:
    # setVerbose(True)
    a = 6
    s = 'test'
    j = None
    def testFunc():
        print('testFunc called')

    debug(a)
    debug(a, 'apple')

    debug('test3')
    debug(s)

    debug(j)
    debug()

    debug(testFunc)

    foo = debug(a)
    debug(foo)

    debug(parseColorParams((5, 5, 5)) )

    debug(SyntaxError('Not an error'))
    try:
        debug(SyntaxError('Not an error'), raiseError=True)
    except SyntaxError:
        print('SyntaxError debug test passed!')
    else:
        print('SyntaxError debug test failed.')

    debug(UserWarning('Not a warning'))
    try:
        debug(UserWarning('Not a warning'), raiseError=True)
    except UserWarning:
        print('UserWarning debug test passed!')
    else:
        print('UserWarning debug test failed.')

    @debug
    def testFunc2():
        print('testFunc2 (decorator test) called')

    debug()

    testFunc2()

    debug(None)

    TUPLE = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    LIST  = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    DICT  = {'a':1, 'b':2, 'c': 3}
    TYPE_LIST = ['a', 2, 7.4, 3]
    TYPE_TUPLE = ('a', 2, 7.4, 3)

    debug([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], raiseError=True)
    debug((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), raiseError=True)
    debug({'a':1, 'b':2, 'c': 3}, raiseError=True)
    debug(['a', 2, 7.4, 3], raiseError=True)
    debug(('a', 2, 7.4, 3), raiseError=True)
    debug()
    debug(TUPLE, raiseError=True)
    debug(LIST, raiseError=True)
    debug(DICT, raiseError=True)
    debug(TYPE_LIST, raiseError=True)
    debug(TYPE_TUPLE, raiseError=True)

#* todo tests
if False:
    todo('testing todo')
    todo('testing todo 2', False)

    @todo
    def unfinishedFunc():
        print("this func is unfin")

    try:
        unfinishedFunc()
    except NotImplementedError:
        print("func decorator test worked!")
    else:
        print("func decorator test failed.")

    @todo(blocking=False)
    def unfinishedFunc2():
        print("this non Blocking func is unfin")

    unfinishedFunc2()

    @todo
    class unfinishedClass:
        def __init__(self):
            print('this class is unfin')

    try:
        x = unfinishedClass()
    except NotImplementedError:
        print("class decorator test worked!")
    else:
        print("class decorator test failed.")

#* Decorator Testing
if False:
    def decorator(*decoratorArgs, **decoratorKwArgs):
        def wrap(functionBeingDecorated):
            def innerWrap(*decoratedArgs, **decoratedKwArgs):
                debug(decoratorArgs)
                debug(decoratorKwArgs)
                debug(functionBeingDecorated)
                debug(decoratedArgs)
                debug(decoratedKwArgs)
                return functionBeingDecorated(*decoratedArgs, **decoratedKwArgs)
            return innerWrap
        return wrap

    @decorator("decoratorArg1", "decoratorArg2", decoratorKwArg="decoratorKwValue")
    def testFunc(funcArg1, funcArg2, funcKwArg='funcKwArg'):
        debug(funcArg1)
        debug(funcArg2)
        debug(funcKwArg)

    testFunc("calledArg1", 'calledArg2', funcKwArg='calledKwArg')

#* Confidence Testing
if False:
    @confidence(29)
    def testFunc(funcArg1, funcArg2, funcKwArg='funcKwArg'):
        debug(funcArg1)
        debug(funcArg2)
        debug(funcKwArg)

    @confident(102)
    def testFunc2(funcArg1, funcArg2, funcKwArg='funcKwArg'):
        debug(funcArg1)
        debug(funcArg2)
        debug(funcKwArg)

    @confident(16)
    def testFunc3(funcArg1, funcArg2, funcKwArg='funcKwArg'):
        debug(funcArg1)
        debug(funcArg2)
        debug(funcKwArg)

    @confidence('super')
    def testFunc4(): pass

    @confidence('not very')
    def testFunc5(): pass

    @confidence('none')
    def testFunc6(): pass

    @confidence('low')
    def testFunc7(): pass

    @confidence('Sorta')
    def testFunc8(): pass

    @confidence('asfgs')
    def testFunc9(): pass

    try:
        testFunc2("calledArg1", 'calledArg2', funcKwArg='calledKwArg')
    except TypeError:
        print('testFunc2 worked')

    testFunc( "calledArg1", 'calledArg2', funcKwArg='calledKwArg')
    testFunc3("calledArg1", 'calledArg2', funcKwArg='calledKwArg')
    testFunc4()
    testFunc5()
    testFunc6()
    testFunc7()
    testFunc8()
    try:
        testFunc9()
    except TypeError:
        print('testFunc9 worked')

#* Key testing
if False:
    # print(Key.one)
    print(Key('one'))
    print(Key('exclamation'))
    print(Key('exclamationmark'))
    print(Key('exclamationPoint'))

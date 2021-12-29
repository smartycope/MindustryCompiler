from enum import Enum, auto
from EasyRegex import *
import re
import argparse
import clipboard
from Cope import *
_print = print
_set = set
_range = range
_type = type
from namespace import *
from customNamespace import *

description = 'A compiler that compiles a functional programming language into mindustry instructions'

parser = argparse.ArgumentParser(description=description)
parser.add_argument('inputFile',  help='The program file')
parser.add_argument('-o', '--outfile', help='Output to a file instead of printing and copying', nargs=1, default=None)
args = parser.parse_args()

outfile = args.outfile
infile  = args.inputFile

with open(infile, 'r') as f:
    inputProgram = f.read()

keywords = ("while", "if", "else")


erEquals = group(word()) + ifNotPrecededBy('if') + optional(whitespace()) + match('=') + ifNotFollowedBy('=') + optional(whitespace()) + namedGroup('val', chunk())
inputProgram = re.sub(erEquals.str(), 'set(' + replaceGroup('1').str() + ', ' + replaceNamedGroup('val').str() + ')', inputProgram)

# Replace and with _and
inputProgram = re.sub(' and ', ' _and ', inputProgram)
# inputProgram = re.sub('True', 'true', inputProgram)

program = inputProgram.strip().splitlines()

def searchForClosingBrace(startingLine) -> "distance":
    for cnt, i in enumerate(program[startingLine:]):
        if i.strip() == '}':
            return cnt
    raise SyntaxError(f'No closing brace found matching the opening brace on line {startingLine + 1}')

# Replace keywords
for lineno, line in enumerate(program):
    line = line.strip()

    # Remove all extrenous whitespace
    program[lineno] = line

    # First take out the comments
    if line.startswith('#'):
        program[lineno] = ''
        continue

    foundKeyword = re.match(matchMax(anyOf(*keywords)).str(), line)
    if foundKeyword:
        keyword = foundKeyword.group().strip()
    else:
        continue

    if keyword == 'while':
        erCondition = match('while') + optional(whiteChunk()) + '\(' + group(chunk()) + '\)' + optional(whiteChunk()) + '{'
        condition = re.search(erCondition.str(), line).groups()[1]
        if not condition:
            raise SyntaxError(f"Missing '{{' at the end of line {lineno + 1}")
        else:
            closing = searchForClosingBrace(lineno)
            program[lineno] = f"jump({closing}, 'true')"
            program[closing + lineno] = f"jump({-(closing - 1)}, '{condition}')"

    if keyword == 'if':
        erCondition = match('if (') + group(chunk()) + '\){'
        condition = re.search(erCondition.str(), line)
        if not condition:
            raise SyntaxError(f"Missing '{{' at the end of line {lineno + 1}")
        else:
            closing = searchForClosingBrace(lineno)
            program[lineno] = f"jump(2, '{condition.groups()[0]}')"
            program.insert(lineno + 1, f'jump({closing}, true)')
            program[closing + lineno + 1] = ''

    if keyword == 'else':
        raise SyntaxError(f"Error: else statement at line {lineno + 1}. else statements are currently unimplemented.")


# Go through and run each line as python code, with a couple of additions
outputProgram = ''
_locals = locals()
code = ''
for i in program:
    if i == '':
        continue
    try:
        try:
            line = 'outputProgram = outputProgram + ' + i + ' + "\\n"'
            exec(line, globals(), _locals)
        #* This is SO hacky, but I LOVE it.
        except NameError as err:
            erParseError = match("'") + group(word()) + match("'")
            foundName = re.search(erParseError.str(), str(err))
            if foundName:
                var = foundName.groups()[0]
                varLine = f'{var} = "{var}"; '
                exec(varLine + line, globals(), _locals)
            else:
                raise err
    except Exception as err:
        raise SyntaxError(f'Error on line {lineno + 1}: {err}\n"{i}" -> "{line}"')

# Fix the jump statement indexes
program = outputProgram.strip().splitlines()
for lineno, line in enumerate(program):
    if 'jump' not in line:
        continue
    erJump = group(optional(whiteChunk())) + 'jump ' + group(optional('-') + number())
    found = re.search(erJump.str(), line)
    if found:
        whitespace = found.groups()[0]
        index      = found.groups()[2]
    else:
        raise SyntaxError(f"Can't find a number in {line}")
    program[lineno] = re.subn(erJump.str(), f'{whitespace}jump {int(index) + lineno}', line, 1)[0]


out = '\n'.join(program)
if outfile:
    with open(outfile, 'w') as f:
        f.write(out)
else:
    _print(out)
    clipboard.copy(out)

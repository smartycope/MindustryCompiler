# Easy Mindustry Code

A compiler and vscode language extension that compiles a simple functional programming language into Mindustry instructions.

## Features

In the game Mindustry (https://github.com/Anuken/Mindustry) there are various processors that use a kind of dynamically typed assembly language to control various buildings and units. The syntax for it is not bad, but after a while it rapidly becomes a giant spaghetti code mess of gotos and end statements. So I wrote a simple compiler that implements if statements, else statements (eventually), while loops, comments, functions (kind of) and a couple other things, as well as generally being able to use a text editor. In addition, I wrote a simple VSCode/VSCodium language extension to provide syntax highlighting and a snippets file for auto-completion (I'm new to writing VSCode extensions and I don't know Javascript, so if someone wants to publish it or something for me go for it and let me know).

## Requirements

I use Cope.py and EasyRegex.py from my own boilerplate repo, but the files provided work.
* To install the extension, just copy the extension folder into the `<user home>/.vscode/extensions` folder and restart Code.

## Known Issues

* The else keyword isn't implemented yet
* I would love to implement for loops eventually
* Adding more inline variable things (like var = add(2, 3) instead of add(var, 2, 3)) would be nice, except that regex sounds hard.

### 1.0.0

Initial release

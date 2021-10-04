# ast2code
a simple program to convert the python AST to source code

# How to use

```python
from ast import parse
from ast2code import *#imports build_value,build_stmt,build_stmts,build_program,reformat
expr = input("Enter an expression:")
print("Built:",build_value(parse(expr)))#expression only
stmt = input("Enter a statement:")
print("Built:",build_stmt(parse(stmt)))#1 statement;EXPRESSION ALSO WORKS
stmts = []
while True:
    try:
        stmt.append(parse(input()))
    except KeyboardInterrupt:
        break
print("Built:",build_stmts(stmts))##A list works
filename = input("Filename:")
print(build_program(parse(open(filename).read())))#ast.Module objects work with build_program

print(reformat(stmt))#Automatically parses and builds;works for full programs/expressions/statements
```
# Installing to your standard library
If you like it and wants to do ```import ast2code``` anywhere without putting the ast2code.py file in the CWD,you can install it.

WARNING:You must manually locate and delete the file to uninstall it.You can specify the install dir.

WARNING:Won't work on other people's computer unless they did the same.

Run pkginst.pyw and install normally.(Custom installer powered by ```tkinter```)
# Reporting bugs
If you get a ```NotImplementedError``` or you have an error installing,post the error msg in a bug report.

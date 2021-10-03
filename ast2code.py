import os,sys
from sys import stdout,stderr
from ast import *
from collections import deque
class Elif(If):
    def __init__(self,thenode):
        self._node = thenode
    def __getattr__(self,attr):
        return getattr(self._node,attr)
def unimpl(*a,**k):
    raise NotImplementedError(*a,**k)
issubinstance = isinstance
def isinstance(x,y):#no subclasses allowed
    if type(y)!=tuple:
        y = (y,)
    return type(x) in y
def unquote(x):
    if len(x)>1 and (x[0] in "'\"") and (x[-1] in "'\""):
        return x[1:-1]
    return x
def commaify(lis,trailsingle=False):
    code = ",".join(map(build_value,lis))
    if trailsingle and len(lis)==1:
        code += ","
    return code
def strp(x):
    if x is None:
        return ""
    return str(x)
def strop(op):
    if isinstance(op,(Add,UAdd)):
        return "+"
    elif isinstance(op,(Sub,USub)):
        return "-"
    elif isinstance(op,FloorDiv):
        return "//"
    elif isinstance(op,Div):
        return "/"
    elif isinstance(op,Mult):
        return "*"
    elif isinstance(op,Pow):
        return "**"
    elif isinstance(op,Mod):
        return "%"
    elif isinstance(op,BitXor):
        return "^"
    elif isinstance(op,BitAnd):
        return "&"
    elif isinstance(op,BitOr):
        return "|"
    elif isinstance(op,MatMult):
        return "@"
    elif isinstance(op,Or):
        return " or "#note the spaces
    elif isinstance(op,And):
        return " and "
    elif isinstance(op,Not):
        return "not "
    elif isinstance(op,In):
        return " in "
    elif isinstance(op,NotIn):
        return " not in "
    elif isinstance(op,Is):
        return " is "
    elif isinstance(op,IsNot):
        return " is not "
    elif isinstance(op,Eq):
        return "=="
    elif isinstance(op,NotEq):
        return "!="
    elif isinstance(op,Gt):
        return ">"
    elif isinstance(op,GtE):
        return ">="
    elif isinstance(op,Lt):
        return "<"
    elif isinstance(op,LtE):
        return "<="
    unimpl("StrOp",op)
def lmap(func,*iterables):
    return list(map(func,*iterables))
def of(node):
    if isinstance(node,(List,ListComp)):
        return "["
    elif isinstance(node,(Tuple,GeneratorExp)):
        return "("
    unimpl("BracketL",type(node))
def ofe(node):
    if isinstance(node,(List,ListComp)):
        return "]"
    elif isinstance(node,(Tuple,GeneratorExp)):
        return ")"
    unimpl("BracketR",type(node))
def reprmod(x):#Uses double quotes as string delim.
    orig = repr(x)
    if orig.startswith("'") and orig.endswith("'"):
        orig = "\""+orig[1:-1].replace("\"","\\\"").replace("\\'","'")+"\""
    return orig
def build_value(node):
    if node is None:
        return None
    elif not issubinstance(node,AST):
        return node
    elif isinstance(node,Expr):
        return build_value(node.value)
    elif isinstance(node,keyword):
        if node.arg is None:
            return "**"+build_value(node.value)
        return node.arg+"="+build_value(node.value)
    elif isinstance(node,arg):
        return node.arg+((":"+build_value(node.annotation)) if node.annotation else "")
    elif isinstance(node,alias):
        code = node.name
        if node.asname is not None:
            code += " as "+node.asname
        return code
    elif isinstance(node,Compare):
        l = [node.left]+node.comparators
        code = ""
        for i in range(len(l)-1):
            code += build_value(l[i])+strop(node.ops[i])
        code += build_value(l[-1])
        return code
    elif isinstance(node,BinOp):
        return "("+build_value(node.left)+strop(node.op)+build_value(node.right)+")"
    elif isinstance(node,BoolOp):
        return "("+strop(node.op).join(map(build_value,node.values))+")"
    elif isinstance(node,UnaryOp):
        return strop(node.op)+build_value(node.operand)
    elif isinstance(node,Starred):
        return "*"+build_value(node.value)
    elif isinstance(node,Subscript):
        code = build_value(node.value)+"["
        ind = node.slice
        if isinstance(ind,Index):
            code += build_value(ind.value)
        else:
            assert isinstance(ind,Slice)
            lwr = strp(build_value(ind.lower))
            upr = strp(build_value(ind.upper))
            stp = strp(build_value(ind.step))
            if stp:
                stp = ":"+stp
            code += lwr+":"+upr+stp
        code += "]"
        return code
    elif isinstance(node,Constant):#repr should work(as stated in its docs)
        return reprmod(node.value)
    elif isinstance(node,Name):
        return node.id
    elif isinstance(node,comprehension):
        code = "for "+build_value(node.target)+" in "+build_value(node.iter)
        for condition in node.ifs:
            code += " if "+build_value(condition)
        return code
    elif isinstance(node,(ListComp,GeneratorExp)):
        code = of(node)+build_value(node.elt)
        fors = []
        for i,cond in enumerate(node.generators):
            fors.append(" "*(1+(len(code)*int(i>0)))+build_value(cond))
        code += "\n".join(fors)+ofe(node)
        return code
    elif isinstance(node,Attribute):
        return build_value(node.value)+"."+node.attr
    elif isinstance(node,(List,Tuple)):#note list is NOT the same as List
        return of(node)+commaify(node.elts,isinstance(node,Tuple))+ofe(node)
    elif isinstance(node,IfExp):
        return "("+(build_value(node.body)+" if "+build_value(node.test)+
                " else "+build_value(node.orelse))+")"
    elif isinstance(node,Call):
        code = build_value(node.func)
        args = commaify(node.args)
        if node.keywords:
            kws = commaify(node.keywords)
            if args:
                kws = ","+kws
            args += kws
        return code+"("+args+")"
    elif isinstance(node,JoinedStr):
        return "f"+"\""+"".join(map(unquote,map(build_value,node.values)))+"\""
    elif isinstance(node,FormattedValue):
        code = "{"+build_value(node.value)+"}"
        if node.format_spec is not None:
            code += ":"+build_value(node.format_spec)
        return code
    elif isinstance(node,Lambda):
        code = "lambda"
        vararg = "*"
        if node.args.vararg:
            vararg += node.args.vararg.arg
        varargs = [vararg] if (node.args.kwonlyargs or node.args.vararg) else []
        arglist = lmap(list,backzip(insif(lmap(build_value,node.args.posonlyargs),"/")+
                                    lmap(build_value,node.args.args)+
                                    varargs+
                                    lmap(build_value,node.args.kwonlyargs)+
                                    keep([kinsp(build_value(node.args.kwarg),"**")]),
                                    node.args.defaults+node.args.kw_defaults))
        for i,(argname,default) in enumerate(arglist):
            if default is not None:
                arglist[i][0] = argname+"="+build_value(default)
        pparglist = [argn for argn,trash in arglist]
        argstr = commaify(pparglist)+":"+build_value(node.body)
        if argstr:
            code += " "+argstr
        return code.strip()
    print(f"unimplemented:{dump(node)}",file=stderr)
    print(dump(node),node.lineno,node.col_offset)
    raise
    return f"(unimplemented:{dump(node)})"
def insif(x,y):
    if x:
        return x+[y,]
    return x
def keep(x):
    return list(filter(bool,x))
def kinsp(x,y):
    if x is not None:
        return y+x
    return x
def backzip(x,y):
    x = list(x)
    y = deque(y)
    while len(y)<len(x):
        y.appendleft(None)
    return zip(x,y)
def indented(x,spaces):
    return "\n".join((" "*spaces+i) for i in x.splitlines())
def _build_stmt(node,indent=0):
    if isinstance(node,Assign):
        code = commaify(node.targets)
        code += " = "
        code += build_value(node.value)
        return code
    elif isinstance(node,AugAssign):
        code = build_value(node.target)
        code += " "+strop(node.op)+"= "
        code += build_value(node.value)
        return code
    elif isinstance(node,(If,Elif)):
        cond = node.test
        code = ("if " if isinstance(node,If) else "elif ")+build_value(cond)+":\n"
        code += build_stmts(node.body,4)
        if node.orelse:
            orelse = list(node.orelse)
            elseif = isinstance(orelse[0],If)
            if elseif:
                orelse[0] = Elif(orelse[0])
            code += ("\n" if elseif else "\nelse:\n")
            code += build_stmts(orelse,(0 if elseif else 4))
        return code
    elif isinstance(node,For):
        code = "for "+build_value(node.target)+" in "+build_value(node.iter)+":\n"
        code += build_stmts(node.body,4)
        if node.orelse:
            code += "\nelse:\n"
            code += build_stmts(node.orelse,4)
        return code
    elif isinstance(node,While):
        code = "while "+build_value(node.test)+":\n"
        code += build_stmts(node.body,4)
        if node.orelse:
            code += "\nelse:\n"
            code += build_stmts(node.orelse,4)
        return code
    elif isinstance(node,Try):
        code = "try:\n"
        code += build_stmts(node.body,4)
        for hdlr in node.handlers:
            code += "\nexcept"
            if hdlr.type is not None:
                code += " "+build_value(hdlr.type)
                if hdlr.name is not None:
                    code += " as "+build_value(hdlr.name)
            code += ":\n"
            code += build_stmts(hdlr.body,4)
        if node.orelse:
            code += "\nelse:\n"
            code += build_stmts(node.orelse,4)
        if node.finalbody:
            code += "\nfinally:\n"
            code += build_stmts(node.finalbody,4)
        return code
    elif isinstance(node,Import):
        return "import "+commaify(node.names)
    elif isinstance(node,ImportFrom):
        return "from "+node.module+" import "+commaify(node.names)
    elif isinstance(node,Pass):
        return "pass"
    elif isinstance(node,Break):
        return "break"
    elif isinstance(node,Continue):
        return "continue"
    elif isinstance(node,FunctionDef):
        code = ""
        for dec in node.decorator_list:
            code += "@"+build_value(dec)+"\n"
        code += "def "+node.name+"("
        vararg = "*"
        if node.args.vararg:
            vararg += node.args.vararg.arg
        varargs = [vararg] if (node.args.kwonlyargs or node.args.vararg) else []
        arglist = lmap(list,backzip(insif(lmap(build_value,node.args.posonlyargs),"/")+
                                    lmap(build_value,node.args.args)+
                                    varargs+
                                    lmap(build_value,node.args.kwonlyargs)+
                                    keep([kinsp(build_value(node.args.kwarg),"**")]),
                                    node.args.defaults+node.args.kw_defaults))
        for i,(argname,default) in enumerate(arglist):
            arglist[i][1] = build_value(default)
        for i,(argname,default) in enumerate(arglist):
            if default is not None:
                arglist[i][0] = argname+"="+default
        pparglist = [argn for argn,trash in arglist]
        code += commaify(pparglist)+"):\n"#NOT EMOJI ):
        for stmt in node.body:
            code += build_stmt(stmt,4)+"\n"
        return code.strip()
    elif isinstance(node,ClassDef):
        code = "class "+node.name
        if node.bases:
            code += "("+commaify(node.bases)+")"
        code += ":\n"
        code += build_stmts(node.body,4)
        return code
    elif isinstance(node,Return):
        return "return "+build_value(node.value)
    elif isinstance(node,Raise):
        code = "raise"
        if node.exc is not None:
            code += " "+build_value(node.exc)
        if node.cause is not None:
            code += " from "+build_value(node.cause)
        return code
    elif isinstance(node,Assert):
        code = "assert "+build_value(node.test)
        if node.msg is not None:
            code += ","+node.msg
        return code
    return build_value(node)
def build_stmt(node,indent=0):
    """\
Builds a single statement from an AST node."""
    return indented(_build_stmt(node,indent),indent)
def build_stmts(stmts,indent=0):
    program = ""
    for instruction in stmts:
        program += build_stmt(instruction)+"\n"
    program = program.strip()
    return indented(program,indent)
def build_program(node):
    if isinstance(node,Module):
        return build_stmts(node.body)
    return build_stmt(node)
def dump_ast(code):
    print(dump(parse(code)))
def reformat(code):
    return build_program(parse(code))
def reformat_file(name,contrast=False,to=stdout,runfc=False,close=None):
    file = open(name)
    stringto = to
    if to and isinstance(to,str):
        to = open(to,"w")
    else:
        stringto = None
    if contrast:
        print("="*7+"ORIGINAL"+"="*7,file=to)
        print(file.read(),file=to)
        print("="*7+"REBUILT"+"="*7,file=to)
        file.seek(0)
    print(reformat(file.read()),file=to)
    if close is None:
        close = (to not in (stdout,stderr))
    if close:
        to.close()
    if runfc and stringto:
        print(os.popen(f"fc {name} {stringto}").read())
DEBUGGING = False
reformat_file("ast2code.py",to="a2c.rb.py",runfc=True)
while DEBUGGING:
    try:
        code = input()
    except KeyboardInterrupt:
        break
    else:
        try:
            print(reformat(code))
        except NotImplementedError:
            print(NotImplemented)

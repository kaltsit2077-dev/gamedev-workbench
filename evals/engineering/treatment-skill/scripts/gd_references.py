"""Finite constant folding for one-line GDScript resource arguments; never eval()."""
import ast
import re

def constant_value(expression,values,shadowed=()):
    if len(expression)>2048: raise ValueError('expression limit')
    tree=ast.parse(expression,mode='eval')
    if len(list(ast.walk(tree)))>60: raise ValueError('node limit')
    def visit(node):
        if isinstance(node,ast.Constant) and type(node.value) in {str,int,float}: result=node.value
        elif isinstance(node,ast.Name) and node.id not in shadowed and node.id in values: result=values[node.id]
        elif isinstance(node,(ast.Tuple,ast.List)): result=tuple(visit(x) for x in node.elts)
        elif isinstance(node,ast.BinOp) and isinstance(node.op,ast.Add):
            left,right=visit(node.left),visit(node.right)
            if not isinstance(left,str) or not isinstance(right,str): raise ValueError('only string addition')
            result=left+right
        elif isinstance(node,ast.BinOp) and isinstance(node.op,ast.Mod):
            left,right=visit(node.left),visit(node.right)
            if not isinstance(left,str) or re.search(r'%(?!%|s|d)',left): raise ValueError('only simple placeholders')
            result=left%right
        else: raise ValueError('runtime or unsupported expression')
        if isinstance(result,str) and len(result)>8192: raise ValueError('string limit')
        return result
    return visit(tree.body)

def bindings(lines):
    values={}; scopes={}; method='<initialization>'; parameters_open=False
    for number,code,literals,raw in lines:
        function=re.match(r'^(?:static\s+)?func\s+(\w+)\s*\(',code)
        if function:
            method=function[1]; scopes.setdefault(method,set())
            parameters_open=True; parameter_text=code[function.end():]
        else: parameter_text=code
        if parameters_open:
            scopes[method].update(re.findall(r'(?:^|,)\s*(\w+)\s*(?=[:,=]|$)',parameter_text.split(')',1)[0]))
            if ')' in parameter_text: parameters_open=False
        if method!='<initialization>':
            scopes.setdefault(method,set()).update(re.findall(r'\b(?:var|const|for)\s+(\w+)',code))
            for nested in re.finditer(r'\bfunc\s*\(([^)]*)\)',code):
                scopes[method].update(re.findall(r'(?:^|,)\s*(\w+)\s*(?=[:,=]|$)',nested[1]))
        declaration=re.match(r'^const\s+(\w+)(?:\s*:\s*\w+)?\s*(?::=|=)',code)
        if declaration:
            comment=next((i for i,char in enumerate(raw) if char=='#' and not any(first<=i<last for first,last,value in literals)),len(raw))
            try: values[declaration[1]]=constant_value(raw[declaration.end():comment].strip(),values)
            except (ValueError,SyntaxError,TypeError,KeyError,OverflowError): pass
    return values,scopes

def calls(code,raw):
    for found in re.finditer(r'(?<![\w.])(?:ResourceLoader\.)?(preload|load)\s*\(',code):
        start=found.end(); depth=1; end=start
        while end<len(code) and depth:
            if code[end]=='(': depth+=1
            elif code[end]==')': depth-=1
            end+=1
        if depth: yield found[1],start,len(raw),None; continue
        # The optional type/cache arguments do not form part of the path expression.
        stop=end-1; nested=0
        for i in range(start,stop):
            if code[i] in '([{': nested+=1
            elif code[i] in ')]}': nested-=1
            elif code[i]==',' and nested==0: stop=i; break
        yield found[1],start,end,raw[start:stop].strip()

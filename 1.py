import ast

source1 = '''
x = 7.5
y = x + x*5.5
def add1():
    x = x + 1
    add2(x)
def add2(y):
    y = y + 2
    add3(y)
    z = y * (5.5 >=2)
def add3(z):
    z = z + 3
add2(y)
add3(x)
'''

N = 0
# function_list = set()
func_name_list = []
func_node_list = []
var_list = set()

class OpTransformer(ast.NodeTransformer):
    def visit_Add(self, node):
        return ast.Sub()
    def visit_Sub(self, node):
        return ast.Add()
    def visit_Mult(self, node):
        return ast.Div()
    def visit_Div(self, node):
        return ast.Mult()
    
    def visit_GtE(self, node):
        return ast.Lt()
    def visit_Lt(self, node):
        return ast.GtE()
    def visit_LtE(self, node):
        return ast.Gt()
    def visit_Gt(self, node):
        return ast.LtE()
    
class FuncTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        global N
        if func_name_list[N][1]:
            # print(N)
            # print(node.name)
            N += 1
            return node
        N += 1

class VisitGlobalVar(ast.NodeVisitor):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        pass
    def visit_Assign(self, node: ast.Assign):
        var_list.add(node.targets[0].id)
        # print(node.targets[0].id)

class InvokedFuncVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # global N
        # N += 1
        func_node_list.append(node)
        func_name_list.append([node.name, False])
        
    def visit_Assign(self, node: ast.Assign):
        pass
        # print(node.targets[0].id)
    def call_recur(self, name:str):
        func_index = -1
        for i in range(len(func_name_list)):
            if func_name_list[len(func_name_list) - i - 1][0] == name:
                func_index = len(func_name_list) - i - 1
                func_name_list[func_index][1] = True
                break
    
        if func_index == -1:
            print("Error: Calling an undefined function!")
            return
        
        func_node = func_node_list[func_index]
        for comp in func_node.body: ### A list of assign and expr etc...
            if isinstance(comp, ast.Expr):
                self.call_recur(comp.value.func.id)

    def visit_Call(self, node):
        func_name = node.func.id
        self.call_recur(func_name)
        # function_list.add(node.func.id)

def append_global(string: str, var_set: set):
    for var in var_set:
        string = string + "\nprint(" + var + ")"
    return string 


if __name__ == "__main__":
    code = input()
    code = "\n".join(code.split("\\n"))
    source = code

    tree = ast.parse(source)
    # print(ast.dump(tree, indent=4))
    # print(ast.unparse(tree))
    visitor_var = VisitGlobalVar()
    visitor_var.visit(tree)
    # func_iter(tree)
    visitor_func = InvokedFuncVisitor()
    visitor_func.visit(tree)

    transformer = OpTransformer()
    transformer.visit(tree)

    # print(func_name_list)
    transformer2 = FuncTransformer()
    transformer2.visit(tree)

    s = ast.unparse(tree)
    print(append_global(s, var_list))
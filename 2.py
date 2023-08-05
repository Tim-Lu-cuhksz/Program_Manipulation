import ast

source1 = '''
x = y + 1
def foo2():
    y = x + 1
def func1(y=x+5):
    z = y*(5-2)
func1()
'''

NUM_OF_USES = 0
defined_var_list = set()
func_dict = dict()

class GlobalVarVisitor(ast.NodeVisitor):
    # Return true if the operation is well defined
    def set_flag_count(self, name: str, v_list:list, count, local_dict=dict(), arg_dict=dict()):
        if count == 1:
            global NUM_OF_USES
            if name not in v_list:
                NUM_OF_USES += 1
                return False
            return True
        elif count == 0:
            if name not in v_list:
                return False
            return True
        elif count == 2:
            return self.check_name(name, local_dict, arg_dict)
        elif count == 3:
            return self.check_name2(name, local_dict, arg_dict)
        elif count == 4:
            return False
        else:
            print("ERROR: Invalid count setting!")

    def compare_recur(self, value:ast.Compare, count = 1, local_dict=dict(), arg_dict=dict()):
        flag = True
        ### We omit constant here because it's always true
        if isinstance(value.left, ast.Name):
            if self.set_flag_count(value.left.id, defined_var_list, count, local_dict, arg_dict) is False:
                flag = False
        elif isinstance(value.left, ast.BinOp):
            if self.binary_recur(value.left, defined_var_list, count, local_dict, arg_dict) is False:
                flag = False
        elif isinstance(value.left, ast.UnaryOp):
            if self.unary_recur(value.left, count, local_dict, arg_dict) is False:
                flag = False
        elif isinstance(value.left, ast.Compare):
            if self.compare_recur(value.left, count, local_dict, arg_dict) is False:
                flag = False
        
        ### Check any undefined var in comparators
        for comp in value.comparators:
            if isinstance(comp, ast.Name):
                if self.set_flag_count(comp.id, defined_var_list, count, local_dict, arg_dict) is False:
                    flag = False
            elif isinstance(comp, ast.BinOp):
                if self.binary_recur(comp, defined_var_list, count, local_dict, arg_dict) is False:
                    flag = False
            elif isinstance(comp, ast.UnaryOp):
                if self.unary_recur(comp, count, local_dict, arg_dict) is False:
                    flag = False
            elif isinstance(comp, ast.Compare):
                if self.compare_recur(comp, count, local_dict, arg_dict) is False:
                    flag = False
        return flag

    ### Return True is defined
    ### count = 1 -> count undefined
    ### count = 0 -> does not count
    ### count = 2 -> count in call/recur
    ### count = 3 -> does not count
    ### count = 4 -> always False
    def unary_recur(self, value:ast.UnaryOp, count=1, local_dict=dict(), arg_dict=dict()):
        flag = False
        if isinstance(value.operand, ast.Name):
            if self.set_flag_count(value.operand.id, defined_var_list, count, local_dict, arg_dict) is False:
                flag = False
        elif isinstance(value.operand, ast.BinOp):
            if self.binary_recur(value.operand, defined_var_list, count, local_dict, arg_dict) is False:
                flag = False
        elif isinstance(value.operand, ast.Compare):
            if self.compare_recur(value.operand, count, local_dict, arg_dict) is False:
                flag = False
        elif isinstance(value.operand, ast.UnaryOp):
            if self.unary_recur(value.operand, count, local_dict, arg_dict) is False:
                flag = False
        return flag

    def binary_recur(self, value: ast.BinOp, var_list:list, count = 1, local_dict=dict(), arg_dict=dict()): ### Need local list here
        # global NUM_OF_USES
        flag = True
        if isinstance(value.left, ast.Name):
            ret = self.set_flag_count(value.left.id, var_list, count, local_dict, arg_dict)
            if ret is False:
                flag = False
        elif isinstance(value.left, ast.BinOp):
            ret = self.binary_recur(value.left, var_list, count, local_dict, arg_dict)
            if ret is False:
                flag = False
        elif isinstance(value.left, ast.UnaryOp):
            if self.unary_recur(value.left, count, local_dict, arg_dict) is False:
                flag = False
        elif isinstance(value.left, ast.Compare):
            if self.compare_recur(value.left, count, local_dict, arg_dict) is False:
                flag = False

        if isinstance(value.right, ast.Name):
            ret = self.set_flag_count(value.right.id, var_list, count, local_dict, arg_dict)
            if ret is False:
                flag = False
        elif isinstance(value.right, ast.BinOp):
            ret = self.binary_recur(value.right, var_list, count, local_dict, arg_dict)
            if ret is False:
                flag = False
        elif isinstance(value.right, ast.UnaryOp):
            if self.unary_recur(value.left, count, local_dict, arg_dict) is False:
                flag = False
        elif isinstance(value.right, ast.Compare):
            if self.compare_recur(value.left, count, local_dict, arg_dict) is False:
                flag = False

        return flag

    def get_func_arg(self, name: str):
        ret_dict = list()

        func_node = func_dict[name]
        args = func_node.args.args
        defaults = func_node.args.defaults
        # print(args)
        # print(defaults)
        if len(args) == len(defaults):
            for i in range(len(args)):
                if isinstance(defaults[i], ast.Constant):
                    ret_dict.append([args[i].arg, True])
                elif isinstance(defaults[i], ast.Name):
                    if self.set_flag_count(defaults[i].id, defined_var_list, 0):
                        ret_dict.append([args[i].arg, True])
                    else:
                        ret_dict.append([args[i].arg, False])
                elif isinstance(defaults[i], ast.UnaryOp):
                    if self.unary_recur(defaults[i], 0):
                        ret_dict.append([args[i].arg, True])
                    else:
                        ret_dict.append([args[i].arg, False])
                elif isinstance(defaults[i], ast.BinOp):
                    if self.binary_recur(defaults[i], defined_var_list, 0):
                        ret_dict.append([args[i].arg, True])
                    else:
                        ret_dict.append([args[i].arg, False])
                elif isinstance(defaults[i], ast.Compare):
                    if self.compare_recur(defaults[i], 0):
                        ret_dict.append([args[i].arg, True])
                    else:
                        ret_dict.append([args[i].arg, False])
                # ret_dict[args[i].arg] = True
        else:
            for i in range(len(args)):
                if i < len(args) - len(defaults):
                    ret_dict.append([args[i].arg, False])
                    # ret_dict[args[i].arg] = False
                else:
                    k = len(args) - len(defaults)
                    if isinstance(defaults[i-k], ast.Constant):
                        ret_dict.append([args[i].arg, True])
                    elif isinstance(defaults[i-k], ast.Name):
                        if self.set_flag_count(defaults[i-k].id, defined_var_list, 0):
                            ret_dict.append([args[i].arg, True])
                        else:
                            ret_dict.append([args[i].arg, False])
                    elif isinstance(defaults[i-k], ast.UnaryOp):
                        if self.unary_recur(defaults[i-k], 0):
                            ret_dict.append([args[i].arg, True])
                        else:
                            ret_dict.append([args[i].arg, False])
                    elif isinstance(defaults[i-k], ast.BinOp):
                        if self.binary_recur(defaults[i-k], defined_var_list, 0):
                            ret_dict.append([args[i].arg, True])
                        else:
                            ret_dict.append([args[i].arg, False])
                    elif isinstance(defaults[i-k], ast.Compare):
                        if self.compare_recur(defaults[i-k], 0):
                            ret_dict.append([args[i].arg, True])
                        else:
                            ret_dict.append([args[i].arg, False])
                    # ret_dict.append([args[i].arg, True])
        return ret_dict

    ## local_var is a combination of local + arg dict
    ### arg_list is a list of arguments, along with truth value for the invoked function
    def update_func_arg(self, arg_list: list, node: ast.Call, var_list: list, local_var = dict(), arg_dict = dict()):
        # arg_dict = dict()
        ### Error checking
        # if len(arg_list) != (len(node.args) + len(node.keywords)):
        #     print("ERROR: Something wrong occurs!!!")
        #     return
        for i in range(len(node.args)):
            if isinstance(node.args[i], ast.Constant):
                arg_list[i][1] = True
            elif isinstance(node.args[i], ast.Name):
                # print(local_var)
                # print(arg_dict)
                if self.check_name2(node.args[i].id, local_var, arg_dict): ## Or in local_var_list
                    arg_list[i][1] = True
                else:
                    arg_list[i][1] = False
            elif isinstance(node.args[i], ast.BinOp):
                arg_list[i][1] = self.binary_recur(node.args[i], var_list, 3) ### local list
            elif isinstance(node.args[i], ast.UnaryOp):
                arg_list[i][1] = self.unary_recur(node.args[i], 3, local_var, arg_dict)
            elif isinstance(node.args[i], ast.Compare): 
                ## Need to work on this
                arg_list[i][1] = self.compare_recur(node.args[i], 3, local_var, arg_dict)

        eval_key = []            
        for i in range(len(node.keywords)):
            arg = node.keywords[i].arg
            value = node.keywords[i].value
            if isinstance(value, ast.Constant):
                eval_key.append([arg, True])
            elif isinstance(value, ast.Name):
                if self.check_name2(value.id, local_var, arg_dict):
                # if value.id in var_list: ### Or local_var list condition
                    eval_key.append([arg, True])
                else:
                    eval_key.append([arg, False])
            elif isinstance(value, ast.BinOp):
                if self.binary_recur(value, var_list, 3, local_var, arg_dict):
                    eval_key.append([arg, True])
                else:
                    eval_key.append([arg, False])
            elif isinstance(value, ast.UnaryOp):
                if self.unary_recur(value, 3, local_var, arg_dict):
                    eval_key.append([arg, True])
                else:
                    eval_key.append([arg, False])
            elif isinstance(value, ast.Compare):
                ### Need to work on this later
                if self.compare_recur(value, 3, local_var, arg_dict):
                    eval_key.append([arg, True])
                else:
                    eval_key.append([arg, False])

        for key in eval_key:
            for j in range(len(arg_list)):
                if key[0] == arg_list[j][0]:
                    arg_list[j][1] = key[1]

    def arg_list_to_dict(self, l: list):
        dic = dict()
        for i in l:
            dic[i[0]] = i[1]
        return dic

    ### Return true if the name is defined, otherwise return false
    ### Count the NUM_OF_USES
    def check_name(self, name_node:str, local_dict:dict, arg_dict:dict):
        global NUM_OF_USES
        # res = None
        if name_node in local_dict:
            if local_dict[name_node] is True:
                return True
            else:
                NUM_OF_USES += 1
                return False
        elif name_node in arg_dict:
            if arg_dict[name_node] is True:
                return True
            else:
                NUM_OF_USES += 1
                return False
        elif name_node in defined_var_list:
            return True
        else:
            NUM_OF_USES += 1
            return False
        
    ### Do not count in this case
    def check_name2(self, name_node:str, local_dict:dict, arg_dict:dict):
        # print(name_node)
        if name_node in local_dict:
            if local_dict[name_node] is True:
                return True
            else:
                return False
        elif name_node in arg_dict:
            if arg_dict[name_node] is True:
                return True
            else:
                return False
        elif name_node in defined_var_list:
            return True
        else:
            return False

    def call_recur(self, call_node: ast.Call, arg_dict: dict, depth = 0):
        if depth > 1e5:
            print("Warning: deep recursive tree! Consider reconfiguring the depth!")
            return
        global NUM_OF_USES
        local_var_dict = dict()
        func_node = func_dict[call_node.func.id]
        body = func_node.body

        for comp in body:
            if isinstance(comp, ast.Assign):
                if isinstance(comp.value, ast.Constant):
                    local_var_dict[comp.targets[0].id] = True
                elif isinstance(comp.value, ast.Name):
                    if self.check_name(comp.value.id, local_var_dict, arg_dict):
                        local_var_dict[comp.targets[0].id] = True
                    else:
                        local_var_dict[comp.targets[0].id] = False
                elif isinstance(comp.value, ast.BinOp):
                    if self.binary_recur(comp.value, defined_var_list, 2, local_var_dict, arg_dict):
                        local_var_dict[comp.targets[0].id] = True
                    else:
                        local_var_dict[comp.targets[0].id] = False
                elif isinstance(comp.value, ast.UnaryOp):
                    if self.unary_recur(comp.value, 2, local_var_dict, arg_dict):
                        local_var_dict[comp.targets[0].id] = True
                    else:
                        local_var_dict[comp.targets[0].id] = False
                elif isinstance(comp.value, ast.Compare):
                    if self.compare_recur(comp.value, 2, local_var_dict, arg_dict):
                        local_var_dict[comp.targets[0].id] = True
                    else:
                        local_var_dict[comp.targets[0].id] = True
            
            elif isinstance(comp, ast.Expr):
                func_id = comp.value.func.id
                arg_list = self.get_func_arg(func_id)
                # print(local_var_dict)
                self.update_func_arg(arg_list, comp.value, defined_var_list, local_var_dict, arg_dict)
                # print(arg_list)
                self.call_recur(comp.value, self.arg_list_to_dict(arg_list), depth + 1)

    def visit_Assign(self, node: ast.Assign):
        global NUM_OF_USES
        # print(node.targets[0].id)
        ### If a variable is assigned with a constant, it is defined
        if isinstance(node.value, ast.Constant):
            defined_var_list.add(node.targets[0].id)
            # print(node.value.value)
        ### If a variable is assigned with another variable, it's defined only if the var is defined
        elif isinstance(node.value, ast.Name):
            if node.value.id in defined_var_list:
                defined_var_list.add(node.targets[0].id)
            else:
                if node.targets[0].id in defined_var_list:
                    defined_var_list.remove(node.targets[0].id)
                NUM_OF_USES += 1
            # print(node.value.id)
        elif isinstance(node.value, ast.UnaryOp):
            if self.unary_recur(node.value):
                defined_var_list.add(node.targets[0].id)
            else:
                if node.targets[0].id in defined_var_list:
                    defined_var_list.remove(node.targets[0].id)
                
        elif isinstance(node.value, ast.BinOp):
            ret = self.binary_recur(node.value, defined_var_list)
            if ret is True:
                defined_var_list.add(node.targets[0].id)
            else:
                if node.targets[0].id in defined_var_list:
                    defined_var_list.remove(node.targets[0].id)
        elif isinstance(node.value, ast.Compare):
            ### Need to work on this
            if self.compare_recur(node.value):
                defined_var_list.add(node.targets[0].id)
            else:
                if node.targets[0].id in defined_var_list:
                    defined_var_list.remove(node.targets[0].id)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        func_dict[node.name] = node
        # if node.args.defaults:
        #     print(node.args.defaults[0].value)
            
    def visit_Call(self, node: ast.Call):
        arg_list = self.get_func_arg(node.func.id)
        self.update_func_arg(arg_list, node, defined_var_list)
        arg_d = self.arg_list_to_dict(arg_list)
        # print(arg_d)
        self.call_recur(node, arg_d)


if __name__ == "__main__":
    code = input()
    code = "\n".join(code.split("\\n"))
    source = code
    tree = ast.parse(source)
    # print(ast.dump(tree, indent=4))
    ### Step drop unused function?

    global_var_v = GlobalVarVisitor()
    global_var_v.visit(tree)
    print(NUM_OF_USES)

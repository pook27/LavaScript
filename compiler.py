import itertools
from assembler import assemble
import re

class Compiler:
    def __init__(self):
        self.vars_map = {}
        self.next_ram = 16
        self.asm = []
        self.label_count = itertools.count()

    def get_var_addr(self, var):
        if var not in self.vars_map:
            self.vars_map[var] = self.next_ram
            self.next_ram += 1
        return self.vars_map[var]

    def write(self, line):
        self.asm.append(line)

    def compile_assign(self,var,expr):
        addr = self.get_var_addr(var)
        if isinstance(expr,int):
            self.write(f"@{expr}")
            self.write("D=A")
        else:
            epxr_addr = self.get_var_addr(expr)
            self.write(f"@{epxr_addr}")
            self.write("D=M")
        self.write(f"@{addr}")
        self.write("M=D")

    def compile_math(self, dest, left, op, right):
        dest_addr = self.get_var_addr(dest)

        if isinstance(left,int):
            self.write(f"@{left}")
            self.write("D=A")
        else:
            left_addr = self.get_var_addr(left)
            self.write(f"@{left_addr}")
            self.write("D=M")

        if isinstance(right, int):
            if op == '+':
                self.write(f"@{right}")
                self.write("D=D+A")
            elif op == '-':
                self.write(f"@{right}")
                self.write("D=D-A")
            else:
                raise NotImplementedError(f"{op} with int not implemented")
        else:
            right_addr = self.get_var_addr(right)
            self.write(f"@{right_addr}")
            if op == '+':
                self.write("D=D+M")
            elif op == '-':
                self.write("D=D-M")
            else:
                raise NotImplementedError(f"{op} with var not implemented")

        self.write(f"@{dest_addr}")
        self.write("M=D")

    def compile_condition(self, left, op, right):
        if isinstance(left, int):
            self.write(f"@{left}")
            self.write("D=A")
        else:
            addr = self.get_var_addr(left)
            self.write(f"@{addr}")
            self.write("D=M")

        if isinstance(right, int):
            self.write(f"@{right}")
            self.write("D=D-A")
        else:
            addr = self.get_var_addr(right)
            self.write(f"@{addr}")
            self.write("D=D-M")

        jump_map = {">": "JLE", "<": "JGE", "==": "JNE", "!=": "JEQ", ">=": "JLT", "<=": "JGT"}
        return jump_map[op]

    def compile_while(self, condition_str, func):
        start_label = f"WHILE_START{next(self.label_count)}"
        end_label = f"WHILE_END{next(self.label_count)}"
        self.write(f"({start_label})")

        or_parts = [part.strip() for part in condition_str.split("or")]
        for or_part in or_parts:
            and_parts = [p.strip() for p in or_part.split("and")]
            for condition in and_parts:
                m = re.match(r"(\w+|\d+)\s*(==|!=|>=|<=|>|<)\s*(\w+|\d+)", condition)
                if not m:
                    raise SyntaxError(f"Unsupported condition: {condition}")
                left, op, right = m.groups()
                left = int(left) if left.isdigit() else left
                right = int(right) if right.isdigit() else right
                jump_instr = self.compile_condition(left, op, right)

                self.write(f"@{end_label}")
                self.write(f"D;{jump_instr}")
        func()
        self.write(f"@{start_label}")
        self.write("0;JMP")
        self.write(f"({end_label})")

    def get_code(self):
        return "\n".join(self.asm)

    def compile(self):
        return assemble(self.get_code()), self.vars_map

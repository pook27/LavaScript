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

        not_int = False
        if not isinstance(right,int):
            right = self.get_var_addr(right)
            not_int = True
        if op == '+':
            self.write(f"@{right}")
            self.write("D=D+M" if not_int else "D=D+A")
        elif op == '-':
            self.write(f"@{right}")
            self.write("D=D-M" if not_int else "D=D-A")
        elif op == '&':
            self.write(f"@{right}")
            self.write("D=D&M" if not_int else "D=D&A")
        elif op == '|':
            self.write(f"@{right}")
            self.write("D=D|M" if not_int else "D=D|A")
        elif op == "*":
            # Optimize: use minimum value as counter, Get counter and addend at compile time if both are constants
            if isinstance(left, int) and isinstance(right, int):
                counter, addend = (left, right) if left <= right else (right, left)
            else:
                # At least one is a variable - need runtime comparison
                counter, addend = None, None
            
            if counter is not None:
                # Compile-time optimization: we know min/max
                self.write(f"@{counter}")
                self.write("D=A")
                self.write("@R13")
                self.write("M=D")  # counter
                self.write("@0")
                self.write("D=A")
                self.write("@R14")
                self.write("M=D")  # result = 0
            else:
                # Runtime comparison: find min/max at runtime, D already has left
                self.write("@R13")
                self.write("M=D")  # R13 = left
                self.write(f"@{right}")
                self.write("D=M" if not_int else "D=A")
                self.write("@R15")
                self.write("M=D")  # R15 = right
                
                # Compare and swap if needed
                self.write("@R13")
                self.write("D=M")
                self.write("@R15")
                self.write("D=D-M")  # D = left - right
                skip_swap = f"MUL_SKIP{next(self.label_count)}"
                self.write(f"@{skip_swap}")
                self.write("D;JLE")  # if left <= right, no swap needed
                
                # Swap: R13 and R15
                self.write("@R13")
                self.write("D=M")
                self.write("@R14")
                self.write("M=D")  # temp = R13
                self.write("@R15")
                self.write("D=M")
                self.write("@R13")
                self.write("M=D")  # R13 = R15
                self.write("@R14")
                self.write("D=M")
                self.write("@R15")
                self.write("M=D")  # R15 = temp
                
                self.write(f"({skip_swap})") # Now R13 = min (counter), R15 = max (addend)
                self.write("@0")
                self.write("D=A")
                self.write("@R14")
                self.write("M=D")  # result = 0
            
            # Main multiplication loop
            loop = f"MUL_LOOP{next(self.label_count)}"
            end = f"MUL_END{next(self.label_count)}"
            self.write(f"({loop})")
            self.write("@R13")
            self.write("D=M")
            self.write(f"@{end}")
            self.write("D;JEQ")  # if counter == 0, end
            
            # Add addend to result
            if counter is not None:
                # Compile-time: load constant addend
                self.write(f"@{addend}")
                self.write("D=A")
            else:
                # Runtime: load from R15
                self.write("@R15")
                self.write("D=M")
            self.write("@R14")
            self.write("M=D+M")
            
            self.write("@R13")
            self.write("M=M-1")  # counter--
            self.write(f"@{loop}")
            self.write("0;JMP")
            
            self.write(f"({end})")
            self.write("@R14")
            self.write("D=M")
        elif op == "/":
            self.write("@R13")  # store dividend (left) into R13
            self.write("M=D")
            self.write("@0")
            self.write("D=A")
            self.write("@R14")  # quotient = 0
            self.write("M=D")
            loop = f"DIV_LOOP{next(self.label_count)}"
            end = f"DIV_END{next(self.label_count)}"
            self.write(f"({loop})")
            self.write("@R13")  # D = dividend
            self.write("D=M")
            self.write(f"@{right}")  # D = dividend - divisor
            self.write("D=D-M" if not_int else "D=D-A")
            self.write(f"@{end}")  # if dividend < divisor, end
            self.write("D;JLT")
            self.write("@R13")  # dividend = dividend - divisor
            self.write("M=D")
            self.write("@R14")  # quotient++
            self.write("M=M+1")
            self.write(f"@{loop}")  # repeat
            self.write("0;JMP")
            self.write(f"({end})")  # end label
            self.write("@R14")  # load quotient
            self.write("D=M")
        else:
            raise NotImplementedError(f"{op} with int not implemented")

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

    def compile_for(self, init_str, condition_str, increment_str, func):
        # Parse and emit initialization, Example: i = 0
        m_init = re.match(r"(\w+)\s*=\s*(.+)", init_str)
        if m_init:
            var, expr = m_init.groups()
            var = var.strip()
            expr = expr.strip()
            if expr.isdigit():
                self.compile_assign(var, int(expr))
            else:
                self.compile_assign(var, expr)
        else:
            raise SyntaxError(f"Unsupported for-loop init: {init_str}")
        start_label = f"FOR_START{next(self.label_count)}"
        end_label = f"FOR_END{next(self.label_count)}"
        self.write(f"({start_label})")

        # Condition
        m_cond = re.match(r"(\w+|\d+)\s*(==|!=|>=|<=|>|<)\s*(\w+|\d+)", condition_str)
        if not m_cond:
            raise SyntaxError(f"Unsupported for-loop condition: {condition_str}")
        left, op, right = m_cond.groups()
        left = int(left) if left.isdigit() else left
        right = int(right) if right.isdigit() else right
        jump_instr = self.compile_condition(left, op, right)
        self.write(f"@{end_label}")
        self.write(f"D;{jump_instr}")

        func() # Body
        # Increment, Example: i = i + 1
        m_incr = re.match(r"(\w+)\s*=\s*(\w+)\s*([\+\-\*/])\s*(\w+|\d+)", increment_str)
        if m_incr:
            var, left, op, right = m_incr.groups()
            var = var.strip()
            left = left.strip()
            op = op.strip()
            right = int(right) if right.isdigit() else right.strip()
            self.compile_math(var, left, op, right)
        else:
            raise SyntaxError(f"Unsupported for-loop increment: {increment_str}")

        # Jump back to start
        self.write(f"@{start_label}")
        self.write("0;JMP")
        self.write(f"({end_label})")

    def compile_if(self, condition_str, func):
        end_label = f"IF_END{next(self.label_count)}"
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
        self.write(f"({end_label})")

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

    def compile_print(self, value, mode="PRINT"):
        if isinstance(value, int):
            self.write(f"@{value}")
            self.write("D=A")
        else:
            if isinstance(value, str) and value.isdigit():
                self.write(f"@{int(value)}")
                self.write("D=A")
            else:
                addr = self.get_var_addr(value)
                self.write(f"@{addr}")
                self.write("D=M")
        self.write(f"{mode} D")

    def compile(self):
        return assemble("\n".join(self.asm))
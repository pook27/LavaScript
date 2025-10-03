import time
from alu import alu


MASK = (1 << 64) - 1  # updated mask for 64 bits

def int_to_bin(v):
    return format(v & MASK, f"064b")  # 64 bits

def bin_to_int(s):
    return int(s, 2)

def signed64(v):
    SIGN = 1 << (64 - 1)
    if v & SIGN:
        return v - (1 << 64)
    return v

def format_bytes(num_bytes):
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f}"

class CPU:
    def __init__(self, rom):
        self.A = "0" * 64
        self.D = "0" * 64
        self.pc = 0
        self.rom = rom
        self.ram = ["0" * 64 for _ in range(2**16)]

    def step(self):
        try:
            instr = self.rom[self.pc]
            if instr[0] == "0":
                self.A = instr[1:].zfill(64)  # 64 bits
                self.pc += 1
                return

            print_bits = instr[1:3]
            a_bit = instr[3]
            comp_bits = instr[4:10]   # six bits: zx,nx,zy,ny,f,no
            dest_bits = instr[10:13]  # A, D, M
            jump_bits = instr[13:16]

            x = self.D
            addrA = bin_to_int(self.A)
            y = self.ram[addrA] if a_bit == "1" else self.A

            # run ALU (zx,nx,zy,ny,f,no)
            zx, nx, zy, ny, f, no = [int(b) for b in comp_bits]
            out, zr, ng = alu(x, y, zx, nx, zy, ny, f, no)

            write_A = (dest_bits[0] == "1")
            write_D = (dest_bits[1] == "1")
            write_M = (dest_bits[2] == "1")

            if write_M:
                self.ram[addrA] = out
            if write_D:
                self.D = out
            if write_A:
                self.A = out

            # 64-bit output and jump logic
            d_value = bin_to_int(self.D)
            d_signed = signed64(d_value)
            if print_bits == "01":
                print(d_signed, end="")
            elif print_bits == "10":
                char_code = d_value & 0xFF
                print(chr(char_code), end="")

            do_jump = False
            if jump_bits == "001" and d_signed > 0:    # JGT
                do_jump = True
            elif jump_bits == "010" and d_signed == 0: # JEQ
                do_jump = True
            elif jump_bits == "011" and d_signed >= 0: # JGE
                do_jump = True
            elif jump_bits == "100" and d_signed < 0:  # JLT
                do_jump = True
            elif jump_bits == "101" and d_signed != 0: # JNE
                do_jump = True
            elif jump_bits == "110" and d_signed <= 0: # JLE
                do_jump = True
            elif jump_bits == "111" and True:          # JMP
                do_jump = True

            if do_jump:
                self.pc = bin_to_int(self.A)
            else:
                self.pc += 1
        except Exception as e:
            import sys
            print(f"Runtime Error at PC={self.pc}: {e}", file=sys.stderr)
            print(f"Instruction: {self.rom[self.pc]}", file=sys.stderr)
            raise

    def run(self, diagnostics = False):
        try:
            while self.pc < len(self.rom):
                self.step()
            print()
        except Exception as e:
            import sys
            print(f"CPU halted due to error: {e}", file=sys.stderr)

        # RAM diagnostics
        if diagnostics:
            used = [(i, v) for i, v in enumerate(self.ram) if v != "0" * 64]
            total = len(self.ram)
            used_count = len(used)
            unused_count = total - used_count
            percent_used = (used_count / total) * 100
            percent_unused = 100 - percent_used
            unused_bytes = (unused_count * 64) // 8  # 64 bits per address, convert to bytes
            unused_str = format_bytes(unused_bytes)
            print(f"RAM usage: {used_count} addresses written ({percent_used:.2f}% used).")
            print(f"Unused RAM: {unused_count} addresses, approx {unused_str} ({percent_unused:.2f}% unused).")

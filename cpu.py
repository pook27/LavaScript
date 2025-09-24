import time
from alu import alu

MASK = (1 << 16) - 1


def int_to_bin(v):
    return format(v & ((1 << 16) - 1), f"016b")

def bin_to_int(s):
    return int(s, 2)

def signed16(v):
    SIGN = 1 << (16 - 1)
    if v & SIGN:
        return v - (1 << 16)
    return v

class CPU:
    def __init__(self, rom):
        self.A = "0" * 16
        self.D = "0" * 16
        self.pc = 0
        self.rom = rom
        self.ram = ["0" * 16 for _ in range(65536)]

    def step(self):
        instr = self.rom[self.pc]
        if instr[0] == "0":
            self.A = instr[1:].zfill(16)
            self.pc += 1
            return

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

        d_unsigned = bin_to_int(self.D)
        d_signed = signed16(d_unsigned)

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
        elif jump_bits == "111":                   # JMP
            do_jump = True

        if do_jump:
            self.pc = bin_to_int(self.A)
        else:
            self.pc += 1

    def run_old(self, step_delay=0):
        while self.pc < len(self.rom):
            D_s = signed16(int(self.D,2))
            print(f"A={int(self.A,2)} D={D_s} M[A]={int(self.ram[int(self.A,2)],2)}")
            self.step()
            time.sleep(step_delay)
        print("DONE")

    def run(self, vars, time_delay=0):
        while self.pc < len(self.rom):
            if time_delay > 0:
                for key, value in vars.items():
                    print(f"{key}={int(self.ram[value],2)}", end=" ")
                print("\n")
                time.sleep(time_delay)
            self.step()
        for key, value in vars.items():
            print(f"{key} : {int(self.ram[value], 2)}")
        print("DONE")

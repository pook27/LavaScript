<h1 align="center">
  🌋 LavaScript 🌋
</h1>

<p align="center">
  <b>A toy programming language and compiler built on top of the 
  <a href="https://www.nand2tetris.org/">Hack Computer</a></b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-learning-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/language-Python-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-Do_Whatever_You_Want-green?style=for-the-badge" />
</p>

<p align="center">
  LavaScript translates <code>.ls</code> files into Hack assembly, 
  assembles them into binary, and runs them on a custom CPU emulator 
  that operates on top of the Hack ALU.  
</p>

<p align="center">
  Inspired by the legendary <a href="https://www.nand2tetris.org/">Nand2Tetris</a> course, 
  extended with ✨ new features ✨ such as assignments, conditions, loops, 
  character printing, and even a quirky <code>Maybe</code> random condition.
</p>

## ✨ Features

- 📝 Variables with automatic memory allocation  
- ➕ Arithmetic operators: `+`, `-`, `*`, `/`  
- 🔀 Logical operators: `&`, `|`  
- 🔎 Comparisons: `==`, `!=`, `>`, `<`, `>=`, `<=`  
- 🔁 Control flow:  
  - `while` loops (supports `True`, `False`, and `Maybe` for random branching)  
  - `if` conditionals  
  - `for (init; condition; increment)` loops  
- 🖨️ Printing:  
  - `print(x)` → print number  
  - `printc('A')` or `printc(x)` → print ASCII character  
- 🔡 Character literals automatically converted to ASCII codes  
- ⚙️ Compiler → Hack assembly  
- 🛠️ Assembler → machine code  
- 💻 CPU emulator executes the machine code with extended print opcodes:  
  - `01` → print number (decimal)  
  - `10` → print ASCII character  
  - `11` → no print (default, backward compatible)

## 🚀 Getting Started

Clone the repository, then run:

```bash
./melt examples/example.ls
to compile and execute a LavaScript program.
```
## Development
- Add new syntax → parser.py
- Implement new operations → compiler.py
- Update opcode translation → assembler.py
- Extend CPU behavior → cpu.py

## Roadmap
<p>Functions and subroutines</p> <p>Strings and arrays</p> <p>Additional operators (like % and logical not)</p> <p>File I/O</p>
License
This project is just for learning and fun. Do whatever you want.

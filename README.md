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
  extended with ✨ new features ✨ such as multiplication, division, conditions, loops, 
  and printing.
</p>


## ✨ Features

- 📝 Variables with automatic memory allocation  
- ➕ Arithmetic operators: `+`, `-`, `*`, `/`  
- 🔀 Logical operators: `&`, `|`  
- 🔎 Conditionals: `==`, `!=`, `>`, `<`, `>=`, `<=`  
- 🔁 Control flow: `while` loops with `and`/`or` conditions  
- ⚙️ Compiler → Hack assembly  
- 🛠️ Assembler → machine code  
- 💻 CPU emulator runs the machine code  
- 🖨️ Extended C-instruction format, for printing instructions:  
  - `01` → print number (decimal)  
  - `10` → print ASCII character  
  - `11` → no print (default, backward compatible)
    
## 🚀 Getting Started

clone the repository, and then
in bash terminal type `./melt example_file.ls` in order to run `example_file.ls`

#Development
  Add new syntax → `parser.py`
  Implement new operations → `compiler.py`
  Update opcode translation → `assembler.py`
  Extend CPU behavior → `cpu.py`

#Roadmap
 <p>Functions and subroutines</p>
 <p>Full string and array support</p>
 <p>for loops and if conditionals</p>
 <p>File I/O</p>

#License This project is just for learning and fun. Do whatever you want

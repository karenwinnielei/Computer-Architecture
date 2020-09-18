"""CPU functionality."""

import sys

SP = 7
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

# `FL` bits: `00000LGE`
L = 0b100
G = 0b010
E = 0b001

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.pc = 0
        self.ram = [0] * 256
        self.fl = 0
    
    def ram_read(self, MAR):
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        
        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()

                    if n == '':
                        continue
                    try:
                        n = int(n, 2)
                    except ValueError:
                        print(f"Invalid number '{n}'")
                        sys.exit(1)
                    self.ram[address] = n
                    address += 1
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL": 
            self.reg[reg_a] *= self.reg[reg_b] 
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = L
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = G
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = E
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def push_value(self, value):
        self.reg[SP] -= 1
        top_of_stack_addr = self.reg[SP]
        self.ram[top_of_stack_addr] = value

    def pop_value(self):
        top_of_stack_addr = self.reg[SP]
        operand_b = self.ram[top_of_stack_addr]
        self.reg[SP] += 1
        return operand_b
    
    def jump_value(self):
        operand_a = self.ram_read(self.pc + 1)
        jump = self.reg[operand_a]
        self.pc = jump

    def run(self):
        """Run the CPU."""
        self.reg[SP] = 0xF4

        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == HLT:
                self.running = False
            
            elif ir == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif ir == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            
            elif ir == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3

            elif ir == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            
            elif ir == PUSH:
                operand_b = self.reg[operand_a]
                self.push_value(operand_b)
                self.pc += 2
            
            elif ir == POP:
                operand_b = self.pop_value()
                self.reg[operand_a] = operand_b
                self.pc += 2
            
            elif ir == CALL:
                return_addr = self.pc + 2
                self.push_value(return_addr)
                operand_b = self.reg[operand_a]
                self.pc = operand_b

            elif ir == RET:
                return_addr = self.pop_value()
                self.pc = return_addr
            
            elif ir == CMP:
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3
            
            elif ir == JMP:
                self.jump_value()

            elif ir == JEQ:
                if self.fl == E:
                    self.jump_value()
                else:
                    self.pc += 2
            
            elif ir == JNE:
                if self.fl != E:
                    self.jump_value()
                else:
                    self.pc += 2

            else:
                print(f"Unknown instruction {ir}")
                sys.exit(3)

            


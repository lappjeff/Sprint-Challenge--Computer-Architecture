"""CPU functionality."""

import sys
ADD = 0b10100000
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101
AND = 0b10101000
OR = 0b10101010
NOT = 0b01101001
XOR = 0b10101011
MOD = 0b10100100
SHL = 0b10101100
SHR = 0b10101101


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * \
            0xFF  # Random Access MEMORY - has 0xFF hex, aka  256 bits - Each index should contain an instruction, like ADD or LDI along with whatever params it needs following it
        self.reg = [0] * 0x08  # registries - 8 registries
        self.pc = 0
        self.sp = 7
        self.reg[7] = 0xF4
        self.im = 5
        self.flags = 0b00000000  # 00000LGE
        self.mar = 0  # Memory Address Register, holds the MEMORY ADDRESS we're reading or writing
        self.mdr = 0  # Memory Data Register, holds the VALUE to write or the VALUE just read
        self.branch_table = {
            "alu_ops": {
                MUL: "MUL",
                ADD: "ADD",
                CMP: "CMP",
                AND: "AND",
                OR: "OR",
                XOR: "XOR",
                NOT: "NOT",
                SHL: "SHL",
                SHR: "SHR",
                MOD: "MOD"
            },
            "pc_ignore": {
                CALL: self.handle_call,
                RET: self.handle_ret,
                JMP: self.handle_jmp,
                JEQ: self.handle_jeq,
                JNE: self.handle_jne
            },
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            HLT: self.handle_hlt,
            PUSH: self.handle_push,
            POP: self.handle_pop,
        }

    def ram_read(self, address):
        self.mar = address
        self.mdr = self.ram[self.mar]
        return self.mdr

    def ram_write(self, address, value):
        """
        Value - value to insert at address
        Address - address in ram to insert param value at
        """
        self.mar = address
        self.mdr = value
        self.ram[self.mar] = self.mdr

    def handle_ldi(self, address, value):
        self.reg[address] = value

    def handle_prn(self, address, *args):
        value = self.reg[address]
        print(value)

    def handle_jmp(self, address, *args):
        self.pc = self.reg[address]

    def handle_jeq(self, address, *args):
        # If equal flag is set (true), jump to the address stored in the given register.
        mask = 0b00000001
        if mask & self.im == 1:
            self.pc = self.reg[address]
        else:
            self.pc += 2

    def handle_jne(self, address, *args):
        # If equal flag is clear (false, 0), jump to the address stored in the given register
        mask = 0b00000001
        if mask & self.im == 0:
            self.pc = self.reg[address]
        else:
            self.pc += 2

    def handle_push(self, address, *args):
        # index of register with desired value, retreived from RAM
        reg_index = address
        # value of register that we want to copy over to stack
        value = self.reg[reg_index]
        # decrement value stored in R7(starts as 0xF4 -- 244)
        self.reg[self.sp] -= 1
        # write register value to stack at the index number found in R7
        self.ram_write(self.reg[self.sp], value)

    def handle_pop(self, address, *args):
        # index of register for popped stack value to be inserted at
        reg_index = address
        # value to insert at register index
        value = self.ram_read(self.reg[self.sp])
        # insert value at reg_index
        self.reg[reg_index] = value
        # reduce size of stack
        self.reg[self.sp] += 1

    def handle_call(self, address, value):
        # decrement value stored at R7
        self.reg[self.sp] -= 1
        # write the index address of the next opcode instruction onto the stack
        self.ram_write(self.reg[self.sp], self.pc + 2)

        # registry index directly after CALL opcode
        reg_index = address
        # set pc to value stored at given registry index
        self.pc = self.reg[reg_index]

    def handle_ret(self, address, value):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def handle_hlt(self):
        sys.exit(1)

    def load(self, file_path):
        """Load a .ls8 file from given path and insert into memory."""

        try:
            address = 0

            with open(file_path) as f:
                for line in f:
                    # split line at hash symbol
                    comment_split = line.split('#')

                    # convert from binary string to number and strips all surrounding whitespace
                    binary_string = comment_split[0].strip()
                    try:
                        num = int(binary_string, base=2)
                    except ValueError:
                        continue
                    self.ram_write(address, num)
                    address += 1
        except FileNotFoundError:
            print(
                f"File could not be found. Please make sure you are using a valid file path")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        reg_a_value, reg_b_value = self.reg[reg_a], self.reg[reg_b]
        if op == "ADD":
            reg_a_value += reg_b_value
        elif op == "MUL":
            reg_a_value *= reg_b_value
        elif op == "CMP":
            # FL bits: 00000LGE
            # Compare the values in two registers.
            # If they are equal, set the Equal E flag to 1, otherwise set it to 0.
            if reg_a_value == reg_b_value:
                self.flags = 0b00000001
                self.im = 0b00000001
            # If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.
            elif reg_a_value > reg_b_value:
                self.flags = 0b00000010
                self.im = 0b00000010
            # If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
            elif reg_a_value < reg_b_value:
                self.flags = 0b00000100
                self.im = 0b00000100
        elif op == "AND":
            and_result = reg_a_value & reg_b_value
            self.reg[reg_a] = and_result
        elif op == "OR":
            or_result = reg_a_value | reg_b_value
            self.reg[reg_a] = or_result
        elif op == "XOR":
            xor_result = reg_a_value ^ reg_b_value
            self.reg[reg_a] = xor_result
        elif op == "NOT":
            mask = 0b11111111
            not_result = mask ^ reg_a_value
            self.reg[reg_a] = not_result
        elif op == "SHL":
            # Shift the value in registerA left by the number of bits specified
            # in registerB, filling the low bits with 0.
            result = reg_a_value << reg_b_value
            self.reg[reg_a] = result
        elif op == "SHR":
            # Shift the value in registerA right by the number
            # of bits specified in registerB, filling the high bits with 0.
            result = reg_a_value >> reg_b_value
            self.reg[reg_a] = result
        elif op == "MOD":
            # Divide the value in the first register by the value in the second,
            # storing the remainder of the result in registerA.
            # If the value in the second register is 0, the system should print an error message and halt.
            result = reg_a_value % reg_b_value
            if result > 0:
                self.reg[reg_a] = result
            else:
                print("Numbers not valid for MOD operation, terminating program")
                self.ram_write[self.pc + 3, HLT]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        while running is True:
            ir = self.ram_read(self.pc)  # Instruction Register
            address = self.ram_read(self.pc + 1)
            value = self.ram_read(self.pc + 2)
            if ir == HLT:
                self.branch_table[ir]()
            elif ir in self.branch_table:

                self.branch_table[ir](address, value)
                self.pc += (ir >> 6) + 1
            # separate elif to ensure pc is not incremented
            elif ir in self.branch_table["pc_ignore"]:
                self.branch_table["pc_ignore"][ir](address, value)
            elif ir in self.branch_table["alu_ops"]:
                # op key from branch_table nested alu_ops table
                op = self.branch_table["alu_ops"][ir]

                self.alu(op, address, value)
                self.pc += (ir >> 6) + 1
            else:
                print(f"Invalid command {ir}")
                self.pc += 1

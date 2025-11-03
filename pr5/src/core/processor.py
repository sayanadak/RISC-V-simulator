from abc import ABC, abstractmethod
from .fu import *
from .riscv_tables import *


class Processor(ABC):
    def __init__(self, start, ram, logger):
        self.pc = start
        self.curr_pc = 0
        self.registers = [0] * 32  # x0 to x31
        self.mem = ram
        self.logr = logger
        self.decoded = {}
        self.ldata = 0

    def fetch(self, pc) -> int:
        """
        Fetch the instruction from memory, and update PC
        returns instruction
        """
        try:
            curr_pc = pc 
            instruction = self.mem.read_word(curr_pc)
            self.logr.debug(f"got instruction {instruction:08x} at {curr_pc:08x}")
            return instruction, curr_pc
        except ValueError as e:
            self.logr.error(f"Error fetching instruction at {curr_pc:08x}: {e}")
            exit()
            

    def decode(self, instruction: int):
        """
        Gets an instruction (32-bit integer) and returns
        a dictionary with the following fields {"opcode", "rs1", "rs2", "rd", "imm"}
        """
        # Extract the opcode (7 bits)

        decoded = {}
        opcode = instruction & 0x7F
        decoded["opcode"] = opcode

        if opcode == 0x33:  # R-type (Arithmetic)
            funct7 = (instruction >> 25) & 0x7F
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            decoded["rs1"] = rs1
            decoded["rs2"] = rs2
            decoded["rd"] = rd
            decoded["funct3"] = funct3
            decoded["funct7"] = funct7
            decoded["imm"] = 0
        elif opcode == 0x03:  # I-type (Load)
            imm = instruction >> 20
            if (imm > 0x800):
            # if (imm & 0x800):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            decoded["rs1"] = rs1
            decoded["rs2"] = 0
            decoded["rd"] = rd
            decoded["funct3"] = funct3
            decoded["funct7"] = 0x00
            decoded["imm"] = imm
        elif opcode == 0x13:  # I-type (Immediate Arithmetic)
            imm = instruction >> 20
            if (imm > 0x800):
            # if (imm & 0x800):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            decoded["rs1"] = rs1
            decoded["rs2"] = 0
            decoded["rd"] = rd
            decoded["funct3"] = funct3
            decoded["funct7"] = 0x00
            decoded["imm"] = imm
        elif opcode == 0x23:  # S-type (Store)
            imm = ((instruction >> 25) << 5) | ((instruction >> 7) & 0x1F)
            if (imm > 0x800):
            # if (imm & 0x800):
                imm = imm - (1 << 32)
                imm = imm | 0xFFFFF000
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            decoded["rs1"] = rs1
            decoded["rs2"] = rs2
            decoded["rd"] = 0
            decoded["funct3"] = funct3
            decoded["funct7"] = 0x00
            decoded["imm"] = imm 
        elif opcode == 0x63:  # B-type (Branch)
            imm_12 = (instruction >> 31) & 0x1
            imm_10_5 = (instruction >> 25) & 0x3F
            imm_4_1 = (instruction >> 8) & 0xF 
            imm_11 = (instruction >> 7) & 0x1
            imm = ((imm_12 << 11) | (imm_11 << 10) | (imm_10_5 << 4) | imm_4_1) << 1
            if (imm > 0x1000):
            # if (imm & 0x1000):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            decoded["rs1"] = rs1
            decoded["rs2"] = rs2
            decoded["rd"] = 0
            decoded["funct3"] = funct3
            decoded["funct7"] = 0x00
            decoded["imm"] = imm
        elif opcode == 0x37:  # U-type (LUI)
            imm = instruction & 0xFFFFF000
            rd = (instruction >> 7) & 0x1F
            decoded["rs1"] = 0
            decoded["rs2"] = 0
            decoded["rd"] = rd
            decoded["funct3"] = 0x0
            decoded["funct7"] = 0x00
            decoded["imm"] = imm
        elif opcode == 0x17:  # U-type (AUIPC)
            imm = instruction & 0xFFFFF000
            rd = (instruction >> 7) & 0x1F
            decoded["rs1"] = 0
            decoded["rs2"] = 0
            decoded["rd"] = rd
            decoded["funct3"] = 0x0
            decoded["funct7"] = 0x00
            decoded["imm"] = imm
        elif opcode == 0x6F:  # J-type (JAL)
            imm_20 = (instruction >> 31) & 0x1  
            imm_10_1 = (instruction >> 21) & 0x3FF
            imm_11 = (instruction >> 20) & 0x1
            imm_19_12 = (instruction >> 12) & 0xFF
            imm = ((imm_20 << 19) | (imm_19_12 << 11) | (imm_11 << 10) | imm_10_1) << 1
            if (imm > 0x100000):
            # if (imm &   0x100000):
                imm = imm | 0xFFF00000
                imm = imm - (1 << 32)
            rd = (instruction >> 7) & 0x1F
            decoded["rs1"] = 0
            decoded["rs2"] = 0
            decoded["rd"] = rd
            decoded["funct3"] = 0x0
            decoded["funct7"] = 0x00
            decoded["imm"] = imm
        else:
            decoded["opcode"] = opcode
            decoded["rs1"] = 0
            decoded["rs2"] = 0
            decoded["rd"] = 0
            decoded["imm"] = 0
            decoded["funct3"] = 0x0
            decoded["funct7"] = 0x00

        self.logr.debug(f"opcode = {decoded['opcode']:02x}, " + 
                        f"funct3 = {decoded['funct3']:01x}, " + 
                        f"funct7 = {decoded['funct7']:02x}")
        op = ((decoded['opcode'] << 12) | 
                   (decoded['funct3'] << 8) | 
                   (decoded['funct7']))
        
        return decoded, op

    def operand_fetch(self,decoded, registers,curr_pc, op  ):
        rs1 = decoded["rs1"]
        rs2 = decoded["rs2"]
        v_rs1 = registers[rs1] if rs1 != 0 and rs1 != None else 0 
        v_rs2 = registers[rs2] if rs2 != 0 and rs2 != None else 0 

        v_imm = decoded["imm"]
        self.logr.debug(f"rs1 = {rs1}, rs2 = {rs2}, imm = {hex(v_imm)}")
        v_pc  = curr_pc

        op1, op2 = alu_operands.get(op, (None, None))(v_rs1, v_rs2, v_imm, v_pc)
        # # FIXME: the choice of the below constant may be correct always
        # if (self.op1 > 0xF0000000):
        #     self.op1 = self.op1 - (1 << 32)

        # # FIXME: the choice of the below constant may be correct always
        # if (self.op2 > 0xF00000000):
        #     self.op2 = self.op2 - (1 << 32)
        self.logr.debug(f"op1: {op1}, op2: {op2}")

        return op1, op2, op


    def execute(self,op1, op2, op ):
        """
        Execute the instruction
        decoded_instr, operand1 and operand2 are returned by previous stages
        returns the result of the operation
        """
        result = alu_function.get(op, None)(op1, op2)
        self.logr.debug(f"Result of {op:05x} is: {result}")
        return result

    def update_pc(self, op, result, curr_pc, decoded):
        """
        Update PC to take a branch or jump
        """
        # TODO: Complete this function appropriately
        new_pc = 0
        if is_branch(op) and result:
            new_pc = curr_pc + decoded["imm"]
        # Check if the instruction is a jump
        elif is_jump(op):
            # For JALR, the LSB of the target address must be set to 0
            if decoded["opcode"] == 0x67:  # This is the opcode for JALR
                new_pc = result & 0xFFFFFFFE
            else:  # JAL
                new_pc = result
        else:  
            # Straight-line code is default case
            new_pc = curr_pc + 4

        return new_pc
        
       

    def mem_access(self, op,result,decoded,store_data): #this store_data is nothign but rs2
        """
        Access memory based on the instruction.
        """
        inst = op
        addr = result  # address is generated by execute()
        ldata=None

        # Handle load instructions
        if is_load(inst):
            masked_inst = (inst & 0x00F00) >> 8
            if (masked_inst == 0x0 or masked_inst == 0x4):
                ldata = self.mem.read(addr)
            elif (masked_inst == 0x1 or masked_inst == 0x5):
                ldata = self.mem.read_halfword(addr)
            elif (masked_inst == 0x2):
                ldata = self.mem.read_word(addr)
            else:
                self.logr.error(f"Invalid load op {inst:05x}")
                exit()
        
        # Handle store instructions
        # rs2 = decoded["rs2"]
        # data = registers[rs2] if rs2 != 0 and rs2 != None else 0 
        data = store_data
        if is_store(inst):
            masked_inst = (inst & 0x00F00) >> 8
            if (masked_inst == 0x0):
                self.mem.write(addr, (data & 0xFF))
            elif (masked_inst == 0x1):
                self.mem.write_halfword(addr, (data & 0xFFFF))
            elif (masked_inst == 0x2):
                self.mem.write_word(addr, data)
            else:
                self.logr.error(f"Invalid store op {inst:05x}")
                exit()
        return ldata


    def reg_write(self,op,decoded, curr_pc,pc, result , ldata, registers):
        """
        Write the result of the operation back to the register.
        """
        inst = op
        rd = decoded["rd"]
        
        if is_branch(inst):
            self.logr.out(f"{curr_pc:08x} | " + 
                          f"next_pc = {pc:08x} | " + 
                          f"x? = {0:08x} | " + 
                          f"mem[?] = {0:08x}")
            return
        
        if is_jump(inst):
            write_val = curr_pc + 4 
            if(rd!=0):
                # registers[rd] = result #changes might required
                registers[rd] = write_val + 4; 
            self.logr.out(f"{curr_pc:08x} | " +
                          f"next_pc = {pc:08x} | " + 
                          f"x{rd} = {registers[rd]:08x} | " +
                          f"mem[?] = {0:08x}")
            return

        if is_unimplemented(inst):
            self.logr.out(f"{curr_pc:08x} | " + 
                          f"next_pc = {pc:08x} | " + 
                          f"x? = {0:08x} | " + 
                          f"mem[?] = {0:08x} *unimplemented*")
            return

        if is_load(inst):
            registers[rd] = ldata
            self.logr.out(f"{curr_pc:08x} | " + 
                          f"next_pc = {pc:08x} | " +
                          f"x{rd} = {registers[rd]:08x} | " +
                          f"mem[{result:08x}] => {ldata:08x}")
            return

        if is_store(inst):
            rs2 = decoded["rs2"]
            data = registers[rs2] if rs2 != 0 and rs2 != None else 0 
            self.logr.out(f"{curr_pc:08x} | " +
                          f"next_pc = {pc:08x} | " +
                          f"x? = {0:08x} | " + 
                          f"mem[{result:08x}] <= {data:08x}")
            return 
        
        # All other instructions
        registers[rd] = result
        self.logr.out(f"{curr_pc:08x} | " + 
                      f"next_pc = {pc:08x} | " +
                      f"x{rd} = {registers[rd]:08x} | " + 
                      f"mem[?] = {0:08x}")

    @abstractmethod
    def run(self, num_insts):
        """Run the processor. To be implemented by subclasses."""
        pass

#
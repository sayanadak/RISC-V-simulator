from .processor import Processor
from .riscv_tables import * # Need this for is_unimplemented

class SingleCycleProcessor(Processor):
    def __init__(self, start, ram, logger, st):
        super().__init__(start, ram, logger)
        self.stats = st

    def run(self, num_insts):
        """
        Run the processor in a single cycle for each instruction.
        """
        i_cnt = 0
        # registers = [0]*32  # This is already a member of the base Processor class
        self.stats.reset()
        while (i_cnt < num_insts):
            
            # 1. 'fetch' is stateless, so we must pass the processor's current PC
            instruction, curr_pc = self.fetch(self.pc)
            
            if instruction is None:
                break 
            decoded, op = self.decode(instruction)

            # 2. 'operand_fetch' returns 3 values (op1, op2, op)
            # 3. Pass the 'curr_pc' from fetch, not the stale 'self.curr_pc'
            op1, op2, op = self.operand_fetch(decoded, self.registers, curr_pc, op)
            
            result = self.execute(op1, op2, op)

            rs2 = decoded["rs2"]
            store_data = self.registers[rs2] if rs2 != 0 and rs2 != None else 0

            ldata = self.mem_access(op, result, decoded,store_data)

            new_pc = self.update_pc(op, result, curr_pc, decoded)
            
            # Pass the processor's register file 'self.registers'
            self.reg_write(op, decoded, curr_pc, new_pc, result, ldata, self.registers)
            
            # 4. CRITICAL: Update the processor's state (self.pc) for the next loop
            self.pc = new_pc
            
            i_cnt += 1
            self.stats.increment_clock_cycle()
            self.stats.increment_instruction_count()
        
        self.logr.info(f"Simulated {i_cnt} instructions")
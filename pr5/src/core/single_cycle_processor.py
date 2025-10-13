from .processor import Processor

class SingleCycleProcessor(Processor):
    def __init__(self, start, ram, logger, st):
        super().__init__(start, ram, logger)
        self.stats = st

    def run(self, num_insts):
        """
        Run the processor in a single cycle for each instruction.
        """
        i_cnt = 0
        while (i_cnt < num_insts):
            instruction = self.fetch()
            if instruction is None:
                break
            self.decode(instruction)
            self.operand_fetch()
            self.execute()
            self.mem_access()
            self.update_pc()
            self.reg_write()
            i_cnt += 1
            self.stats.increment_instruction_count()
        
        self.logr.info(f"Simulated {i_cnt} instructions")


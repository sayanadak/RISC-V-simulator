class FPipelinedProcessor:
    def __init__(self, start_pc, mem, loggr, stats):
        self.pc = start_pc
        self.mem = mem
        self.logr = loggr
        self.stats = stats

        self.pipeline_regs = {
            "IF/DE": None,
            "DE/EX": None,
            "EX/MA": None,
            "MA/WB": None
        }

        self.halted = False
        self.registers = [0] * 32

    def fetch(self):
        """Instruction fetch stage"""
        if self.halted:
            self.pipeline_regs["IF/DE"] = None
            return

        inst = self.mem.read_word(self.pc)
        self.pipeline_regs["IF/DE"] = {"pc": self.pc, "inst": inst}
        self.logr.debug(f"Fetched instruction {inst:08x} at PC {self.pc:08x}")
        self.pc += 4

        self.stats.clock_cycles += 1

    def decode(self):
        """Instruction decode stage"""
        reg = self.pipeline_regs["IF/DE"]
        if not reg:
            self.pipeline_regs["DE/EX"] = None
            return

        inst = reg["inst"]
        self.pipeline_regs["DE/EX"] = reg
        self.logr.debug(f"Decoded instruction {inst:08x} at PC {reg['pc']:08x}")

    def execute(self):
        """Execute stage"""
        reg = self.pipeline_regs["DE/EX"]
        if not reg:
            self.pipeline_regs["EX/MA"] = None
            return

        inst = reg["inst"]
        pc = reg["pc"]

        self.registers[10] = (self.registers[10] + 1) & 0xFFFFFFFF

        self.pipeline_regs["EX/MA"] = reg
        self.logr.debug(f"Executed instruction {inst:08x} at PC {pc:08x}")

        self.stats.instruction_count += 1

    def memory_access(self):
        """Memory access stage"""
        reg = self.pipeline_regs["EX/MA"]
        if not reg:
            self.pipeline_regs["MA/WB"] = None
            return

        inst = reg["inst"]
        pc = reg["pc"]

        addr = 0x80008000
        self.mem.write_word(addr, self.registers[10])
        self.logr.debug(f"Memory write: {self.registers[10]:08x} to {addr:08x}")

        self.pipeline_regs["MA/WB"] = reg

        self.stats.memory_accesses += 1

    def write_back(self):
        """Write back stage"""
        reg = self.pipeline_regs["MA/WB"]
        if not reg:
            return

        inst = reg["inst"]
        pc = reg["pc"]
        self.logr.debug(f"Write back for instruction {inst:08x} at PC {pc:08x}")

    def run(self, num_insts):
        for _ in range(num_insts):
            self.write_back()
            self.memory_access()
            self.execute()
            self.decode()
            self.fetch()

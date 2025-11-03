from .processor import Processor

class PipelinedProcessor(Processor):
    def __init__(self, start, ram, logger, st):
        super().__init__(start, ram, logger)
        self.stats = st

        self.pipeline_regs = {
            "IF/ID": None,
            "ID/EX": None,
            "EX/MEM": None,
            "MEM/WB": None,
        }
        
        self.flush_count = 0
        self.branch_taken = False
        self.new_pc = None

    def run(self, num_insts):
        """
        Run a 5-stage pipelined processor.
        Implements basic 5-stage pipeline: IF -> ID -> EX -> MEM -> WB
        Handles control hazards with 3-cycle penalty (target PC after EX stage)
        Handles data hazards with stalls (no forwarding)
        """
        cycle = 0
        instructions_completed = 0
        
        while instructions_completed < num_insts:
            cycle += 1
                        
            wb_done = self.writeback_stage()
            if wb_done:
                instructions_completed += 1
            
            self.memory_stage()
            self.execute_stage()
            stall = self.decode_stage()
            
            if not stall:
                self.fetch_stage()
            else:
                pass
        
        self.stats['cycles'] = cycle
        self.logger.log(f"[PIPELINE] Completed {num_insts} instructions in {cycle} cycles")

    def fetch_stage(self):
        """
        Instruction Fetch (IF) stage
        Fetches instruction from memory at PC and stores in IF/ID register
        """
        if self.flush_count > 0:
            self.pipeline_regs["IF/ID"] = {"bubble": True}
            self.flush_count -= 1
            return
        
        if self.branch_taken:
            self.pc = self.new_pc
            self.branch_taken = False
        
        try:
            inst = self.fetch(self.pc)
            self.pipeline_regs["IF/ID"] = {
                "pc": self.pc,
                "inst": inst,
                "bubble": False
            }
            self.pc += 4 
        except:
            self.pipeline_regs["IF/ID"] = {"bubble": True}

    def decode_stage(self):
        """
        Instruction Decode (ID) stage
        Decodes instruction and reads registers
        Returns True if pipeline should stall due to data hazard
        """
        if_id = self.pipeline_regs["IF/ID"]
        
        if if_id is None or if_id.get("bubble"):
            self.pipeline_regs["ID/EX"] = {"bubble": True}
            return False
        
        inst = if_id["inst"]
        pc = if_id["pc"]
        
        decoded = self.decode(inst)
        
        stall = self.check_data_hazard(decoded)
        
        if stall:
            self.pipeline_regs["ID/EX"] = {"bubble": True}
            return True
        
        operands = self.operand_fetch(decoded)
        
        self.pipeline_regs["ID/EX"] = {
            "pc": pc,
            "decoded": decoded,
            "operands": operands,
            "bubble": False
        }
        
        return False

    def check_data_hazard(self, decoded):
        """
        Check if there's a load-use data hazard that requires a stall
        Returns True if stall is needed
        """
        id_ex = self.pipeline_regs["ID/EX"]
        
        if id_ex is None or id_ex.get("bubble"):
            return False
        
        prev_decoded = id_ex.get("decoded")
        if prev_decoded and prev_decoded.get("opcode") in ["lw", "lb", "lh", "lbu", "lhu"]:
            prev_rd = prev_decoded.get("rd")
            
            curr_rs1 = decoded.get("rs1")
            curr_rs2 = decoded.get("rs2")
            
            if prev_rd and (prev_rd == curr_rs1 or prev_rd == curr_rs2):
                return True
        
        return False

    def execute_stage(self):
        """
        Execute (EX) stage
        Performs ALU operations and determines branch target
        """
        id_ex = self.pipeline_regs["ID/EX"]
        
        if id_ex is None or id_ex.get("bubble"):
            self.pipeline_regs["EX/MEM"] = {"bubble": True}
            return
        
        decoded = id_ex["decoded"]
        operands = id_ex["operands"]
        pc = id_ex["pc"]
        
        result = self.execute(decoded, operands, pc)
        
        if decoded.get("control_flow"):
            target_pc = result.get("target_pc")
            if target_pc is not None and target_pc != pc + 4:
                self.flush_count = 3
                self.branch_taken = True
                self.new_pc = target_pc
        
        self.pipeline_regs["EX/MEM"] = {
            "decoded": decoded,
            "result": result,
            "bubble": False
        }

    def memory_stage(self):
        """
        Memory Access (MEM) stage
        Accesses memory for load/store instructions
        """
        ex_mem = self.pipeline_regs["EX/MEM"]
        
        if ex_mem is None or ex_mem.get("bubble"):
            self.pipeline_regs["MEM/WB"] = {"bubble": True}
            return
        
        decoded = ex_mem["decoded"]
        result = ex_mem["result"]
        
        mem_data = self.mem_access(decoded, result)
        
        self.pipeline_regs["MEM/WB"] = {
            "decoded": decoded,
            "result": result,
            "mem_data": mem_data,
            "bubble": False
        }

    def writeback_stage(self):
        """
        Write Back (WB) stage
        Writes result back to register file
        Returns True if an instruction completed
        """
        mem_wb = self.pipeline_regs["MEM/WB"]
        
        if mem_wb is None or mem_wb.get("bubble"):
            return False
        
        decoded = mem_wb["decoded"]
        result = mem_wb["result"]
        mem_data = mem_wb.get("mem_data")
        
        self.reg_write(decoded, result, mem_data)
        
        return True
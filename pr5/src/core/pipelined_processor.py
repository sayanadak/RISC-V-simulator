from .processor import Processor


class PipelinedProcessor(Processor):
    def __init__(self, start, ram, logger, st):
        super().__init__(start, ram, logger)
        self.stats = st

        # NOTE: The following dictionary is only suggestive. You may wish to
        # use a different structure or names if deemed fit
        self.pipeline_regs = {
            "IF/ID": None,
            "ID/EX": None,
            "EX/MEM": None,
            "MEM/WB": None,
        }

    def run(self, num_insts):
        """
        Run a 5-stage pipelined processor.
        """
        # TODO: Complete this function in such a way that the statistics file
        # (stats.json) has the correct cycle count when the program is executed
        # on a simple 5-stage pipeline without any forwarding or bypass
        # mechanism implemented. Assume that the targetPC is generated after
        # the EX stage (there will be three wrong-path instructions in case of
        # a control hazard). You should change the interfaces of fetch(),
        # decode(), operand_fetch(), execute(), update_pc(), mem_access(), and
        # reg_write() functions of the Processor base class as needed, and
        # update the code of the SingleCycleProcessor appropriately. Refrain
        # from changing the output formats of the [OUT] messages printed from
        # the reg_write() function. You can ignore counting the number of
        # memory accesses for now.

        '''
            fetch -> decode -> execute -> memory_access -> write_back 
            but this flow can't be done in simulator because each state will 
            use it's previous registers latch to get registers,oprand, oprator etc.
            go with normal flow then fetch will update the IF/ID regsiters. and decode
            will be using this IF/ID registers to execute instruction but which is wrong. 
            hence we can change flow to avoid this or we can create another copy of this 
            registers which will store the previous register values. 

            I am trying to copy all the registers in dummy variable at the start of the clock 
            then this dummy variables will be used for each stage and original pipeline_regs will be updated
            after each stage run

            Data hazards are simply countered by adding bubble. 
            1.controle hazard->add two bubbles
            2.data hazard(RAW dependency) -> add two bubbles
            3.structural hazards
        '''
        self.stats.reset(); 
        total_cycles = num_insts + 4 # four instruction to drain the pipeline

        for cycle in range(total_cycles):
            dummy_regs = self.pipeline_regs.copy() # normal dummy=self.pipeline_regs will make changes to pipeline_regs, hence deep copy

            #INSTRUCTION FETCH => should store the insruction and current_pc to IF/ID_regs
            if(cycle<num_insts):
                instruction,curr_pc = self.fetch(self.pc)
                self.pc = curr_pc + 4; #update pc logic for later 
                self.pipeline_regs["IF/ID"] = {
                    "instruction":instruction, 
                    "curr_pc" : curr_pc
                }
            else:
                self.pipeline_regs["IF/ID"] = None #bubble




            #INSTRUCTION DECODE AND OPRAND FETCH => should store the curr_pc, decoded, op, op1, op2,rs2 to ID/EX STAGE
            id_data = dummy_regs["IF/ID"] 
            if id_data is not None: 
                decoded, op = self.decode(id_data["instruction"])
                op1,op2,_ = self.operand_fetch(decoded,self.registers,id_data["curr_pc"], op)
                self.pipeline_regs["ID/EX"] ={
                    "curr_pc": id_data["curr_pc"], 
                    "decoded": decoded,     
                    "op" : op, 
                    "op1" : op1, 
                    "op2" : op2, 
                    "store_data" : self.registers[decoded["rs2"]]
                }
            else:
                self.pipeline_regs["ID/EX"] = None

            #EXECUTE => shold store the curr_pc, decodec, op, rs2, result, next_pc to EX/MEM_regs
            ex_data = dummy_regs["ID/EX"]
            if ex_data is not None:
                result = self.execute(ex_data["op1"], ex_data["op2"], ex_data["op"])
                next_pc = self.update_pc(ex_data["op"], result, ex_data["curr_pc"], ex_data["decoded"])
                self.pipeline_regs["EX/MEM"] = {
                    "curr_pc": ex_data["curr_pc"], "decoded": ex_data["decoded"],
                    "op": ex_data["op"], "store_data": ex_data["store_data"],
                    "result": result, "next_pc": next_pc
                }
            else:
                self.pipeline_regs["EX/MEM"] = None


            #MEMORY ACCESS=> should store the curr_pc, decoded,op, result, next_pc, ldata to MEM/WB_regs
            mem_data = dummy_regs["EX/MEM"]
            if mem_data is not None:
                ldata = self.mem_access(
                    mem_data["op"], mem_data["result"], 
                    mem_data["decoded"], mem_data["store_data"] # Use passed store_data
                )
                self.pipeline_regs["MEM/WB"] = {
                    "curr_pc": mem_data["curr_pc"], "decoded": mem_data["decoded"],
                    "op": mem_data["op"], "result": mem_data["result"],
                    "next_pc": mem_data["next_pc"], "ldata": ldata
                }
            else:
                self.pipeline_regs["MEM/WB"] = None

            #WRITE BACK 
            wb_data = dummy_regs["MEM/WB"]
            if wb_data is not None:
                self.reg_write(
                    wb_data["op"], wb_data["decoded"], wb_data["curr_pc"],
                    wb_data["next_pc"], wb_data["result"], wb_data["ldata"],
                    self.registers
                )


        pass


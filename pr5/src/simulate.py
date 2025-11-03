#!/usr/bin/env python3
import argparse
import os
import sys
import ram
import loader
import logger
import stats
import core

def parse_args():
    parser = argparse.ArgumentParser(description="RISC-V Processor Simulator")
    parser.add_argument('--start', type=lambda x: int(x.replace('0x', '').replace('0X', ''), 16), 
                        required=True,
                        help='Start PC in hex (e.g. 0x80000000 or 80000000)')
    parser.add_argument('r5ob_path', type=str,
                        help='Path to the input r5ob file')
    parser.add_argument('--num_insts', type=int, default=1000,
                        help='Number of instructions to simulate (default: 1000)')
   
    parser.add_argument(
        '--proc',
        type=str,
        choices=['SingleCycleProcessor', 'PipelinedProcessor'],
        default='SingleCycleProcessor',
        help='Select processor type: SingleCycleProcessor or PipelinedProcessor (default: SingleCycleProcessor)'
    )
    
    return parser.parse_args()

def run_simulation():
    """Main simulation entry point"""
    
    loggr = logger.setup()
    cmd = "python3 " + " ".join(sys.argv)
    loggr.info(f"Running: {cmd}")

    args = parse_args()

    if not os.path.isfile(args.r5ob_path):
        loggr.error(f"Error: Executable file '{args.r5ob_path}' does not exist.")
        sys.exit(1)

    mem = ram.RAM(loggr)
    loader.load(mem, args.r5ob_path)
    
    st = stats.Statistics(loggr)
    
    if args.proc == 'SingleCycleProcessor':
        processor = core.SingleCycleProcessor(args.start, mem, loggr, st)
        loggr.info("Using SingleCycleProcessor")
    elif args.proc == 'PipelinedProcessor':
        processor = core.PipelinedProcessor(args.start, mem, loggr, st)
        loggr.info("Using PipelinedProcessor")
    else:
        loggr.error(f"Invalid processor type: {args.proc}")
        sys.exit(1)

    loggr.info(f"Start address: {hex(args.start)}")
    loggr.info(f"Executable path: {args.r5ob_path}")
    loggr.info(f"Number of instructions: {args.num_insts}")

    try:
        processor.run(args.num_insts)
    except Exception as e:
        loggr.error(f"Simulation error: {e}")
        import traceback
        loggr.error(traceback.format_exc())
        sys.exit(1)
    
    st.write_statistics("stats.json")
    loggr.info("Simulation completed successfully")

if __name__ == "__main__":
    run_simulation()
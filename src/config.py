from m5.objects import *

# Generalized CPU class with configurable options
class ConfigurableCPU(DerivO3CPU):  # Using DerivO3CPU for flexibility in ILP techniques
    def __init__(self, num_threads=1, fetch_width=1, decode_width=1, issue_width=1, commit_width=1, branch_pred=None):
        super().__init__()
        self.numThreads = num_threads
        self.fetchWidth = fetch_width
        self.decodeWidth = decode_width
        self.issueWidth = issue_width
        self.commitWidth = commit_width
        self.branchPred = branch_pred if branch_pred else None

# General system builder function with ILP parameters
def build_system(ilp_type="basic", branch_pred=None, num_threads=1, width=1):
    system = System()
    system.clk_domain = SrcClockDomain(clock='2GHz', voltage_domain=VoltageDomain())
    system.mem_mode = 'timing' if ilp_type in ["branch_prediction", "superscalar", "smt"] else 'atomic'
    system.mem_ranges = [AddrRange('512MB')]

    # Set CPU configuration based on ILP type
    if ilp_type == "basic":
        system.cpu = ConfigurableCPU()
    elif ilp_type == "branch_prediction":
        system.cpu = ConfigurableCPU(branch_pred=branch_pred)
    elif ilp_type == "superscalar":
        system.cpu = ConfigurableCPU(fetch_width=width, decode_width=width, issue_width=width, commit_width=width)
    elif ilp_type == "smt":
        system.cpu = ConfigurableCPU(num_threads=num_threads, fetch_width=width, decode_width=width, issue_width=width, commit_width=width)
    else:
        raise ValueError("Invalid ILP type. Choose from: basic, branch_prediction, superscalar, smt.")

    # Connect CPU to system memory
    system.membus = SystemXBar()
    system.cpu.icache_port = system.membus.cpu_side_ports
    system.cpu.dcache_port = system.membus.cpu_side_ports

    # Memory controller configuration
    system.mem_ctrl = DDR3_1600_8x8()
    system.mem_ctrl.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Workload setup (e.g., running "Hello World")
    binary = "tests/test-progs/hello/bin/x86/linux/hello"
    system.workload = SEWorkload.init_compatible(binary)
    process = Process(cmd=[binary])
    system.cpu.workload = process
    system.cpu.createThreads()

    # Connect system ports
    system.system_port = system.membus.cpu_side_ports
    return system

# Simulation runner
def run_simulation(ilp_type="basic", branch_pred=None, num_threads=1, width=1):
    root = Root(full_system=False, system=build_system(ilp_type, branch_pred, num_threads, width))
    m5.instantiate()
    print(f"Starting {ilp_type} simulation with {num_threads} threads and width {width}...")
    exit_event = m5.simulate()
    print(f"Simulation finished: {exit_event.getCause()}")

if __name__ == "__main__":
    # Examples of running different ILP configurations:
    # Basic Pipeline
    run_simulation(ilp_type="basic")
    # Branch Prediction (e.g., LTAGE predictor)
    run_simulation(ilp_type="branch_prediction", branch_pred=LTAGE())
    # Superscalar with width 4
    run_simulation(ilp_type="superscalar", width=4)
    # SMT with 2 threads and width 4
    run_simulation(ilp_type="smt", num_threads=2, width=4)

# MSCS531_Assignment4
Instruction- Level Parallelism (ILP) in computer architecture. Students will engage with theoretical underpinnings, analyze practical techniques, evaluate trade-offs, and scrutinize real-world implementations. T
Here is a guide and sample configuration code for setting up a basic gem5 simulation with a pipeline and progressing through the ILP techniques you mentioned. **Please ensure you have gem5 installed and configured.** For this setup, I’ll provide Python configuration scripts as used in gem5’s Python-based API, focusing on basic pipeline, branch prediction, superscalar configuration, and SMT.

### 1. Basic Pipeline Simulation

This configuration defines a simple pipeline with fetch, decode, execute, memory, and writeback stages.

#### `basic_pipeline_config.py`

```python
from m5.objects import *
from m5.util import addToPath
from m5 import options

# Define simple CPU and memory system
class BasicPipelineCPU(AtomicSimpleCPU):  # Using AtomicSimpleCPU for simplicity
    def __init__(self):
        super().__init__()

# Define a basic system with CPU, memory, and a program to run
def build_system():
    system = System()
    system.clk_domain = SrcClockDomain(clock='1GHz', voltage_domain=VoltageDomain())
    system.mem_mode = 'atomic'
    system.mem_ranges = [AddrRange('512MB')]

    # Simple CPU with pipeline stages
    system.cpu = BasicPipelineCPU()
    system.membus = SystemXBar()

    # Memory controller
    system.mem_ctrl = DDR3_1600_8x8()
    system.mem_ctrl.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Connect CPU to memory bus
    system.cpu.icache_port = system.membus.cpu_side_ports
    system.cpu.dcache_port = system.membus.cpu_side_ports

    # Program to run (e.g., hello world)
    binary = "tests/test-progs/hello/bin/x86/linux/hello"
    system.workload = SEWorkload.init_compatible(binary)
    process = Process(cmd=[binary])
    system.cpu.workload = process
    system.cpu.createThreads()

    # Connect system ports
    system.system_port = system.membus.cpu_side_ports
    return system

# Run simulation
def run_simulation():
    root = Root(full_system=False, system=build_system())
    m5.instantiate()
    print("Starting simulation...")
    exit_event = m5.simulate()
    print(f"Simulation finished: {exit_event.getCause()}")

if __name__ == "__main__":
    run_simulation()
```

### 2. Branch Prediction Configuration

To add branch prediction, update the CPU to use a simple branch predictor (e.g., a static predictor that always predicts “taken”).

#### `branch_prediction_config.py`

```python
from m5.objects import *

class BranchPredictionCPU(TimingSimpleCPU):  # TimingSimpleCPU for dynamic timing
    def __init__(self):
        super().__init__()
        self.branchPred = LTAGE()  # Lightweight TAGE predictor

def build_system():
    system = System()
    system.clk_domain = SrcClockDomain(clock='2GHz', voltage_domain=VoltageDomain())
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('512MB')]

    # CPU with branch prediction
    system.cpu = BranchPredictionCPU()
    system.membus = SystemXBar()

    # Memory controller
    system.mem_ctrl = DDR3_1600_8x8()
    system.mem_ctrl.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Program to run
    binary = "tests/test-progs/hello/bin/x86/linux/hello"
    system.workload = SEWorkload.init_compatible(binary)
    process = Process(cmd=[binary])
    system.cpu.workload = process
    system.cpu.createThreads()

    # Connect system ports
    system.system_port = system.membus.cpu_side_ports
    return system

# Run simulation
def run_simulation():
    root = Root(full_system=False, system=build_system())
    m5.instantiate()
    print("Starting branch prediction simulation...")
    exit_event = m5.simulate()
    print(f"Simulation finished: {exit_event.getCause()}")

if __name__ == "__main__":
    run_simulation()
```

### 3. Superscalar Configuration

In this setup, we’ll configure a superscalar CPU that can issue multiple instructions per cycle. We will use `DerivO3CPU` for out-of-order execution, which supports superscalar configuration.

#### `superscalar_config.py`

```python
from m5.objects import *

class SuperscalarCPU(DerivO3CPU):
    def __init__(self):
        super().__init__()
        self.numThreads = 1
        self.numROBEntries = 192
        self.fetchWidth = 4
        self.decodeWidth = 4
        self.issueWidth = 4
        self.commitWidth = 4

def build_system():
    system = System()
    system.clk_domain = SrcClockDomain(clock='2GHz', voltage_domain=VoltageDomain())
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('512MB')]

    # Superscalar CPU setup
    system.cpu = SuperscalarCPU()
    system.membus = SystemXBar()

    # Memory controller
    system.mem_ctrl = DDR3_1600_8x8()
    system.mem_ctrl.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Program to run
    binary = "tests/test-progs/hello/bin/x86/linux/hello"
    system.workload = SEWorkload.init_compatible(binary)
    process = Process(cmd=[binary])
    system.cpu.workload = process
    system.cpu.createThreads()

    # Connect system ports
    system.system_port = system.membus.cpu_side_ports
    return system

# Run simulation
def run_simulation():
    root = Root(full_system=False, system=build_system())
    m5.instantiate()
    print("Starting superscalar simulation...")
    exit_event = m5.simulate()
    print(f"Simulation finished: {exit_event.getCause()}")

if __name__ == "__main__":
    run_simulation()
```

### 4. Simultaneous Multithreading (SMT) Configuration

For SMT, we’ll enable multiple threads on `DerivO3CPU`.

#### `smt_config.py`

```python
from m5.objects import *

class SMTCPU(DerivO3CPU):
    def __init__(self):
        super().__init__()
        self.numThreads = 2  # Enable SMT with 2 threads
        self.fetchWidth = 4
        self.decodeWidth = 4
        self.issueWidth = 4
        self.commitWidth = 4

def build_system():
    system = System()
    system.clk_domain = SrcClockDomain(clock='2GHz', voltage_domain=VoltageDomain())
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('512MB')]

    # SMT CPU setup
    system.cpu = SMTCPU()
    system.membus = SystemXBar()

    # Memory controller
    system.mem_ctrl = DDR3_1600_8x8()
    system.mem_ctrl.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Program to run
    binary = "tests/test-progs/hello/bin/x86/linux/hello"
    system.workload = SEWorkload.init_compatible(binary)
    process = Process(cmd=[binary])
    system.cpu.workload = process
    system.cpu.createThreads()

    # Connect system ports
    system.system_port = system.membus.cpu_side_ports
    return system

# Run simulation
def run_simulation():
    root = Root(full_system=False, system=build_system())
    m5.instantiate()
    print("Starting SMT simulation...")
    exit_event = m5.simulate()
    print(f"Simulation finished: {exit_event.getCause()}")

if __name__ == "__main__":
    run_simulation()
```

---

### Running the Configurations

1. Place each script in your `gem5` directory or a dedicated folder.
2. Run the script from the command line with:

   ```bash
   gem5.opt <config_script.py>
   ```

Replace `<config_script.py>` with the desired configuration file name, such as `basic_pipeline_config.py`, `branch_prediction_config.py`, etc.

---

### Collecting Data and Analyzing Results

- Use gem5’s stats file (typically `m5out/stats.txt`) to collect metrics like **IPC** (Instructions per Cycle) and **latency**.
- Use `m5out/config.json` to confirm configuration settings.


### Optimization
```python
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

```

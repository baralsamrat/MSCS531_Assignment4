from m5.objects import *
from m5.util import addToPath
import m5
import sys

# Set up the system
system = System()
system.clk_domain = SrcClockDomain(clock='1GHz', voltage_domain=VoltageDomain())
system.mem_ranges = [AddrRange('512MB')]
system.membus = SystemXBar()

# Create CPU
system.cpu = AtomicSimpleCPU()

# Import necessary cache classes
system.cpu.icache = L1ICache(size='32kB')
system.cpu.dcache = L1DCache(size='32kB')

# Connect the CPU to the caches
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Connect the caches to the memory bus
system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)

# Create a workload
process = Process(pid=0)
process.executable = '/Users/labaik/Documents/GitHub/MSCS531_Assignment4/src/hello_world'  # Update with your actual path
system.cpu.workload = process
system.cpu.createThreads()

# Instantiate the system
root = Root(full_system=False, system=system)
m5.instantiate()

print("Running the simulation")
exit_event = m5.simulate()
print("Exiting @ tick {} because {}".format(m5.curTick(), exit_event.getCause()))

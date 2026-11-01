"""Read-only historical packages and new writable root."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
T2=(Path(__file__).resolve().parents[3] / 'experiments/phase_t2_structure_allocator_v02_20261031')
T1A=(Path(__file__).resolve().parents[3] / 'experiments/training_t1a_solver_gate_20261031')
T1B=(Path(__file__).resolve().parents[3] / 'experiments/training_t1b_planning_value_20261031')
if str(T2) not in sys.path:sys.path.insert(0,str(T2))
import t2.bootstrap

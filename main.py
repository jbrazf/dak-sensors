from pzem import read_all_pzem004tv3_registers
from sht35 import read_sht35

print(read_all_pzem004tv3_registers())
print(read_sht35())
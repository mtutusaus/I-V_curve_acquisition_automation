from pymeasure.instruments.keithley import Keithley2400
from time import sleep

# Keithley2400 (25): Applies constant Collector current and measures Collector-Emitter voltage
vce_gpib_address = "GPIB::25"
vce_source_current = 150e-3  # in Amps
vce_compliance_voltage = 2  # in Volts
vce_measure_nplc = 10  # Number of power line cycles
vce_measure_voltage_range = 2  # in Volts

# Keithley2400 (24): Applies constant Gate-Emitter voltage
vge_gpib_address = "GPIB::24"
vge_source_voltage = 15  # in V
vge_compliance_current = 1e-3  # in A

# Initialize, reset and config VCE SMU
smu_vce = Keithley2400(vce_gpib_address)
print("VCE SMU ID:", smu_vce.id)
smu_vce.reset()
smu_vce.use_front_terminals()
smu_vce.apply_current(vce_source_current, vce_compliance_voltage)
smu_vce.measure_voltage(vce_measure_nplc, vce_measure_voltage_range)
smu_vce.wires = 4

# Initialize, reset and config VGE SMU
smu_vge = Keithley2400(vge_gpib_address)
print("VGE SMU ID:", smu_vge.id)
smu_vge.reset()
smu_vge.use_front_terminals()
smu_vge.source_mode = "voltage"
smu_vge.source_voltage = vge_source_voltage
smu_vge.compliance_current = vge_compliance_current

sleep(0.5)  # Time for instruments to react

# First apply VGE and then IC
smu_vge.enable_source()
smu_vce.enable_source()
smu_vce.config_buffer(10)  # So it performs 10 measurements
smu_vce.source_current = vce_source_current
smu_vce.start_buffer()
smu_vce.wait_for_buffer()

# Read the mean voltage of 10 measurements
voltage = smu_vce.mean_voltage

# Calculate Tj from calibrated equation
# Tj = 357.351188877009-533.230356018299*voltage    # H40ER5S DEV 9
Tj = 357.090847511229-532.214573058354*voltage      # H40ER5S DEV 10
# Tj = 357.69782493429-533.886811196684*voltage     # H40ER5S DEV 11

print(f"Vce @ 150 mA = {voltage} V")
print(f"Tj = {Tj} °C")
smu_vce.beep(4000, 2)
# First disable IC and then VGE
smu_vce.disable_source()
smu_vge.disable_source()
# Clear status and SRQ to end measurement
smu_vce.write("*CLS")
smu_vce.write("*SRE 0")
smu_vge.write("*CLS")
smu_vge.write("*SRE 0")

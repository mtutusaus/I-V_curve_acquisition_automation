from pymeasure.instruments.keithley import Keithley2400
from time import sleep

# Set source_current and measure_voltage parameters
source_current = 10e-3  # in Amps
compliance_voltage = 2  # in Volts
measure_nplc = 10  # Number of power line cycles
measure_voltage_range = 2  # in Volts

# Connect and configure the instrument
smu = Keithley2400("GPIB::25")
print("ID:", smu.id)
smu.reset()
smu.use_front_terminals()
smu.apply_current(source_current, compliance_voltage)
smu.measure_voltage(measure_nplc, measure_voltage_range)
smu.wires = 4
sleep(0.5)
smu.enable_source()
smu.config_buffer(10) # So it performs 10 measurements
smu.source_current = source_current
smu.start_buffer()
smu.wait_for_buffer()

# Read the mean voltage of 10 measurements
voltage = smu.mean_voltage

# Calculate Tj from calibrated equation
# Tj = 357.351188877009-533.230356018299*voltage      # H40ER5S DEV 9
Tj = 357.090847511229-532.214573058354*voltage    # H40ER5S DEV 10
# Tj = 357.69782493429-533.886811196684*voltage     # H40ER5S DEV 11

print(f"Vce @ 10 mA ={voltage}V")
print(f"Tj = {Tj}°C")
smu.beep(4000, 2)
smu.disable_source()
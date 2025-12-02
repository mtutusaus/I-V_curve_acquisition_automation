# Import necessary packages
from pymeasure.instruments.keithley import Keithley2400
from time import sleep
import time
import sys


def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    percent = "{:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}', )
    sys.stdout.flush()
    if iteration == total:
        print()


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

measurement_duration = 15 * 60  # Total duration in seconds (15 minutes)
interval = 1  # Desired interval between measurements in seconds

# File variables
prefix = "temp_log"
temperature_filename = "70"
extension = "txt"
filename = f"{prefix}_{temperature_filename}.{extension}"

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

start_time = time.time()
# Open the file for writing
try:
    with open(filename, "w") as file:
        # Write header
        file.write("Time (s)\tTemperature (deg C)\tSetpoint (deg C)\n")

        elapsed_time = 0
        measurement_count = 0

        while elapsed_time < measurement_duration:
            # Measure voltage
            smu_vce.source_current = vce_source_current
            voltage = smu_vce.voltage
            # Tj = 357.351188877009-533.230356018299*voltage        # H40ER5S DEV 9
            Tj = 357.090847511229-532.214573058354*voltage          # H40ER5S DEV 10
            # Tj = 357.69782493429-533.886811196684*voltage         # H40ER5S DEV 11

            # Get the current timestamp relative to start_time
            timestamp = time.time() - start_time

            # Write data to the file
            file.write(f"{timestamp:.2f}\t{Tj:.6f}\t{temperature_filename}\n")
            measurement_count += 1
            print_progress_bar(measurement_count, measurement_duration // interval, prefix='Progress:', suffix='Complete', length=50)

            # Wait for the next measurement or until equipment is ready
            while time.time() - start_time < elapsed_time + interval:
                sleep(0.1)  # Short delay to avoid busy-waiting
            elapsed_time = time.time() - start_time

except KeyboardInterrupt:
    print("\nMeasurement stopped by the user.")

finally:
    total_time = time.time() - start_time
    minutes, seconds = divmod(total_time, 60)
    print("\n")
    print(f'Elapsed time: {int(minutes)} minutes and {seconds:.2f} seconds')
    smu_vce.beep(4000, 2)
    # First disable IC and then VGE
    smu_vce.disable_source()
    smu_vge.disable_source()

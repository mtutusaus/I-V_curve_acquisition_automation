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


# Set source_current and measure_voltage parameters
source_current = 10e-3  # in Amps
compliance_voltage = 2  # in Volts
measure_nplc = 10  # Number of power line cycles
measure_voltage_range = 2  # in Volts

measurement_duration = 15 * 60  # Total duration in seconds (15 minutes)
interval = 1  # Desired interval between measurements in seconds

# Variables
prefix = "temp_log"
temperature_filename = "170"
extension = "txt"

# Generate filename
filename = f"{prefix}_{temperature_filename}.{extension}"


# Connect and configure the instrument
smu = Keithley2400("GPIB::25")
smu.reset()
smu.use_front_terminals()
smu.apply_current(source_current, compliance_voltage)
smu.measure_voltage(measure_nplc, measure_voltage_range)
smu.wires = 4
sleep(0.1)  # Wait here to give the instrument time to react
smu.enable_source()

# Open the file for writing
start_time = time.time()

try:
    with open(filename, "w") as file:
        # Write header
        file.write("Time (s)\tTemperature (deg C)\tSetpoint (deg C)\n")

        elapsed_time = 0
        measurement_count = 0

        while elapsed_time < measurement_duration:
            # Measure voltage
            smu.source_current = source_current
            voltage = smu.voltage
            # Tj = 357.351188877009 - 533.230356018299 * voltage    # H40ER5S DEV 9
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
    smu.beep(4000, 2)
    smu.disable_source()

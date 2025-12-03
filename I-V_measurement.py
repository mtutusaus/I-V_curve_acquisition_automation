from tek371 import Tek371
import pyvisa
from pymeasure.instruments.keithley import Keithley2400
from time import sleep
import warnings
import os
import csv

# Suppress only the specific PyVISA warning
warnings.filterwarnings("ignore", message="read string doesn't end with termination characters")


# TEK371 constants
tek371_gpib_address = "GPIB0::23::INSTR"
tek371_horizontal_scale = 200E-3  # in V/DIV
tek371_vertical_scale = 5  # in A/DIV
tek371_vce_percentage = 100.0  # in %

# Keithley2400 constants
smu_gpib_address = "GPIB::24"
smu_source_voltage = 20  # in V
smu_compliance_current = 1e-3  # in A

# Device under test constants
folder = "E:/Miquel_Tutu/H40ER5S/H40ER5S_dev10_2025-12-01"
DUT = "H40ER5S"
dev = "dev10"
vge_applied = "20"
temperature_applied = "120"
file = f"{DUT}_{dev}_{vge_applied}V_{temperature_applied}C"
number_of_curves = 10


def compute_mean_file(folder_path: str, base_name: str, N: int):
    """
    Compute per-row mean of Voltage and Current across N files:
    {folder}/{base_name}_1.csv ... {folder}/{base_name}_{N}.csv
    Save result as {folder}/{base_name}_MEAN.csv.
    """
    filepaths = [os.path.join(folder_path, f"{base_name}_{i}.csv") for i in range(1, N + 1)]
    rows_list = []

    # Read all files into memory
    for path in filepaths:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows_list.append(list(reader))

    # Compute means (skip header)
    header = rows_list[0][0]
    num_rows = len(rows_list[0])  # should be 257
    mean_rows = [header]  # Set first row of mean CSV file to have the same header

    for r in range(1, num_rows):
        values_v = [float(rows_list[i][r][0]) for i in range(N)]  # Voltage values across all files
        values_i = [float(rows_list[i][r][1]) for i in range(N)]  # Current values across all files
        mean_v = sum(values_v) / N
        mean_i = sum(values_i) / N
        mean_rows.append([mean_v, mean_i])

    # Create 'mean' subfolder if it doesn't exist
    mean_folder = os.path.join(folder_path, "mean")
    os.makedirs(mean_folder, exist_ok=True)

    # Save mean file in the subfolder
    out_path = os.path.join(mean_folder, f"{base_name}_MEAN.csv")
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(mean_rows)

    print(f"Mean file written: {out_path}")


def main():
    # Scan GPIB bus for all connected devices (useful to be sure the PC is connected to the right bus...)
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    print("GPIB SCAN")
    for r in resources:
        if "GPIB" in r:
            print("  ", r)

    print("-" * 50)
    print("CONNECTED DEVICES")

    # Initialize, reset and config SMU
    smu = Keithley2400(smu_gpib_address)
    print(f"SMU connected at address {smu_gpib_address.split('::')[1]}: {smu.id}")
    smu.reset()
    # SMU is only applying voltage, not measuring, so no need for SRQ
    smu.write("*CLS")  # Clear status
    smu.write("*SRE 0")  # Disable SRQ
    smu.use_front_terminals()
    smu.source_mode = "voltage"
    smu.source_voltage = smu_source_voltage
    smu.compliance_current = smu_compliance_current
    sleep(0.5)

    # Initialize, reset and config tracer
    tek = Tek371(tek371_gpib_address)
    print(f"Tracer connected at address {tek371_gpib_address.split('::')[1]}: {tek.id_string()}")
    print("-" * 50)
    tek.initialize()
    tek.set_peak_power(300)
    # Step generator is not used, set to minimum
    tek.set_step_number(0)
    tek.set_step_voltage(200e-3)
    tek.set_step_offset(0)
    tek.enable_srq_event()
    tek.set_horizontal("COL", tek371_horizontal_scale)  # 200 mV/div
    tek.set_vertical(tek371_vertical_scale)  # 5 A/div
    print("\nCRT SETTINGS")
    print(f"  Horizontal scale set to: {tek.get_horizontal().split(':')[1]} V/DIV")
    print(f"  Vertical scale set to: {tek.get_vertical().split(':')[1]} A/DIV\n")
    tek.set_display_mode("STO")
    sleep(0.5)

    print("START OF MEASUREMENT")
    print("-" * 50)
    smu.enable_source()
    for i in range(1, number_of_curves+1):
        print(f"CURVE {i}/{number_of_curves}")
        # Set Collector Supply to desired %
        tek.set_collector_supply(tek371_vce_percentage)
        print(f"  Collector supply set to: {tek.get_collector_supply().split()[-1]} %")

        # Set measurement mode to sweep
        tek.set_measurement_mode("SWE")

        # Start the sweep
        print(f"  Starting sweep number {i}/{number_of_curves}...")
        if tek.wait_for_srq(timeout_s=60.0):
            print(f"  Sweep {i}/{number_of_curves} finished!")
        else:
            raise TimeoutError(f"  Sweep {i}/{number_of_curves} did not complete within timeout")

        # Read curve and save to CSV
        filename = f"{folder}/{file}_{i}.csv"
        tek.read_curve(filename)
        print("-" * 50)

        # Reset SRQ for new sweep
        tek.discard_and_disable_all_events()
        tek.enable_srq_event()

    smu.disable_source()
    smu.beep(4000, 2)
    tek.disable_srq_event()
    tek.close()
    print("I-V curves acquisition done!\n")
    print("Processing mean I-V file...")
    # After all curves are saved, compute the mean file
    compute_mean_file(folder, file, number_of_curves)
    print("\nScript finished.")


if __name__ == "__main__":
    main()

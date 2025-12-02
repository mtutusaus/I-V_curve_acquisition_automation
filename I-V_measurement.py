from tek371 import Tek371
import pyvisa
from pymeasure.instruments.keithley import Keithley2400
from time import sleep
import warnings

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
temperature_applied = "60"
file = f"{DUT}_{dev}_{vge_applied}V_{temperature_applied}C"
number_of_curves = 10


def main():

    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    print("GPIB SCAN")
    for r in resources:
        if "GPIB" in r:
            print("  ", r)

    # Initialize, reset and config SMU
    smu = Keithley2400(smu_gpib_address)
    print("-" * 50)
    print("CONNECTED DEVICES")
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
    tek.set_step_number(0)
    tek.set_step_voltage(5)
    tek.set_step_offset(4)
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
    print("Done")


if __name__ == "__main__":
    main()

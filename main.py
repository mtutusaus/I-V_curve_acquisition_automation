from tek371 import Tek371
from pymeasure.instruments.keithley import Keithley2400
from time import sleep

# TEK371 constants
tek371_gpib_address = "GPIB0::23::INSTR"
tek371_horizontal_scale = 200e-3 # in V/DIV
tek371_vertical_scale = 5 # in A/DIV
tek371_vce_percentage = 100.0 # in %

# Keithley2400 constants
smu_gpib_address = "GPIB::25"
smu_source_voltage = 15 # in V
smu_compliance_current = 1e-3 # in A

# Device under test constants
DUT = "IGBT_dev1"
number_of_curves = 10
folder = "Data/"


def main():
    # Initialize, reset and config SMU
    smu = Keithley2400(smu_gpib_address)
    print("SMU connected:", smu.id)
    smu.reset()
    smu.use_front_terminals()
    smu.source_mode = "voltage"
    smu.source_voltage = smu_source_voltage
    smu.compliance_current = smu_compliance_current
    sleep(0.5)

    # Initialize, reset and config tracer
    tek = Tek371(tek371_gpib_address)
    print("Tracer connected:", tek.id_string())
    tek.initialize()
    tek.set_peak_power(300)
    tek.set_step_number(0)
    tek.set_step_voltage(200e-3)
    tek.set_step_offset(0)
    tek.enable_srq_event()
    tek.set_horizontal("COL", tek371_horizontal_scale)  # 200 mV/div
    tek.set_vertical(tek371_vertical_scale)  # 5 A/div
    print("CRT screen settings")
    print(f"Horizontal scale set to: {tek.get_horizontal().split(':')[1]} V/DIV")
    print(f"Vertical scale set to: {tek.get_vertical().split(':')[1]} A/DIV")
    tek.set_display_mode("STO")
    sleep(0.5)

    smu.enable_source()
    for i in range(1, number_of_curves+1):
        # Set Collector Supply to desired %
        tek.set_collector_supply(tek371_vce_percentage)
        print(f"Collector supply set to: {tek.get_collector_supply().split()[-1]} %")

        # Set measurement mode to sweep
        tek.set_measurement_mode("SWE")

        # Start the sweep
        print(f"Starting sweep number {i}/{number_of_curves}...")
        if tek.wait_for_srq(timeout_s=60.0):
            print(f"Sweep {i}/{number_of_curves} finished!")
        else:
            raise TimeoutError(f"Sweep {i}/{number_of_curves} did not complete within timeout")

        # Read curve and save to CSV
        filename = f"{folder}/I-V_{DUT}_{i}.csv"
        tek.read_curve(filename)
        print("---------")

        # Reset SRQ for new sweep
        tek.discard_and_disable_all_events()
        tek.enable_srq_event()

    smu.disable_source()
    tek.disable_srq_event()
    tek.close()
    print("Done")


if __name__ == "__main__":
    main()

# I-V curve automated acquisition

## Overview
This project automates the acquisition of experimental I-V curves of MOS gated power devices measured with a Tektronix TEK371 high power curve tracer. The Gate-Source (Emitter) voltage is applied with a Keitlhey 2400 Sourcemeter unit. The curve tracer is controlled using the [tek371](https://github.com/mtutusaus/tek371-driver) driver, and the SMU using its dedicated [PyMeasure](https://github.com/pymeasure/pymeasure) driver.

---

## Requirements
- Python 3.10 (not tested with other versions)
- [PyVISA](https://pyvisa.readthedocs.io/)
- [PyMeasure](https://github.com/pymeasure/pymeasure)
- GPIB interface (e.g., NI GPIB-USB adapter)
---

## Usage
The scripts are intended to be used as follows:
1. [`Tj_heating-period_measurement`](Tj_heating-period_measurement.py): The hot plate used to set the junction temperature has a settling time of 15 minutes, this script performs a measurement of the internal junction temperature of the DUT through the calibrated offline TSEP every second, and records everything into a txt file. It is not mandatory to use, but recommended to not exceed the heating time, specially at high temperatures as it may degrade the device under test.
2. [`Tj_single_measurement`](Tj_single_measurement.py): Performs 10 consecutive junction temperature measurements and returns the mean value. This would be the junction temperature the device is when measuring the I-V curves.
3. [`I-V_measurement`](I-V_measurement.py): Performs any number of consecutive I-V curves at specific conditions, saves all the curve files separately on the provided location.
---
## **License**
This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit
- **NonCommercial** — You may not use the material for commercial purposes
- **ShareAlike** — Derivatives must use the same license

See the [LICENSE](LICENSE) file for the full license text.

## Acknowledgments

- M365 Copilot (Microsoft) for development assistance

## Author

[Miquel Tutusaus](https://github.com/mtutusaus), 2025

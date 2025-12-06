# I-V curve automated acquisition

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PyVISA](https://img.shields.io/badge/instrument-PyVISA-blue.svg)
![PyMeasure](https://img.shields.io/badge/instrument-PyMeasure-green.svg)
![AI-Assisted](https://img.shields.io/badge/Development-AI--Assisted-purple)
[![License: CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## **Overview**
This project automates the acquisition of I-V curves of MOS gated power devices measured with a **Tektronix TEK371** high power curve tracer at different junction temperatures set by a hot plate. The Gate-Source (Emitter) voltage is applied with a **Keitlhey 2400** SMU. The curve tracer is controlled using the [tek371](https://github.com/mtutusaus/tek371-driver) driver, and the SMU using its dedicated [PyMeasure](https://github.com/pymeasure/pymeasure) driver.

---
## **Requirements**
- Python 3.10 (not tested with other versions)
- [PyVISA](https://pyvisa.readthedocs.io/)
- [PyMeasure](https://github.com/pymeasure/pymeasure)
- GPIB interface (e.g., NI GPIB-USB adapter)
---

## **Usage**
The scripts are intended to be used as follows:
1. [`Tj_heating-period_measurement`](Tj_heating-period_measurement.py): The hot plate used to set the junction temperature has a settling time of 15 minutes, this script performs a measurement of the internal junction temperature of the DUT through the calibrated offline TSEP every second, and records everything into a txt file. It is not mandatory to use, but recommended to not exceed the heating time, specially at high temperatures as it may degrade the device under test.
2. [`Tj_single_measurement`](Tj_single_measurement.py): Performs 10 consecutive junction temperature measurements and returns the mean value. This would be the junction temperature the device is when measuring the I-V curves.
3. [`I-V_measurement`](I-V_measurement.py): Performs any number of consecutive I-V curves at specific conditions, saves all the curve files separately on the provided location. Computes the mean of all measurements and saves it into a separate folder within the same directory.
4. [`I-V single`](I-V_single.py): Performs any number of consecutive single measurements at specific conditions, saves all the curve files separately on the provided location. Computes the mean of all measurements and saves it into a separate folder within the same directory.

---
## **Related Projects**

This project is built on top of:
- [tek371-driver](https://github.com/mtutusaus/tek371-driver) - Low-level Tektronix 371 communication driver

---
## **Development**

- This project is developed with AI assistance (M365 Copilot) for code suggestions, debugging, and optimization.

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

---
## **Author**

[Miquel Tutusaus](https://github.com/mtutusaus), 2025

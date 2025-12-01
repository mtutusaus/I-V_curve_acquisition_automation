# I-V curve automated acquisition

## Overview
This project automates the acquisition of experimental I-V curves of MOS gated power devices measured with a Tektronix TEK371 high power curve tracer. The Gate-Source (Emitter) voltage is applied with a Keitlhey 2400 Sourcemeter unit. The curve tracer is controlled using the [tek371](https://github.com/mtutusaus/tek371-driver) driver, and the SMU using its dedicated [PyMeasure](https://github.com/pymeasure/pymeasure) driver.

---

## Requirements
- Python 3.10 (not tested with other versions)
- [PyVISA](https://pyvisa.readthedocs.io/)
- [PyMeasure](https://github.com/pymeasure/pymeasure)
- GPIB interface (e.g., NI GPIB-USB adapter)

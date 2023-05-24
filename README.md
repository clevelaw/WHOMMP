W.H.O.M.M.P. – William’s Home Office Metabolic Monitoring Program
W.H.O.M.M.P. is a Python-based GUI utilizing Tkinter and Matplotlib libraries that allows monitoring and visualization of health parameters centered around a stationary bike. The program utilizes an Arduino as a data acquisition system. Real-time data is collected for the following parameters:
•	Pedal revolutions: A built in cadence sensor was rewired to send a signal straight to the Arduino instead the bikes built in 7 segment display
•	CO2 concentration: MQ-135 sensor to measure CO2 concentrations in the air
•	IR and Red Light Absorbance: MAX30102 Pulse + Oximeter sensor emits IR and Red Light that can then be collected and used to determine pulse and blood oxygen saturation. The sensor has recommended software but after testing this was found to be fairly inaccurate and slow
•	Air pressure sensor: for future use in measuring respiratory parameters
•	Temperature: Basic thermistor calibrated for physiological temperatures
•	SpO2: Calculates the blood oxygen saturation level.
Derived parameters:
•	Heart rate: derived from the red light absorbance data
•	Speed: derived from the cadence sensor
•	Distance: derived from the cadence sensor, 1 revolution = 0.0038miles
•	Blood Oxygen saturation: derived from IR and Red light absorbance, algorithm for determining was based on this paper <LINK>(Yosef et al 2018)
Prerequisites
•	Python 3.x
•	Arduino microcontroller
•	Arduino IDE
•	Required libraries (serial, time, datetime, tkinter, collections, threading, re, matplotlib)
Running the program
After installing all the required modules, the code is run from a single file and runs continuously until stopped. A more general purpose data acquisition program is also available that displays only the raw data collected from the Arduino with no data processing and can be repurposed as needed.
Arduino Code
The Arduino code is responsible only for the data collection. Some sensors included built in libraries but all data was collected raw to be analyzed live in the python code.
Future Improvements
The project was initially conceived as a method of measuring several metabolic parameters during exercise. This would include calorimetry, capnography, and the more basic data associated with a stationary bike. Currently, the biggest limitations with the setup are the sensors used for data acquisition. The CO2 sensor is designed for monitoring atmospheric CO2 and as a result does not have the resolution needed to measure live respiratory data for each inhalation/exhalation. A replacement sensor would be a NDIR sensor which could acquire capnography data sufficient for this purpose but are significantly more expensive (~$400). Oxygen sensors are also a viable alternative but again at a higher price than the CO2 sensors.
License
This project is licensed under the MIT License.

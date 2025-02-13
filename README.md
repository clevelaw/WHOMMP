# **W.H.O.M.M.P. – William’s Home Office Metabolic Monitoring Program**
W.H.O.M.M.P. is a Python-based GUI utilizing Tkinter and Matplotlib libraries that allows monitoring and visualization of health parameters centered around a stationary bike. The program utilizes an Arduino as a data acquisition system with several different sensors used for collecting data. This includes a hall-effect sensor to for the bike pedals, an MQ135 sensor for expired CO2, a MAX30105 for pulse oximetry and heart rate, a MPS20N0040D for air pressure, and a thermistor for body temperature. 

  ![whommp_running](https://github.com/user-attachments/assets/ffd89a9c-31ff-4241-8131-00e553b0837a)

## **Collected data**
**Pedal revolutions:** used to derive distance traveled and speed  
**CO2 concentration:** Measures exhaled CO2   
**IR and Red Light Absorbance:** used to collect IR and Red Light absorbance on the skin that can then be used to determine pulse and blood oxygen saturation
**Air pressure sensor:** for future use in measuring respiratory parameters
**Temperature:** Basic thermistor calibrated for physiological temperatures

## **Derived parameters:**

**Heart rate:** derived from the red light absorbance data.  
**Speed:** derived from the cadence sensor.  
**Distance:** derived from the cadence sensor, 1 revolution = 0.0038 miles.  
**Blood Oxygen saturation:** derived from IR and Red light absorbance, the algorithm for determining was based on this paper [Yosef et al 2018](https://pubmed.ncbi.nlm.nih.gov/30326552/)

## **Prerequisites**
Python 3.
Arduino microcontroller  
Running the program  
After installing all the required modules, the code is run from a single file and runs continuously until stopped. A more general-purpose data acquisition program is also available that displays only the raw data collected from the Arduino with no data processing and can be repurposed as needed.  

## **Arduino Code**  
The Arduino code is responsible only for the data collection. Some sensors included built-in libraries, but all data was collected raw to be analyzed live in the Python code.

## **Future Improvements**  
The project was initially conceived as a method of measuring several metabolic parameters during exercise. This would include calorimetry, capnography, and the more basic data associated with a stationary bike. Currently, the biggest limitations with the setup are the sensors used for data acquisition. The CO2 sensor is designed for monitoring atmospheric CO2 and as a result does not have the resolution needed to measure live respiratory data for each inhalation/exhalation. A replacement sensor would be an NDIR sensor, which could acquire capnography data sufficient for this purpose but is significantly more expensive (~$400). Oxygen sensors are also a viable alternative but again at a higher price than the CO2 sensors.

**License**  
This project is licensed under the MIT License.

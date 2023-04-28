import serial
import time
import datetime as dt
import tkinter as tk
from collections import deque
import threading
import re
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker

NBLUE = '#006FFF'
NCYAN = '#13F4EF'
NGREEN = '#68FF00'
NYELLOW = '#FAFF00'
NRED = '#FF005C'
NORANGE = '#FF6600'
NPINK = '#FF00FF'
NPURPLE = '#9D00FF'

try:
    print("Connecting to arduino")
    arduino = serial.Serial('COM3', 19200)
    throw_away = arduino.readline().decode().strip()
    print("Connected to arduino")
except:
    print("Port not found!")

def arduino_multi_signal(ard_input):
    data = ard_input.readline().decode().strip()
    ard_list = re.findall(r"[-+]?\d*\.\d+|\d+", data)
    return ard_list

class Example(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.current_time = dt.datetime.now()
        time_fmt = mdates.DateFormatter('%S')
        start_time = self.current_time - dt.timedelta(seconds=50)  # subtract 50 seconds to get the start time
        self.time_array = [start_time + dt.timedelta(seconds=(i*0.1)) for i in range(500)] # empty array, current time starts at [-1]
        self.config(bg='#000000') #top ribbon color
        self.data_range = 500
        self.x_data = [0 + i for i in range(self.data_range)]
        self.y_data = [0 for i in range(self.data_range)]
        self.y_data2 = [0 for i in range(self.data_range)]
        self.y_data3 = [0 for i in range(self.data_range)]
        self.y_data4 = [0 for i in range(self.data_range)]
        self.y_data5 = [0 for i in range(self.data_range)]
        self.y_data6 = [0 for i in range(self.data_range)]
        self.y_data7 = [0 for i in range(self.data_range)]
        self.y_data8 = [0 for i in range(self.data_range)]
        self.y_data9 = [0 for i in range(self.data_range)]
        self.figure = Figure(figsize=(13, 6), dpi=100, facecolor='#000000')
        self.figure.subplots_adjust(left=0.05,
                                    bottom=0.05,
                                    right=0.95,
                                    top=0.95,
                                    wspace=0.2,
                                    hspace=0.4)
        # graphs
        self.ax1, self.plot1 = self.create_graph(time_fmt, 331, self.time_array, self.y_data, (0, 0.1), NBLUE, "Distance", "Miles")
        self.ax2, self.plot2 = self.create_graph(time_fmt, 332, self.time_array, self.y_data2, (0, 25), NCYAN, "Speed", "M/H")
        self.ax3, self.plot3 = self.create_graph(time_fmt, 339, self.time_array, self.y_data3, (150, 800), NGREEN, "Gas", "unitz")
        self.ax4, self.plot4 = self.create_graph(time_fmt, 334, self.time_array, self.y_data4, (0, 200), NYELLOW, "Heart Rate", 'BPM')
        #graph with 2 y-axis
        self.ax5, self.plot5, self.plot55 = self.double_graph(time_fmt, 336, self.time_array, self.y_data5, self.y_data9, (0, 0.1), 'white', 'IR Wave', "AU", "AU")
        self.ax6, self.plot6 = self.create_graph(time_fmt, 337, self.time_array, self.y_data6, (0, 0.1), NPINK, 'Pressure', "kPa")
        self.ax7, self.plot7 = self.create_graph(time_fmt, 338, self.time_array, self.y_data7, (0, 0.1), NPURPLE, 'Temp', "deg")
        self.ax8, self.plot8 = self.create_graph(time_fmt, 335, self.time_array, self.y_data8, (0, 0.1), NORANGE, 'Sp02', "%")
        #self.ax1.xaxis.set_visible(False)

        #plot area to place static/dynamic text
        fs = 15
        self.textarea = self.figure.add_subplot(236)
        self.textarea.axis('off')
        self.ax1_text = self.textarea.text(0, 1200, '', fontsize=fs, ha='left', va='top', color=NBLUE, backgroundcolor='black')
        self.ax2_text = self.textarea.text(0.6, 1200, '', fontsize=fs, ha='left', va='top', color=NCYAN, backgroundcolor='black')
        self.ax9_text = self.textarea.text(0.3, 1150, '', fontsize=fs, ha='left', va='top', color=NRED, backgroundcolor='black')
        self.ax4_text = self.textarea.text(0, 1100, '', fontsize=fs, ha='left', va='top', color=NYELLOW, backgroundcolor='black')
        self.ax8_text = self.textarea.text(0.6, 1100, '', fontsize=fs, ha='left', va='top', color=NORANGE, backgroundcolor='black')
        self.ax6_text = self.textarea.text(0, 1000, '', fontsize=fs, ha='left', va='top', color=NPINK, backgroundcolor='black')
        self.ax7_text = self.textarea.text(0.3, 950, '', fontsize=fs, ha='left', va='top', color=NPURPLE, backgroundcolor='black')
        self.ax3_text = self.textarea.text(0.6, 1000, '', fontsize=fs, ha='left', va='top', color=NGREEN, backgroundcolor='black')

        """
        testing text location
        self.textarea.text(0, 0, '<0,0', fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(1, 0, '<1,0', fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 1200, '<0,1200' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(1, 1200, '<1,1200' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 1200, '0,1200r>' , fontsize=fs, ha='right', va='top', color=NYELLOW)
        self.textarea.text(0, 600, '<0,600' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 300, '<0,300' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 880, '0,880r>' , fontsize=fs, ha='right', va='top', color=NYELLOW)
        self.textarea.text(0.5, 1200, '<0.5,1200' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        """

        label = tk.Label(self, text="W.H.O.M.M.P.", fg=NGREEN, bg='#000000', font=20)
        label.pack(pady=10, padx=10)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.timer = 0
        self.ir_timer = 0
        self.rotations = 1
        self.previous = 0
        self.speed = 0
        self.distance = 0
        self.start = time.time()
        self.speed_arr = deque([[self.start,1]])
        self.beat = 0
        self.hr = 0
        self.update_plot()

    def graph_info(self, xdata, ydata, xformat, location, ylimits, line_color, y_units, title):
        graph_dict = {
            "xdata": xdata,
            "ydata": ydata,
            "xformat": xformat,
            "location": location,
            "ylimits": ylimits,
            "line_color": line_color,
            "y_units": y_units,
            "title": title
        }
        return graph_dict

    def create_graph(self, xformat, location, xdata, ydata, ylim, line_color, dataname, units):
        gname = self.figure.add_subplot(location)
        gname.xaxis.set_major_formatter(xformat)
        graph = gname.plot(xdata, ydata, label=dataname, color=line_color)[0]
        gname.set_ylim(ylim[0], ylim[1])
        gname.set_xlim(self.x_data[0], self.x_data[-1])
        gname.set_facecolor('black')
        gname.set_title(dataname, color=line_color)
        gname.set_ylabel(units, color=line_color)
        gname.tick_params(axis='both', color=line_color, labelcolor=line_color)
        return gname, graph

    def double_graph(self, xformat, location, xdata, ydata, y2_data, ylim, line_color, dataname, units, units2):
        gname = self.figure.add_subplot(location)
        graph1 = gname.plot(xdata, ydata, label=dataname, color=line_color)[0]
        gname.set_ylim(ylim[0], ylim[1])
        gname.set_xlim(self.x_data[0], self.x_data[-1])
        gname.set_facecolor('black')
        gname.set_title(dataname, color=line_color)
        gname.set_ylabel(units, color=line_color)
        gname.tick_params(axis='x', labelcolor=line_color)
        gname.tick_params(axis='y', labelcolor=line_color)
        # 2nd y-axis
        gname2 = gname.twinx()
        graph2 = gname2.plot(xdata, y2_data, label=dataname, color='red')[0]
        gname2.set_ylim(25_000, 29_000)
        gname2.set_ylabel(units2)
        gname2.xaxis.set_major_formatter(xformat)
        gname2.tick_params(axis='y', labelcolor='red')

        return gname, graph1, graph2

    def calc_params(self, index1, index2):
        self.distance = self.rotations * 0.0038
        self.rot_dif = self.speed_arr[index1][1] - self.speed_arr[index2][1] ##################################################always 1
        self.time_dif = self.speed_arr[index1][0] - self.speed_arr[index2][0]

        speed_num = 8                      # 8 decided on arbitrarily
        if len(self.speed_arr) > speed_num:
            dt = [self.speed_arr[-1][0] - self.speed_arr[-i][0] for i in range(2, speed_num)]
            avg_pedal = [(num / (idx + 1)) for idx, num in enumerate(dt)]
            self.speed = 0.0038 / ((sum(avg_pedal) / len(avg_pedal)) / 3600)
        else:
            if self.time_dif == 0:
                self.speed = 0
            else:
                self.speed = (self.rot_dif * 0.0038) / self.time_dif * 3600

    def wave_calc(self, data):
        self.ir_timer += 1
        if self.ir_timer > 50:
            self.ir_timer = 0
            peaks = 0
            for i in range(400, 490):
                if data[i] > data[i - 1] and data[i] > data[i - 2] \
                        and data[i] > data[i + 1] and data[i] > data[i + 2]:
                    peaks += 1
            tick = self.time_array[490] - self.time_array[400]
            self.hr = (60/tick.total_seconds()) * peaks

    def update_plot(self):
        if self.timer >= 100:
            self.timer = 0
        self.timer += 1
        in_signal = arduino_multi_signal(arduino)
        #in_signal = [0, 1, 2, 3, 70000, 28000, 6, 7, 8, 9]
        # [a0, a1, a2, a3, IR, Red, BPM, AvgBPM, SP02, ?Finger]###################
        # 20:57:08.044 -> MQA: 236 MQB: 151 MQC: 15 MQD: 54 IR:1152 Red: 271 BPM: 4.01 AvgBPM: 0 Sat: 99 temperatureF: 89.4875: No_finger

        bike_signal = int(in_signal[0])
        gas1 = int(in_signal[1])
        ir_wave = int(float(in_signal[4]))
        red_wave = int(float(in_signal[5]))
        pressure = int(float(in_signal[2]))
        temperature = int(float(in_signal[9]))
        sat = int(float(in_signal[8]))
        print(in_signal)
        ############gas1 = -45.06*ratio*ratio+30.354*ratio+94.845

        if bike_signal - self.previous > 200:
            self.rotations += 1
            self.speed_arr.append([time.time(), self.rotations])
            if len(self.speed_arr) > 10:
                self.speed_arr.popleft()
        self.previous = bike_signal

        pedals = len(self.speed_arr)
        if pedals > 1:
            self.calc_params(pedals - 1, pedals - 2)
        else:
            self.rot_dif = 0
            self.time_dif = 0

        # update the x-axis
        self.x_data.append(self.x_data[-1] + 1)
        self.x_data.pop(0)

        self.time_array.append(dt.datetime.now())
        self.time_array.pop(0)

        # distance
        self.y_data.append(self.distance)
        self.y_data.pop(0)
        self.plot1.set_xdata(self.time_array)
        self.plot1.set_ydata(self.y_data)
        self.ax1.set_xlim(self.time_array[0], self.time_array[-1])
        self.ax1.set_ylim(min(self.y_data) , max(self.y_data)+0.1)

        # speed
        self.y_data2.append(self.speed)
        self.y_data2.pop(0)
        self.plot2.set_xdata(self.time_array)
        self.plot2.set_ydata(self.y_data2)
        self.ax2.set_xlim(self.time_array[0], self.time_array[-1])

        # gas
        self.y_data3.append(gas1)
        self.y_data3.pop(0)
        self.plot3.set_xdata(self.time_array)
        self.plot3.set_ydata(self.y_data3)
        self.ax3.set_xlim(self.time_array[0], self.time_array[-1])
        self.ax3.set_ylim(min(self.y_data3) - 15, max(self.y_data3) + 15)

        # heart rate
        self.y_data4.append(self.hr)
        self.y_data4.pop(0)
        self.plot4.set_xdata(self.time_array)
        self.plot4.set_ydata(self.y_data4)
        self.ax4.set_xlim(self.time_array[0], self.time_array[-1])
        self.ax4.set_ylim(0, 200)

        # IR/Red wavelengths
        self.y_data5.append(ir_wave)
        self.y_data5.pop(0)
        if ir_wave > 80000:
            self.wave_calc(self.y_data5)
        else:
            self.hr = 0

        self.plot5.set_xdata(self.time_array)
        self.plot5.set_ydata(self.y_data5)
        self.ax5.set_xlim(self.time_array[0], self.time_array[-1])
        self.ax5.set_ylim(min(self.y_data5) - 1000, max(self.y_data5) + 1000)
        self.y_data9.append(red_wave) # part 2
        self.y_data9.pop(0)
        self.plot55.set_xdata(self.time_array)
        self.plot55.set_ydata(self.y_data9)

        # Pressure
        self.y_data6.append(pressure)
        self.y_data6.pop(0)
        self.plot6.set_xdata(self.time_array)
        self.plot6.set_ydata(self.y_data6)
        self.ax6.set_xlim(self.time_array[0], self.time_array[-1])
        self.ax6.set_ylim(min(self.y_data6)-5, max(self.y_data6)+5)

        # Temperature
        self.y_data7.append(temperature)
        self.y_data7.pop(0)
        self.plot7.set_xdata(self.time_array)
        self.plot7.set_ydata(self.y_data7)
        self.ax7.set_xlim(self.time_array[0], self.time_array[-1])
        self.ax7.set_ylim(70, 105)

        # Pulse Ox
        self.y_data8.append(sat)
        self.y_data8.pop(0)
        self.plot8.set_xdata(self.time_array)
        self.plot8.set_ydata(self.y_data8)
        self.ax8.set_xlim(self.time_array[0], self.time_array[-1])
        self.ax8.set_ylim(80, 105)

        # Text box
        self.textarea.set_ylim(0, 500)
        self.ax1_text.set_text(f"Distance:{self.distance: .2f}mi")
        self.ax2_text.set_text(f"Speed:{self.speed: .2f}mph")
        self.ax3_text.set_text(f"{gas1: .1f}gas")
        self.ax4_text.set_text(f"HR:{self.hr: 0.0f}bpm")
        self.ax6_text.set_text(f"{pressure: .2f}kpa")
        self.ax7_text.set_text(f"{temperature: .2f}\N{DEGREE SIGN}F")
        self.ax8_text.set_text(f"{sat: .2f}%")
        current = self.time_array[-1] - self.current_time
        self.ax9_text.set_text(f"Elapsed: {str(current).split('.')[0]}")

        self.canvas.draw_idle()  # redraw plot
        threading.Timer(0.001, self.update_plot).start()

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

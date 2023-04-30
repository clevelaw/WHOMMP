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

class WHOMMPGUI(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.current_time = dt.datetime.now()
        time_fmt = mdates.DateFormatter('%S')
        self.data_range = 500
        start_time = self.current_time - dt.timedelta(seconds=50)  # subtract 50 seconds to get the start time
        self.time_array = [start_time + dt.timedelta(seconds=(i * 0.1)) for i in
                           range(self.data_range)]  # empty array, current time starts at [-1]
        self.config(bg='#000000')  # top ribbon color
        label = tk.Label(self, text="W.H.O.M.M.P.", fg=NGREEN, bg='#000000', font=20)
        label.pack(pady=10, padx=10)
        self.figure = Figure(figsize=(13, 6), dpi=100, facecolor='#000000')
        self.figure.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.2,  hspace=0.4)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # creating arrays to store data
        self.x_data = [0 + i for i in range(self.data_range)]
        self.data_distance = [0 for i in range(self.data_range)]
        self.data_speed = [0 for i in range(self.data_range)]
        self.data_gas = [0 for i in range(self.data_range)]
        self.data_hr = [0 for i in range(self.data_range)]
        self.data_ir_wave = [0 for i in range(self.data_range)]
        self.data_pressure = [0 for i in range(self.data_range)]
        self.data_temperature = [0 for i in range(self.data_range)]
        self.data_sat = [0 for i in range(self.data_range)]
        self.data_red_wave = [0 for i in range(self.data_range)]

        # creating the graphs and axes for each input
        self.ax_distance, self.plot_distance = self.create_graph(time_fmt, 331, self.time_array, self.data_distance, (0, 0.1), NBLUE,
                                                 "Distance", "Miles")
        self.ax_speed, self.plot_speed = self.create_graph(time_fmt, 332, self.time_array, self.data_speed, (0, 25), NCYAN,
                                                 "Speed", "M/H")
        self.ax_gas, self.plot_gas = self.create_graph(time_fmt, 339, self.time_array, self.data_gas, (150, 800), NGREEN,
                                                 "Gas", "unitz")
        self.ax_hr, self.plot_hr = self.create_graph(time_fmt, 334, self.time_array, self.data_hr, (0, 200), NYELLOW,
                                                 "Heart Rate", 'BPM')
        # graph with 2 y-axis
        self.ax_ir_wave, self.plot_ir_wave, self.plot_red_wave = self.double_graph(time_fmt, 336, self.time_array, self.data_ir_wave,
                                                              self.data_red_wave, (0, 0.1), 'white', 'IR Wave', "AU", "AU")
        self.ax_pressure, self.plot_pressure = self.create_graph(time_fmt, 337, self.time_array, self.data_pressure, (0, 0.1), NPINK,
                                                 'Pressure', "kPa")
        self.ax_temperature, self.plot_temperature = self.create_graph(time_fmt, 338, self.time_array, self.data_temperature, (0, 0.1), NPURPLE,
                                                 'Temp', "deg")
        self.ax_sat, self.plot_sat = self.create_graph(time_fmt, 335, self.time_array, self.data_sat, (0, 0.1), NORANGE,
                                                 'Sp02', "%")

        # plot area to place static/dynamic text
        fs = 15
        self.textarea = self.figure.add_subplot(236)
        self.textarea.axis('off')
        self.text_distance = self.textarea.text(0, 1200, '', fontsize=fs, ha='left', va='top', color=NBLUE,
                                           backgroundcolor='black')
        self.text_speed = self.textarea.text(0.6, 1200, '', fontsize=fs, ha='left', va='top', color=NCYAN,
                                           backgroundcolor='black')
        self.text_time = self.textarea.text(0.3, 1150, '', fontsize=fs, ha='left', va='top', color=NRED,
                                           backgroundcolor='black')
        self.text_hr = self.textarea.text(0, 1100, '', fontsize=fs, ha='left', va='top', color=NYELLOW,
                                           backgroundcolor='black')
        self.text_sat = self.textarea.text(0.6, 1100, '', fontsize=fs, ha='left', va='top', color=NORANGE,
                                           backgroundcolor='black')
        self.text_pressure = self.textarea.text(0, 1000, '', fontsize=fs, ha='left', va='top', color=NPINK,
                                           backgroundcolor='black')
        self.text_temperature = self.textarea.text(0.3, 950, '', fontsize=fs, ha='left', va='top', color=NPURPLE,
                                           backgroundcolor='black')
        self.text_gas = self.textarea.text(0.6, 1000, '', fontsize=fs, ha='left', va='top', color=NGREEN,
                                           backgroundcolor='black')
        self.text_waves = self.textarea.text(0.3, 1050, '', fontsize=fs, ha='left', va='top', color='white',
                                            backgroundcolor='black')

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

        # initializing values to be used in live calcs
        self.timer = 0
        self.ir_timer = 0
        self.rotations = 1
        self.previous = 0
        self.speed = 0
        self.distance = 0
        self.start = time.time()
        self.speed_arr = deque([[self.start, 1]])
        self.beat = 0
        self.hr = 0


        self.update_plot()

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
        """
        performs same function as create_graph() but adds another array of data to second y-axis
        displays 2nd y-axis on the right
        """
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
        self.rot_dif = self.speed_arr[index1][1] - self.speed_arr[index2][1]  # always 1 currently, potential to get different averages in future
        self.time_dif = self.speed_arr[index1][0] - self.speed_arr[index2][0]

        speed_num = 8  # 8 decided on arbitrarily, increase for wider avg, dec for more instant speed
        if len(self.speed_arr) > speed_num:
            dt = [self.speed_arr[-1][0] - self.speed_arr[-i][0] for i in range(2, speed_num)]
            avg_pedal = [(num / (idx + 1)) for idx, num in enumerate(dt)]
            self.speed = 0.0038 / ((sum(avg_pedal) / len(avg_pedal)) / 3600)
        else: # small exceptions for start of run before speed_arr is populated
            if self.time_dif < 0.004:
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
            self.hr = (60 / tick.total_seconds()) * peaks

    def graph_shift(self, shifting_graph, new_data, shifting_plot):
        shifting_graph.append(new_data)
        shifting_graph.pop(0)
        shifting_plot.set_xdata(self.time_array)
        shifting_plot.set_ydata(shifting_graph)

    def graph_lims(self, ax_in, ymin, ymax):
        ax_in.set_xlim(self.time_array[0], self.time_array[-1])
        ax_in.set_ylim(ymin, ymax)

    def update_plot(self):
        if self.timer >= 100:
            self.timer = 0
        self.timer += 1

        in_signal = arduino_multi_signal(arduino)
        while len(in_signal) < 10: #arduino occasionally returns [] for first value
            in_signal.append(0)
        #in_signal = [0, 1, 2, 3, 70000, 28000, 6, 7, 8, 9]
        # [a0, a1, a2, a3, IR, Red, BPM, AvgBPM, SP02, ?Finger]

        print(in_signal)

        bike_signal = int(in_signal[0])
        self.gas1 = int(in_signal[1])
        self.pressure = int(float(in_signal[2]))
        self.ir_wave = int(float(in_signal[4]))
        self.red_wave = int(float(in_signal[5]))
        self.sat = int(float(in_signal[8]))
        self.temperature = int(float(in_signal[9]))


        # create an array with time of when pedals have occured
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

        # only computes heart rate if finger is detected
        if self.ir_wave > 80000:
            self.wave_calc(self.data_ir_wave)
        else:
            self.hr = 0

        # update the x-axis
        self.x_data.append(self.x_data[-1] + 1)
        self.x_data.pop(0)
        self.time_array.append(dt.datetime.now())
        self.time_array.pop(0)

        # update each plot with new data
        self.graph_shift(self.data_distance, self.distance, self.plot_distance)
        self.graph_shift(self.data_speed, self.speed, self.plot_speed)
        self.graph_shift(self.data_gas, self.gas1, self.plot_gas)
        self.graph_shift(self.data_hr, self.hr, self.plot_hr)
        self.graph_shift(self.data_ir_wave, self.ir_wave, self.plot_ir_wave)
        self.graph_shift(self.data_pressure, self.pressure, self.plot_pressure)
        self.graph_shift(self.data_temperature, self.temperature, self.plot_temperature)
        self.graph_shift(self.data_sat, self.sat, self.plot_sat)
        self.graph_shift(self.data_red_wave, self.red_wave, self.plot_red_wave)

        # moving on the x-axis and scaling the y-axis
        self.graph_lims(self.ax_distance, min(self.data_distance), max(self.data_distance) + 0.1)
        self.graph_lims(self.ax_speed, 0, 25)
        self.graph_lims(self.ax_gas, min(self.data_gas) - 15, max(self.data_gas) + 15)
        self.graph_lims(self.ax_hr, 0, 200)
        self.graph_lims(self.ax_ir_wave, min(self.data_ir_wave) - 1000, max(self.data_ir_wave) + 1000)
        self.graph_lims(self.ax_pressure, min(self.data_pressure) - 5, max(self.data_pressure) + 5)
        self.graph_lims(self.ax_temperature, 70, 105)
        self.graph_lims(self.ax_sat, 80, 105)

        # Text box
        self.textarea.set_ylim(0, 500)
        self.text_distance.set_text(f"Distance:{self.distance: .2f}mi")
        self.text_speed.set_text(f"Speed:{self.speed: .2f}mph")
        self.text_gas.set_text(f"{self.gas1: .1f}gas")
        self.text_hr.set_text(f"HR:{self.hr: 0.0f}bpm")
        self.text_pressure.set_text(f"{self.pressure: .2f}kpa")
        self.text_temperature.set_text(f"{self.temperature: .2f}\N{DEGREE SIGN}F")
        self.text_sat.set_text(f"{self.sat: .2f}%")
        self.text_waves.set_text(f"IR: {self.ir_wave/1000: .0f}k Red: {self.red_wave/1000: .0f}k")
        current = self.time_array[-1] - self.current_time
        self.text_time.set_text(f"Elapsed: {str(current).split('.')[0]}")

        # redraw plot
        self.canvas.draw_idle()
        threading.Timer(0.001, self.update_plot).start()


if __name__ == "__main__":
    root = tk.Tk()
    WHOMMPGUI(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

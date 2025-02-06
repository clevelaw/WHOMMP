import time
import datetime as dt
import tkinter as tk
from collections import deque
import re
import bisect
import serial
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
SERIAL_PORT = 'COM3'
BAUD_RATE = 9_600

try:
    print("Connecting to Arduino...")
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=None)
    arduino.readline().decode().strip()  # discard initial line as it tends to be all zeros
    print("Connected to Arduino")
except serial.SerialException as e:
    print(f"Serial Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")

def read_arduino(ard_input) -> list:
    """reads input from arduino serial input and formats data as a list of ints
        example ard_list = [0, 1, 2, 3, 70000, 28000, 6, 7, 8, 9]
    """
    try:
        data = ard_input.readline().decode().strip()
        ard_list = re.findall(r"[-+]?\d*\.\d+|\d+", data)
        for index, value in enumerate(ard_list):
            if not value.isdigit():
                ard_list[index] = 0
            else:
                ard_list[index] = int(float(value))
        return ard_list
    except ValueError:
        print("Could not parse data")
    except serial.SerialException:
        print("Serial connection lost")

def on_closing() -> None:
    """stops the script if the GUI is closed"""
    root.destroy()

class WHOMMPGUI(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.config(bg='#000000')  # top ribbon color
        label = tk.Label(self, text="W.H.O.M.M.P.", fg=NGREEN, bg='#000000', font=20)
        label.pack(pady=10, padx=10)
        self.figure = Figure(figsize=(13, 6), dpi=100, facecolor='#000000')
        self.figure.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.2,  hspace=0.4)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.current_time = dt.datetime.now()
        self.time_fmt = mdates.DateFormatter('%S')
        self.data_range = 300
        self.start_time = self.current_time - dt.timedelta(seconds=50)  # subtract 50 seconds to get the start time
        self.time_array = [self.current_time - dt.timedelta(seconds=i * 0.1)\
                           for i in range(self.data_range)][::-1]
        self.rot_dif = 0
        self.time_dif = 0

        # creating arrays to store data
        #self.data_distance = [0] * self.data_range
        self.data_distance = deque([0] * self.data_range)
        self.data_speed = deque([0] * self.data_range)
        self.data_gas = deque([0] * self.data_range)
        self.data_hr = deque([0] * self.data_range)
        self.data_ir_wave = deque([0] * self.data_range)
        self.data_pressure = deque([0] * self.data_range)
        self.data_temperature = deque([0] * self.data_range)
        self.data_sat = deque([0] * self.data_range)
        self.data_red_wave = deque([0] * self.data_range)
        # creating the graphs and axes for each input
        self.ax_distance, self.plot_distance = self.create_graph(self.time_fmt, [3, 3, 1],
            self.time_array, self.data_distance, (0, 0.1), NBLUE, "Distance", "Miles")
        self.ax_speed, self.plot_speed = self.create_graph(self.time_fmt, [3, 3, 2],
            self.time_array, self.data_speed, (0, 25), NCYAN, "Speed", "M/H")
        self.ax_gas, self.plot_gas = self.create_graph(self.time_fmt, [3, 3, 3],
            self.time_array, self.data_gas, (150, 800), NGREEN, "Gas", "ppm")
        self.ax_hr, self.plot_hr = self.create_graph(self.time_fmt, [3, 3, 4],
            self.time_array, self.data_hr, (0, 200), NYELLOW, "Heart Rate", 'BPM')
        self.ax_pressure, self.plot_pressure = self.create_graph(self.time_fmt, [3, 3, 7],
            self.time_array, self.data_pressure, (0, 0.1), NPINK,'Pressure', "kPa")
        self.ax_temperature, self.plot_temperature = self.create_graph(self.time_fmt, [3, 3, 8],
            self.time_array, self.data_temperature, (0, 0.1), NPURPLE, 'Temp', "deg")
        self.ax_sat, self.plot_sat = self.create_graph(self.time_fmt, [3, 3, 9],
            self.time_array, self.data_sat, (0, 0.1), NORANGE, 'Sp02', "%")
        # graph with 2 y-axis
        self.ax_ir_wave, self.plot_ir_wave, self.plot_red_wave = self.double_graph(self.time_fmt, [3, 3, 6],
            self.time_array, self.data_ir_wave, self.data_red_wave, (0, 0.1), 'white', 'Absorbance', "AU", "AU")

        # plot area to place static/dynamic text
        fs = 14
        self.textarea = self.figure.add_subplot(3, 3, 5)
        self.textarea.axis('off')
        self.text_distance = self.textarea.text(0, 700, '', fontsize=fs, ha='left', va='top',
            color=NBLUE, backgroundcolor='black')
        self.text_speed = self.textarea.text(0, 525, '', fontsize=fs, ha='left', va='top',
            color=NCYAN, backgroundcolor='black')
        self.text_hr = self.textarea.text(0, 350, '', fontsize=fs, ha='left', va='top',
            color=NYELLOW, backgroundcolor='black')
        self.text_pressure = self.textarea.text(0, 175, '', fontsize=fs, ha='left', va='top',
            color=NPINK, backgroundcolor='black')
        self.text_time = self.textarea.text(0, 0, '', fontsize=fs, ha='left', va='top',
            color=NRED, backgroundcolor='black')
        self.text_gas = self.textarea.text(.95, 700, '', fontsize=fs, ha='right', va='top',
            color=NGREEN, backgroundcolor='black')
        self.text_ir = self.textarea.text(.95, 525, '', fontsize=fs, ha='right', va='top',
            color='white', backgroundcolor='black')
        self.text_red = self.textarea.text(.95, 350, '', fontsize=fs, ha='right', va='top',
            color='red', backgroundcolor='black')
        self.text_temperature = self.textarea.text(.95, 175, '', fontsize=fs, ha='right', va='top',
            color=NPURPLE, backgroundcolor='black')
        self.text_sat = self.textarea.text(.95, 0, '', fontsize=fs, ha='right', va='top',
             color=NORANGE, backgroundcolor='black')
        """
        # testing text location
        self.textarea.text(0, 0, '<0,0', fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(1, 0, '<1,0', fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 1200, '<0,1200' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(1, 1200, '<1,1200' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 1200, '0,1200r>' , fontsize=fs, ha='right', va='top', color=NYELLOW)
        self.textarea.text(0, 600, '<0,600' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 300, '<0,300' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 700, '0,7000r>' , fontsize=fs, ha='right', va='top', color=NYELLOW)
        self.textarea.text(0.5, 1200, '<0.5,1200' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        """
        # initializing values to be used in live calcs
        self.ir_timer = 0
        self.rotations = 1
        self.previous = 0
        self.speed = 0
        self.distance = 0
        self.start = time.time()
        self.speed_arr = deque([[self.start, 1]])
        self.beat = 0
        self.hr = 0

    def find_thirty_before(self, input_array) -> int:
        """find the index 30s before the current time for setting x-axis time"""
        target_time = input_array[-1] - dt.timedelta(seconds=30)
        index = bisect.bisect_left(input_array, target_time)
        if index == len(input_array):
            closest_index = index - 1
        elif index == 0:
            closest_index = 0
        else:
            closest_index = index
        return closest_index

    def print_time(self):
        """useful for finding timing errors"""
        print_time_index = self.find_thirty_before(self.time_array)
        print("Time array difference:", self.time_array[-1] - self.time_array[0])
        print("Graph range:", self.time_array[0], self.time_array[print_time_index], self.time_array[-1])

    def create_graph(self, xformat, location, xdata, ydata, ylim, line_color, dataname, units):
        """initial setup for individual GUI graphs"""
        gname = self.figure.add_subplot(location[0], location[1], location[2])
        gname.xaxis.set_major_formatter(xformat)
        graph = gname.plot(xdata, ydata, label=dataname, color=line_color)[0]
        gname.set_ylim(ylim[0], ylim[1])
        create_graph_limit = self.find_thirty_before(self.time_array)
        gname.set_xlim(self.time_array[create_graph_limit], self.time_array[-1])
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
        gname = self.figure.add_subplot(location[0], location[1], location[2])
        graph1 = gname.plot(xdata, ydata, label=dataname, color=line_color)[0]
        gname.set_ylim(ylim[0], ylim[1])
        double_graph_limit = self.find_thirty_before(self.time_array)
        gname.set_xlim(self.time_array[double_graph_limit], self.time_array[-1])
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
        """used for calculating speed of wheel rotation on stationary bike
        0.0038 is the constant to convert a single rotation of bike wheel to the distance it correlates to
        """
        self.distance = self.rotations * 0.0038
        self.rot_dif = self.speed_arr[index1][1] - self.speed_arr[index2][1]  # always 1 currently, potential to get different averages in future
        self.time_dif = self.speed_arr[index1][0] - self.speed_arr[index2][0]

        speed_num = 8  # 8 decided on arbitrarily, inc for wider avg, dec for more instant speed
        if len(self.speed_arr) > speed_num:
            time_change = [self.speed_arr[-1][0] - self.speed_arr[-i][0]\
                for i in range(2, speed_num)]
            avg_pedal = [(num / (idx + 1)) for idx, num in enumerate(time_change)]
            self.speed = 0.0038 / ((sum(avg_pedal) / len(avg_pedal)) / 3600)
        else: # small exceptions for start of run before speed_arr is populated
            if self.time_dif < 0.004:
                self.speed = 0
            else:
                self.speed = (self.rot_dif * 0.0038) / self.time_dif * 3600

    def wave_calc(self, data):
        """finds total number of local maxima in a wave"""
        self.ir_timer += 1
        if self.ir_timer > 50:
            self.ir_timer = 0
            peaks = 0
            for i in range(self.data_range - 50, self.data_range - 10):
                if data[i] > data[i - 1] and data[i] > data[i - 2] \
                        and data[i] > data[i + 1] and data[i] > data[i + 2]:
                    peaks += 1
            tick = self.time_array[490] - self.time_array[400]
            self.hr = (60 / tick.total_seconds()) * peaks

    def graph_shift(self, shifting_graph, new_data, shifting_plot):
        """FIFO principle for the collected data"""
        shifting_graph.append(new_data)
        shifting_graph.popleft()
        shifting_plot.set_xdata(self.time_array)
        shifting_plot.set_ydata(shifting_graph)

    def graph_lims(self, ax_in, ymin, ymax):
        """dynamically sets the y-axis on graphs"""
        graph_limit = self.find_thirty_before(self.time_array)
        ax_in.set_xlim(self.time_array[graph_limit], self.time_array[-1])
        ax_in.set_ylim(ymin, ymax)

    def update_plot(self):
        """-called recursively to collect data and directs GUI to update the graphs and text box info"""

        in_signal = read_arduino(arduino) # [a0, a1, a2, a3, IR, Red, BPM, AvgBPM, SP02, Pressure]
        while len(in_signal) < 10: #arduino occasionally returns [] for first value
            in_signal.append(0)

        bike_input = in_signal[0]
        gas_input = in_signal[1]
        pressure_input = in_signal[2]
        ir_input = in_signal[4]
        red_input = in_signal[5]
        sat_input = in_signal[8]
        temperature_input = in_signal[9]

        # create an array with time of when pedals have occured
        if bike_input - self.previous > 200:
            self.rotations += 1
            self.speed_arr.append([time.time(), self.rotations])
            if len(self.speed_arr) > 10:
                self.speed_arr.popleft()
        self.previous = bike_input
        pedals = len(self.speed_arr)
        if pedals > 1:
            self.calc_params(pedals - 1, pedals - 2)
        else:
            self.rot_dif = 0
            self.time_dif = 0

        # only computes heart rate if finger is detected
        if ir_input > 80000:
            self.wave_calc(self.data_ir_wave)
        else:
            self.hr = 0

        self.time_array.append(dt.datetime.now())
        self.time_array.pop(0)

        # update each plot with new data
        self.graph_shift(self.data_distance, self.distance, self.plot_distance)
        self.graph_shift(self.data_speed, self.speed, self.plot_speed)
        self.graph_shift(self.data_gas, gas_input, self.plot_gas)
        self.graph_shift(self.data_hr, self.hr, self.plot_hr)
        self.graph_shift(self.data_ir_wave, ir_input, self.plot_ir_wave)
        self.graph_shift(self.data_pressure, pressure_input, self.plot_pressure)
        self.graph_shift(self.data_temperature, temperature_input, self.plot_temperature)
        self.graph_shift(self.data_sat, sat_input, self.plot_sat)
        self.graph_shift(self.data_red_wave, red_input, self.plot_red_wave)

        # moving on the x-axis and scaling the y-axis
        self.graph_lims(self.ax_distance, min(self.data_distance), max(self.data_distance) + 0.1)
        self.graph_lims(self.ax_speed, 0, 25)
        self.graph_lims(self.ax_gas, min(self.data_gas) - 15, max(self.data_gas) + 15)
        self.graph_lims(self.ax_hr, 0, 200)
        self.graph_lims(self.ax_ir_wave, min(self.data_ir_wave) - 1000, max(self.data_ir_wave) + 1000)
        self.graph_lims(self.ax_pressure, min(self.data_pressure) - 5, max(self.data_pressure) + 5)
        self.graph_lims(self.ax_temperature, 70, 105)
        self.graph_lims(self.ax_sat, 80, 105)

        # update the text boxes with current values
        self.textarea.set_ylim(0, self.data_range * 2)
        self.text_distance.set_text(f"Distance:{self.distance: .2f}mi")
        self.text_speed.set_text(f"Speed:{self.speed: .2f}mph")
        self.text_gas.set_text(f"{gas_input: .1f}ppm")
        self.text_hr.set_text(f"HR:{self.hr: 0.0f}bpm")
        self.text_pressure.set_text(f"{pressure_input: .2f}kpa")
        self.text_temperature.set_text(f"{temperature_input: .2f}\N{DEGREE SIGN}F")
        self.text_sat.set_text(f"{sat_input: .2f}%")
        self.text_ir.set_text(f"IR: {ir_input/1000: .0f}k")
        self.text_red.set_text(f"Red: {red_input/1000: .0f}k")
        current = self.time_array[-1] - self.current_time
        self.text_time.set_text(f"{str(current).split('.', maxsplit=1)[0]}")

        # redraw plot
        self.canvas.draw_idle()
        self.after(500, self.update_plot)

if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height - 50}")
    bike_gui = WHOMMPGUI(root)
    bike_gui.pack(side="top", fill="both", expand=True)
    print("-----------Starting GUI-----------")
    bike_gui.update_plot()
    root.mainloop()

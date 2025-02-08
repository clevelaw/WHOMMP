import time
import sys
import datetime as dt
import tkinter as tk
from collections import deque
import re
import bisect
import threading
import serial
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Define colors and serial settings
NBLUE = '#006FFF'
NCYAN = '#13F4EF'
NGREEN = '#68FF00'
NYELLOW = '#FAFF00'
NRED = '#FF005C'
NORANGE = '#FF6600'
NPINK = '#FF00FF'
NPURPLE = '#9D00FF'
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
GLOBAL_TIME = time.time()

# connect to Arduino
try:
    print("Connecting to Arduino...")
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=None)
    arduino.readline().decode().strip()  # discard initial line (often zeros)
    print("Connected to Arduino")
except serial.SerialException as e:
    print(f"Serial Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected Error: {e}")
    sys.exit(1)


def read_arduino(ard_input) -> list:
    """Read input from Arduino serial and format it as a list of integers."""
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
    """Stop the script when the GUI is closed."""
    root.destroy()


class GraphPanel:
    """create and update the graphs"""

    def __init__(self, figure, time_fmt, data_range):
        self.figure = figure
        self.time_fmt = time_fmt
        self.data_range = data_range
        self.current_time = dt.datetime.now()
        self.time_array = [self.current_time - dt.timedelta(seconds=i * 0.04)
                           for i in range(data_range)][::-1]
        # deques to store collected data
        self.data_distance = deque([0] * data_range)
        self.data_speed = deque([0] * data_range)
        self.data_gas = deque([0] * data_range)
        self.data_hr = deque([0] * data_range)
        self.data_ir_wave = deque([0] * data_range)
        self.data_pressure = deque([0] * data_range)
        self.data_temperature = deque([0] * data_range)
        self.data_sat = deque([0] * data_range)
        self.data_red_wave = deque([0] * data_range)

        # create graphs
        self.ax_distance, self.plot_distance = self.create_graph([3, 3, 1],
                                                                 self.data_distance, (0, 0.1), NBLUE, "Distance", "Miles")
        self.ax_speed, self.plot_speed = self.create_graph([3, 3, 2],
                                                           self.data_speed, (0, 25), NCYAN, "Speed", "mph")
        self.ax_gas, self.plot_gas = self.create_graph([3, 3, 3],
                                                       self.data_gas, (150, 800), NGREEN, "Gas", "ppm")
        self.ax_hr, self.plot_hr = self.create_graph([3, 3, 4],
                                                     self.data_hr, (0, 200), NYELLOW, "Heart Rate", "BPM")
        self.ax_pressure, self.plot_pressure = self.create_graph([3, 3, 7],
                                                                 self.data_pressure, (0, 0.1), NPINK, 'Pressure', "kPa")
        self.ax_temperature, self.plot_temperature = self.create_graph([3, 3, 8],
                                                                       self.data_temperature, (0, 0.1), NPURPLE, 'Temp', "deg")
        self.ax_sat, self.plot_sat = self.create_graph([3, 3, 9],
                                                       self.data_sat, (0, 0.1), NORANGE, 'Sp02', "%")
        self.ax_ir_wave, self.plot_ir_wave, self.plot_red_wave = self.double_graph([3, 3, 6],
                                                                                   self.data_ir_wave, self.data_red_wave, (0, 0.1), 'white', 'Absorbance', "AU", "AU")

    def find_x_limit(self, input_array) -> int:
        """Find the index corresponding to 30 seconds before the latest time."""
        time_window = (
            # depends on read speeds
            self.time_array[-1] - self.time_array[0]).seconds
        target_time = input_array[-1] - dt.timedelta(seconds=time_window)
        index = bisect.bisect_left(input_array, target_time)
        if index == len(input_array):
            closest_index = index - 1
        elif index == 0:
            closest_index = 0
        else:
            closest_index = index
        return closest_index

    def create_graph(self, location, ydata, ylim, line_color, dataname, units):
        """Initial setup for a single graph."""
        ax = self.figure.add_subplot(location[0], location[1], location[2])
        ax.xaxis.set_major_formatter(self.time_fmt)
        plot_line = ax.plot(self.time_array, ydata,
                            label=dataname, color=line_color)[0]
        ax.set_ylim(ylim[0], ylim[1])
        limit_index = self.find_x_limit(self.time_array)
        ax.set_xlim(self.time_array[limit_index], self.time_array[-1])
        ax.set_facecolor('black')
        ax.set_title(dataname, color=line_color)
        ax.set_ylabel(units, color=line_color)
        ax.tick_params(axis='both', color=line_color, labelcolor=line_color)
        return ax, plot_line

    def double_graph(self, location, ydata, y2_data, ylim, line_color, dataname, units, units2):
        """Setup for a graph with two y-axes."""
        ax = self.figure.add_subplot(location[0], location[1], location[2])
        plot_line1 = ax.plot(self.time_array, ydata,
                             label=dataname, color=line_color)[0]
        ax.set_ylim(ylim[0], ylim[1])
        limit_index = self.find_x_limit(self.time_array)
        ax.set_xlim(self.time_array[limit_index], self.time_array[-1])
        ax.set_facecolor('black')
        ax.set_title(dataname, color=line_color)
        ax.set_ylabel(units, color=line_color)
        ax.tick_params(axis='x', labelcolor=line_color)
        ax.tick_params(axis='y', labelcolor=line_color)
        # Second y-axis
        ax2 = ax.twinx()
        plot_line2 = ax2.plot(self.time_array, y2_data,
                              label=dataname, color='red')[0]
        ax2.set_ylim(25000, 29000)
        ax2.set_ylabel(units2)
        ax2.xaxis.set_major_formatter(self.time_fmt)
        ax2.tick_params(axis='y', labelcolor='red')
        return ax, plot_line1, plot_line2

    def graph_shift(self, data_deque, new_data, plot_line):
        """Shift the data (FIFO) and update the plot’s data."""
        data_deque.append(new_data)
        data_deque.popleft()
        plot_line.set_xdata(self.time_array)
        plot_line.set_ydata(data_deque)

    def graph_lims(self, ax, ymin, ymax):
        """Dynamically adjust the y-axis limits and x-axis time window."""
        limit_index = self.find_x_limit(self.time_array)
        ax.set_xlim(self.time_array[limit_index], self.time_array[-1])
        ax.set_ylim(ymin, ymax)

    def update_time(self):
        """Append the current time and remove the oldest time value."""
        self.time_array.pop(0)
        self.time_array.append(dt.datetime.now())


class CalculationHandler:
    """Computes speed, distance, heart rate, etc."""

    def __init__(self):
        self.rotations = 1
        self.previous = 0
        self.speed_arr = deque([[time.time(), 1]])
        self.ir_timer = 0
        self.hr = 0
        self.speed = 0
        self.distance = 0

    def calc_params(self, speed_arr):
        """Calculate the current speed and distance."""
        pedals = len(speed_arr)
        if pedals > 1:
            rot_dif = speed_arr[-1][1] - speed_arr[-2][1]
            time_dif = speed_arr[-1][0] - speed_arr[-2][0]
            speed_num = 8  # Number of samples to average for speed calculation
            if len(speed_arr) > speed_num:
                time_change = [speed_arr[-1][0] - speed_arr[-i][0]
                               for i in range(2, speed_num)]
                avg_pedal = [t / (idx + 1)
                             for idx, t in enumerate(time_change)]
                self.speed = 0.0038 / \
                    ((sum(avg_pedal) / len(avg_pedal)) / 3600)
            else:
                if time_dif < 0.004:
                    self.speed = 0
                else:
                    self.speed = (rot_dif * 0.0038) / time_dif * 3600
        else:
            self.speed = 0

        self.distance = self.rotations * 0.0038

    def wave_calc(self, data, time_array, data_range):
        """Compute heart rate based on peaks in the IR waveform."""
        self.ir_timer += 1
        if self.ir_timer > 50:
            self.ir_timer = 0
            peaks = 0
            for i in range(data_range - 50, data_range - 10):
                if data[i] > data[i - 1] and data[i] > data[i - 2] and \
                   data[i] > data[i + 1] and data[i] > data[i + 2]:
                    peaks += 1
            tick = time_array[190] - time_array[100]
            self.hr = (60 / tick.total_seconds()) * peaks


class TextPanel:
    """Manages the text panel and updates."""

    def __init__(self, figure, data_range):
        self.textarea = figure.add_subplot(3, 3, 5)
        self.textarea.axis('off')
        textbox_height = figure.figbbox.extents[2] - 100
        fs = 20
        # testing text location
        """
        self.textarea.text(0, 0, '<0,0', fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(1, 0, '<1,0', fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 1200, '<0,1200' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(1, 1200, '<1,qqq' , fontsize=30, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 1200, '0,1200r>' , fontsize=fs, ha='right', va='top', color=NYELLOW)
        self.textarea.text(0, 600, '<0,600' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 300, '<0,300' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        self.textarea.text(0, 700, '0,7000r>' , fontsize=fs, ha='right', va='top', color=NYELLOW)
        self.textarea.text(0.5, 1200, '<0.5,1200' , fontsize=fs, ha='left', va='top', color=NYELLOW)
        """

        self.text_distance = self.textarea.text(0, textbox_height, '', fontsize=fs, ha='left', va='top',
                                                color=NBLUE, backgroundcolor='black')
        self.text_speed = self.textarea.text(0, textbox_height * .75, '', fontsize=fs, ha='left', va='top',
                                             color=NCYAN, backgroundcolor='black')
        self.text_hr = self.textarea.text(0, textbox_height * 0.5, '', fontsize=fs, ha='left', va='top',
                                          color=NYELLOW, backgroundcolor='black')
        self.text_pressure = self.textarea.text(0, textbox_height * .25, '', fontsize=fs, ha='left', va='top',
                                                color=NPINK, backgroundcolor='black')
        self.text_time = self.textarea.text(0, 0, '', fontsize=fs, ha='left', va='top',
                                            color=NRED, backgroundcolor='black')
        self.text_gas = self.textarea.text(0.95, textbox_height, '', fontsize=fs, ha='right', va='top',
                                           color=NGREEN, backgroundcolor='black')
        self.text_ir = self.textarea.text(0.95, textbox_height * 0.75, '', fontsize=fs, ha='right', va='top',
                                          color='white', backgroundcolor='black')
        self.text_red = self.textarea.text(0.95, textbox_height * 0.5, '', fontsize=fs, ha='right', va='top',
                                           color='red', backgroundcolor='black')
        self.text_temperature = self.textarea.text(0.95, textbox_height * 0.25, '', fontsize=fs, ha='right', va='top',
                                                   color=NPURPLE, backgroundcolor='black')
        self.text_sat = self.textarea.text(0.95, 0, '', fontsize=fs, ha='right', va='top',
                                           color=NORANGE, backgroundcolor='black')
        self.textarea.set_ylim(0, data_range * 2)

    def update(self, distance, speed, gas, hr, pressure, temperature, sat, ir, red, current):
        """Update the text display with current values."""
        self.text_distance.set_text(f"Distance: {distance: .2f}mi")
        self.text_speed.set_text(f"Speed: {speed: .2f}mph")
        self.text_gas.set_text(f"{gas: .1f}ppm")
        self.text_hr.set_text(f"HR: {hr: .0f}bpm")
        self.text_pressure.set_text(f"{pressure: .2f}kpa")
        self.text_temperature.set_text(f"{temperature: .2f}\N{DEGREE SIGN}F")
        self.text_sat.set_text(f"{sat: .2f}%")
        self.text_ir.set_text(f"IR: {ir/1000: .0f}k")
        self.text_red.set_text(f"Red: {red/1000: .0f}k")
        self.text_time.set_text(f"{str(current).split('.', maxsplit=1)[0]}")


class WHOMMPGUI(tk.Frame):
    """Main element for the GUI, uses GraphPanel, CalculationHandler, TextPanel
        take the root of the Tkinter as an input"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg='#000000')
        label = tk.Label(self, text="W.H.O.M.M.P.",
                         fg=NGREEN, bg='#000000', font=20)
        label.pack(pady=10, padx=10)

        # set up Matplotlib figure and canvas
        self.figure = Figure(figsize=(13, 6), dpi=100, facecolor='#000000')
        self.figure.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95,
                                    wspace=0.2, hspace=0.4)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.data_range = 500
        self.time_fmt = mdates.DateFormatter('%S')

        # instantiate the sub-components
        self.graph_panel = GraphPanel(
            self.figure, self.time_fmt, self.data_range)
        self.calc_handler = CalculationHandler()
        self.text_panel = TextPanel(self.figure, self.data_range)

    def update_plot(self):
        """Read data, update calculations, graphs, and text; then schedule the next update."""
        # reads in data and stores, can cause large delays if not read fast enough
        # in_signal = read_arduino(arduino)  # Expected: [a0, a1, a2, a3, IR, Red, BPM, AvgBPM, SP02, Pressure]
        in_signal = read_arduino(arduino)

        while len(in_signal) < 10:  # arduino sometimes returns too few values
            in_signal.append(0)

        # Unpack sensor values
        bike_input = in_signal[0]
        gas_input = in_signal[1]
        pressure_input = in_signal[2]
        ir_input = in_signal[4]
        red_input = in_signal[5]
        sat_input = in_signal[3]  # nonnononon
        temperature_input = in_signal[6]

        # converts a signal from hall sensor to distance
        if bike_input - self.calc_handler.previous > 200:
            self.calc_handler.rotations += 1
            self.calc_handler.speed_arr.append(
                [time.time(), self.calc_handler.rotations])
            if len(self.calc_handler.speed_arr) > 10:
                self.calc_handler.speed_arr.popleft()
        self.calc_handler.previous = bike_input
        self.calc_handler.calc_params(self.calc_handler.speed_arr)

        # compute heart rate only if finger is detected
        if ir_input > 80000:
            self.calc_handler.wave_calc(self.graph_panel.data_ir_wave,
                                        self.graph_panel.time_array, self.data_range)
        else:
            self.calc_handler.hr = 0

        # update time history for the x-axis
        self.graph_panel.update_time()

        # update each graph with the new data
        self.graph_panel.graph_shift(self.graph_panel.data_distance, self.calc_handler.distance,
                                     self.graph_panel.plot_distance)
        self.graph_panel.graph_shift(self.graph_panel.data_speed, self.calc_handler.speed,
                                     self.graph_panel.plot_speed)
        self.graph_panel.graph_shift(self.graph_panel.data_gas, gas_input,
                                     self.graph_panel.plot_gas)
        self.graph_panel.graph_shift(self.graph_panel.data_hr, self.calc_handler.hr,
                                     self.graph_panel.plot_hr)
        self.graph_panel.graph_shift(self.graph_panel.data_ir_wave, ir_input,
                                     self.graph_panel.plot_ir_wave)
        self.graph_panel.graph_shift(self.graph_panel.data_pressure, pressure_input,
                                     self.graph_panel.plot_pressure)
        self.graph_panel.graph_shift(self.graph_panel.data_temperature, temperature_input,
                                     self.graph_panel.plot_temperature)
        self.graph_panel.graph_shift(self.graph_panel.data_sat, sat_input,
                                     self.graph_panel.plot_sat)
        self.graph_panel.graph_shift(self.graph_panel.data_red_wave, red_input,
                                     self.graph_panel.plot_red_wave)

        # adjust axes limits as
        self.graph_panel.graph_lims(self.graph_panel.ax_distance,
                                    min(self.graph_panel.data_distance),
                                    max(self.graph_panel.data_distance) + 0.1)
        self.graph_panel.graph_lims(self.graph_panel.ax_speed, 0, 25)
        self.graph_panel.graph_lims(self.graph_panel.ax_gas,
                                    min(self.graph_panel.data_gas) - 15,
                                    max(self.graph_panel.data_gas) + 15)
        self.graph_panel.graph_lims(self.graph_panel.ax_hr, 0, 200)
        self.graph_panel.graph_lims(self.graph_panel.ax_ir_wave,
                                    min(self.graph_panel.data_ir_wave) - 1000,
                                    max(self.graph_panel.data_ir_wave) + 1000)
        self.graph_panel.graph_lims(self.graph_panel.ax_pressure,
                                    min(self.graph_panel.data_pressure) - 5,
                                    max(self.graph_panel.data_pressure) + 5)
        self.graph_panel.graph_lims(self.graph_panel.ax_temperature, 70, 105)
        self.graph_panel.graph_lims(self.graph_panel.ax_sat, 80, 105)

        # update text display with the current values
        current = self.graph_panel.time_array[-1] - \
            self.graph_panel.current_time
        self.text_panel.update(self.calc_handler.distance, self.calc_handler.speed, gas_input,
                               self.calc_handler.hr, pressure_input, temperature_input,
                               sat_input, ir_input, red_input, current)

        # redraws all components of the
        self.canvas.draw_idle()
        # runs into race conditions if used recursively
        # threading.Timer(0.1, self.update_plot).start()


def schedule_update(gui, interval=0.1):
    """Calls gui.update_plot() and schedules itself again after 'interval' seconds."""
    gui.update_plot()
    t = threading.Timer(interval, schedule_update, args=(gui, interval))
    t.daemon = True
    t.start()


if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height - 50}")
    bike_gui = WHOMMPGUI(root)
    bike_gui.pack(side="top", fill="both", expand=True)
    print("-----------Starting GUI-----------")
    schedule_update(bike_gui, interval=0.001)
    root.mainloop()

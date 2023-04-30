import serial
import datetime as dt
import tkinter as tk
import threading
import re
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#                            ['NBLUE', 'NCYAN', 'NGREEN', 'NYELLOW', white, 'NRED', 'NORANGE', 'NPINK', 'NPURPLE']
color_list = ['#006FFF', '#13F4EF', '#68FF00', '#FAFF00', 'white', '#FF005C', '#FF6600', '#FF00FF', '#9D00FF']

input_info = {
    "input1": "in1",
    "input2": "in2",
    "input3": "in3",
    "input4": "in4",
    "input5": "in5",
    "input6": "in6",
    "input7": "in7",
    "input8": "in8"
}

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
        self.figure = Figure(figsize=(13, 6), dpi=100, facecolor='#000000')
        self.figure.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.2, hspace=0.4)
        label = tk.Label(self, text="Arduino DAQ", fg=color_list[2], bg='#000000', font=20)
        label.pack(pady=10, padx=10)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


        self.x_data = [0 + i for i in range(self.data_range)]
        # will always create 8 graphs, assumes arduino is acquiring at least that many signals
        self.data_list = []
        for i in range(8):
            self.data_list.append([0 for j in range(self.data_range)])

        # creating the graphs and their positioning, 333 is skipped for text
        graphs = [(331 + j, self.data_list[i], color_list[i], f'{input_info[f"input{i+1}"]}', f'Unit{i + 1}') for i, j in
                  zip(range(8), [0, 1, 3, 4, 5, 6, 7, 8])]

        # creating the axis and line for each set of data
        self.axes_and_plots = []
        for i, (subplot, data, color, label, unit) in enumerate(graphs, start=1):
            ax, plot = self.create_graph(time_fmt, subplot, self.time_array, data, (0, 1024), color, label, unit)
            self.axes_and_plots.append((ax, plot))

        # plot area to place static/dynamic text
        fs = 15
        self.textarea = self.figure.add_subplot(236)
        self.textarea.axis('off')
        self.text_time = self.textarea.text(0.6, 1200, '', fontsize=fs, ha='left', va='top', color=color_list[5],
                                            backgroundcolor='black')

        # positions in this were determined manually
        pos_list = [(0, 1200), (0.3, 1150), (0, 1100), (0.3, 1050), (0.6, 1100), (0, 1000), (0.3, 950), (0.6, 1000)]
        for i in range(0, len(pos_list)):
            text = self.textarea.text(pos_list[i][0], pos_list[i][1], '', fontsize=fs, ha='left', va='top',
                                      color=color_list[i], backgroundcolor='black')
            setattr(self, f"text{i + 1}", text)

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

    def graph_shift(self, shifting_graph, new_data, shifting_plot):
        shifting_graph.append(new_data)
        shifting_graph.pop(0)
        shifting_plot.set_xdata(self.time_array)
        shifting_plot.set_ydata(shifting_graph)

    def graph_lims(self, ax_in, ymin, ymax):
        ax_in.set_xlim(self.time_array[0], self.time_array[-1])
        ax_in.set_ylim(ymin, ymax)

    def update_plot(self):
        # extracting signal from arduino
        in_signal = arduino_multi_signal(arduino)
        while len(in_signal) < 8:
            in_signal.append(0)
        for sig in range(0, len(in_signal)):
            in_signal[sig] = int(float(in_signal[sig]))

        # update the x-axis
        self.x_data.append(self.x_data[-1] + 1)
        self.x_data.pop(0)
        self.time_array.append(dt.datetime.now())
        self.time_array.pop(0)

        # update plots and shift y-axis
        for k in range(len(self.data_list)):
            self.graph_shift(self.data_list[k], in_signal[k], self.axes_and_plots[k][1])
            self.graph_lims(self.axes_and_plots[k][0], min(self.data_list[k]), max(self.data_list[k])+0.1)

        # Text box
        self.textarea.set_ylim(0, 500)
        self.text1.set_text(f"{input_info['input1']}:{in_signal[0]: .2f}")
        self.text2.set_text(f"{input_info['input2']}:{in_signal[1]: .2f}")
        self.text3.set_text(f"{input_info['input3']}:{in_signal[2]: .2f}")
        self.text4.set_text(f"{input_info['input4']}:{in_signal[3]: .2f}")
        self.text5.set_text(f"{input_info['input5']}:{in_signal[4]: .2f}")
        self.text6.set_text(f"{input_info['input6']}:{in_signal[5]: .2f}")
        self.text7.set_text(f"{input_info['input7']}:{in_signal[6]: .2f}")
        self.text8.set_text(f"{input_info['input8']}:{in_signal[7]: .2f}")
        current = self.time_array[-1] - self.current_time
        self.text_time.set_text(f"Elapsed: {str(current).split('.')[0]}")

        # redraw plot
        self.canvas.draw_idle()
        threading.Timer(0.001, self.update_plot).start()

if __name__ == "__main__":
    root = tk.Tk()
    WHOMMPGUI(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

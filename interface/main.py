import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from adv_analysis import make_graph

# Savitzky–Golay filter parameters
WINDOW_LENGTH = 101
POLYNOM_ORDER = 3

FONTSIZE = 14

angle = "Left"
graph = "values"
task = "task 1"
trials = []
file_path = None

def select_file():
    global file_path, trials
    file_path = filedialog.askopenfilename()
    trials = []
    update_button_state()

def update_button_state():
    if file_path is not None:
        show_button.config(state="normal")
    else:
        show_button.config(state="disabled")

def select_angle(event):
    global angle
    angle = angle_var.get()

def select_graph(event):
    global graph
    graph = graph_var.get()

def select_task(event):
    global task
    task = task_var.get()

def show_graph():
    global trials, file_path

    from_text = from_entry.get()
    from_value = float(from_text)
    to_text = to_entry.get()
    to_value = float(to_text)

    fig = make_graph(file_path, angle, graph, [from_value, to_value], WINDOW_LENGTH, POLYNOM_ORDER, task)
    plt.show()

    canvas.figure = fig
    canvas.draw()

root = tk.Tk()
matplotlib.use('TkAgg')

style = ttk.Style()
style.configure('TButton', font=('TkDefaultFont', FONTSIZE), padding=10)
style.configure('TMenubutton', font=('TkDefaultFont', FONTSIZE), padding=10)

# Create frame to hold buttons and dropdowns
frame = ttk.Frame(root)
frame.pack()

# Select file button
select_file_button = ttk.Button(frame, text="Select file", command=select_file)
select_file_button.pack(side=tk.LEFT)

# Select angle dropdown
angle_var = tk.StringVar(root)
angle_var.set("Left")  # default value
angle_options = ["Left", "Left", "Right"]
angle_dropdown = ttk.OptionMenu(frame, angle_var, *angle_options, command=select_angle)
angle_dropdown.pack(side=tk.LEFT)

# Select graph dropdown
graph_var = tk.StringVar(root)
graph_var.set("values")  # default value
graph_options = ["values", "values", "trials angle/time",
                 "corr dist-angle", "corr elbow-shoulder", "parameters",
                 "compare angle/time", "compare corr elbow-shoulder",
                 "compare sides"]
graph_dropdown = ttk.OptionMenu(frame, graph_var, *graph_options, command=select_graph)
graph_dropdown.pack(side=tk.LEFT)

# Select task dropdown
task_var = tk.StringVar(root)
task_var.set("task 1")  # default value
task_options = ["task 1", "task 1", "task 2", "task 3"]
task_dropdown = ttk.OptionMenu(frame, task_var, *task_options, command=select_task)
task_dropdown.pack(side=tk.LEFT)

# From entry and label
from_label = ttk.Label(frame, text="From:", font=('TkDefaultFont', FONTSIZE))
from_label.pack(side=tk.LEFT)
from_entry = ttk.Entry(frame, width=5, font=('TkDefaultFont', FONTSIZE))
from_entry.insert(0, "0")
from_entry.pack(side=tk.LEFT)

# To entry and label
to_label = ttk.Label(frame, text="To:", font=('TkDefaultFont', FONTSIZE))
to_label.pack(side=tk.LEFT)
to_entry = ttk.Entry(frame, width=5, font=('TkDefaultFont', FONTSIZE))
to_entry.insert(0, "100")
to_entry.pack(side=tk.LEFT)

# Show button
show_button = ttk.Button(frame, text="Show", command=show_graph)
show_button.pack(side=tk.LEFT)
update_button_state()

# Create a canvas to display the plot
fig = matplotlib.figure.Figure()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

root.mainloop()

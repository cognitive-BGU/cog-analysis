import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from adv_analysis import make_graph
from edit_trials import edit_trials

FONTSIZE = 14

side = "LEFT"
graph = "values"
task = "task 1"
trials = []
filename = None

def select_file():
    global filename, trials
    filename = filedialog.askopenfilename()
    trials = []
    update_button_state()

def update_button_state():
    if filename is not None:
        show_button.config(state="normal")
        edit_trails_button.config(state="normal")
    else:
        show_button.config(state="disabled")
        edit_trails_button.config(state="disabled")

def side_angle(event):
    global side
    side = side_var.get()

def select_graph(event):
    global graph
    graph = graph_var.get()

def select_task(event):
    global task
    task = task_var.get()

def show_graph():
    global trials, filename
    from_value = float(from_entry.get())
    to_value = float(to_entry.get())
    fig = make_graph(filename, side, graph, [from_value, to_value], task)
    plt.show()

    canvas.figure = fig
    canvas.draw()

root = tk.Tk()
matplotlib.use('TkAgg')

style = ttk.Style()
style.configure('TButton', font=('TkDefaultFont', FONTSIZE), padding=10)
style.configure('TMenubutton', font=('TkDefaultFont', FONTSIZE), padding=10)

frame = ttk.Frame(root)
frame.pack()

# Select file button
select_file_button = ttk.Button(frame, text="Select file", command=select_file)
select_file_button.pack(side=tk.LEFT)

# Select side dropdown
side_var = tk.StringVar(root)
side_var.set("LEFT")  # default value
side_options = ["LEFT", "LEFT", "RIGHT"]
side_dropdown = ttk.OptionMenu(frame, side_var, *side_options, command=side_angle)
side_dropdown.pack(side=tk.LEFT)

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

# Edit Trails button
edit_trails_button = ttk.Button(frame, text="Edit Trials",
                                command=lambda: edit_trials(filename, side, [float(from_entry.get()), float(to_entry.get())]))
edit_trails_button.pack(side=tk.LEFT)
update_button_state()

# Create a canvas to display the plot
fig = matplotlib.figure.Figure()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

root.mainloop()

import tkinter as tk
from tkinter import filedialog, ttk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from adv_analysis import make_graph

angle = "LeftShoulderAngle"
graph = "values"
task = "task 1"
trials = []


def show_trials():
    global trials
    global trials_window
    if 'trials_window' in globals():
        trials_window.destroy()
    trials_window = tk.Toplevel(root)
    trials_window.title("Trials")

    # Set the size and position of the window
    trials_window.geometry("300x600+{}+{}".format(root.winfo_x() + 100, root.winfo_y() + 100))

    # Add title
    title_label = ttk.Label(trials_window, text="frame", font=("TkDefaultFont", 12))
    title_label.grid(row=0, column=1, columnspan=2)
    title_label = ttk.Label(trials_window, text="seconds", font=("TkDefaultFont", 12))
    title_label.grid(row=0, column=3, columnspan=2)

    def delete_trial(i):
        del trials[i]
        show_trials()

    def save_trials():
        global trials
        for i, trial in enumerate(trials):
            for j in range(len(trial)):
                trial_entry = trials_window.grid_slaves(row=i + 1, column=j + 1)[0]
                trial[j] = int(trial_entry.get())
        trials_window.destroy()

    for i, trial in enumerate(trials):
        trial_label = ttk.Label(trials_window, text=f"Trial {i + 1}:")
        trial_label.grid(row=i + 1, column=0)
        for j, value in enumerate(trial):
            trial_entry = ttk.Entry(trials_window, width=5)
            trial_entry.insert(0, str(value))
            trial_entry.grid(row=i + 1, column=j + 1)
        # Add label displaying trial value divided by 60
        trial_start_label = ttk.Label(trials_window, text=f"{(trial[0]) / 60:.2f}")
        trial_start_label.grid(row=i + 1, column=len(trial) + 1)
        trial_end_label = ttk.Label(trials_window, text=f"{(trial[1]) / 60:.2f}")
        trial_end_label.grid(row=i + 1, column=len(trial) + 2)

        delete_button = tk.Button(trials_window, text="Delete", command=lambda i=i: delete_trial(i))
        delete_button.configure(font=("TkDefaultFont", 12))  # Make the font on the Delete button smaller
        delete_button.grid(row=i + 1, column=len(trial) + 3)

    # Save button
    save_button = tk.Button(trials_window, text="Save", command=save_trials)
    save_button.configure(font=("TkDefaultFont", 12))
    save_button.grid(row=len(trials) + 1, column=0, columnspan=len(trials[0]) + 3)


def select_file():
    global fstFile, trials
    fstFile = filedialog.askopenfilename()
    trials = []


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
    import matplotlib.pyplot as plt

    global trials, fstFile
    from_text = from_entry.get()
    to_text = to_entry.get()
    window_length_text = window_length_entry.get()
    polyorder_text = polyorder_entry.get()

    # Convert the text to floating-point numbers or integers
    from_value = float(from_text)
    to_value = float(to_text)
    window_length_value = int(window_length_text)
    polyorder_value = int(polyorder_text)

    fig = make_graph(fstFile, angle, graph, [from_value, to_value], window_length_value, polyorder_value, task)

    ################
    plt.show()
    ############

    canvas.figure = fig
    canvas.draw()
    trials_button.config(state="normal")


FONTSIZE = 14
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
angle_var.set("LeftShoulderAngle")  # default value
angle_options = ["LeftShoulderAngle", "LeftShoulderAngle", "RightShoulderAngle"]
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

# Window length entry and label
window_length_label = ttk.Label(frame, text="Window length:", font=('TkDefaultFont', FONTSIZE))
window_length_label.pack(side=tk.LEFT)
window_length_entry = ttk.Entry(frame, width=5, font=('TkDefaultFont', FONTSIZE))
window_length_entry.insert(0, "101")
window_length_entry.pack(side=tk.LEFT)

# Polyorder entry and label
polyorder_label = ttk.Label(frame, text="Polyorder:", font=('TkDefaultFont', FONTSIZE))
polyorder_label.pack(side=tk.LEFT)
polyorder_entry = ttk.Entry(frame, width=5, font=('TkDefaultFont', FONTSIZE))
polyorder_entry.insert(0, "3")
polyorder_entry.pack(side=tk.LEFT)

# Show button
show_button = ttk.Button(frame, text="Show", command=show_graph)
show_button.pack(side=tk.LEFT)

# Trials button
trials_button = ttk.Button(frame, text="Trials", command=show_trials)
if len(trials) == 0:
    trials_button.config(state="disabled")
trials_button.pack(side=tk.LEFT)

# Create a canvas to display the plot
fig = matplotlib.figure.Figure()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

root.mainloop()

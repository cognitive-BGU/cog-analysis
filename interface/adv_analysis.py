import json
import os
import pandas as pd
from scipy.signal import argrelextrema
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from calculate import *
from dist_from_target import calculate_dist_from_target
from make_graphs import *

n = 300  # number of points to be checked before and after the local maximum

LIM_ALL = [35, 50]
LIM_STATIC = [0, 10]

# Savitzky–Golay filter parameters
WINDOW_LENGTH = 151
POLYNOM_ORDER = 3

data_dict = {}


def get_data_from_excel(side, filename):
    to_import = ["T (sec)"]
    for coor in ["X", "Y", "Z"]:
        to_import.append(f"LEFT_SHOULDER {coor}")
        to_import.append(f"RIGHT_SHOULDER {coor}")
        to_import.append(f"{side}_HIP {coor}")
        to_import.append(f"{side}_ELBOW {coor}")
        to_import.append(f"{side}_WRIST {coor}")

    data = pd.read_excel(filename, usecols=to_import)
    return data


def get_mp_data(filename, side, time_interval):
    key = (filename, side, WINDOW_LENGTH, POLYNOM_ORDER)
    if key not in data_dict:
        data = get_data_from_excel(side, filename)
        data_dict[key] = clean_data(data, WINDOW_LENGTH, POLYNOM_ORDER)
    return data_dict[key]


def load_trials_from_json(angle_velocity, trials_filename):
    try:
        with open(trials_filename, 'r') as f:
            trials_data = json.load(f)
        trials = [[int(j) for j in item['trial']] for item in trials_data]
        max_v_indices = [item['max'] for item in trials_data]
        # Ensure indices are within bounds
        max_v_indices = [index for index in max_v_indices if index < len(angle_velocity)]
        trials = [[start, end] for start, end in trials if end < len(angle_velocity)]
    except FileNotFoundError:
        max_v_indices = argrelextrema(np.array(angle_velocity), np.greater_equal, order=n)[0]
        trials = [[int(j) for j in find_interval(angle_velocity, index)] for index in max_v_indices]
        trials_data = [{'max': int(max_v), 'trial': trial} for max_v, trial in zip(max_v_indices, trials)]
        with open(trials_filename, 'w') as f:
            json.dump(trials_data, f, indent=4)
    return trials, max_v_indices



def make_graph(filename, side, graph, time_interval, task):
    fig = plt.figure(figsize=(13, 7))
    if graph == 'compare sides':
        return compare_sides(fig, filename)

    data = get_mp_data(filename, side, time_interval)

    ribs = [calculate_rib_point(data, side, frame) for frame in range(len(data))]

    data[f"{side}_RIB X"] = [rib['x'] for rib in ribs]
    data[f"{side}_RIB Y"] = [rib['y'] for rib in ribs]
    data[f"{side}_RIB Z"] = [rib['z'] for rib in ribs]

    angle_data = make_vector_angle3D(data, side, ['ELBOW', 'SHOULDER', 'RIB'])
    time = list(data['T (sec)'].values)
    angle_velocity = calculate_velocity(time, angle_data)
    dist_from_target = calculate_dist_from_target(data, side)
    elbow_angle_data = make_vector_angle2D(data, side, ['WRIST', 'ELBOW', 'SHOULDER'])

    directory = os.path.dirname(filename)
    original_filename = os.path.splitext(os.path.basename(filename))[0]
    trials_filename = os.path.join(directory, f'{original_filename}_{side}.json')
    trials, max_v_indices = load_trials_from_json(angle_velocity, trials_filename)

    if graph == 'values':
        window_size = 5  # You can adjust the window size here if needed
        return make_values_graph(fig, data, trials, max_v_indices, angle_velocity, time,
                                 dist_from_target, angle_data, elbow_angle_data, time_interval, side)

    elbow_angle_data = make_vector_angle2D(data, side, ['WRIST', 'ELBOW', 'SHOULDER'])
    waves = []
    for interval in trials:
        if time[interval[0]] > time_interval[0] and time[interval[1]] < time_interval[1]:
            w = {'t': time[interval[0]: interval[1]],
                 'l': dist_from_target[interval[0]: interval[1]],
                 'v': angle_velocity[interval[0]: interval[1]],
                 'sa': angle_data[interval[0]: interval[1]],  # shoulder angle
                 'ea': elbow_angle_data[interval[0]: interval[1]],  # elbow angle
                 't-i': [round(time[interval[0]], 2), round(time[interval[1]], 2)]}
            waves.append(w)

    if graph == 'trials angle/time':
        return make_all_trials_graph(fig, waves)

    if graph == 'corr dist-angle':
        axs = fig.subplots(3, len(waves) // 3 + 1)
        axs = axs.flatten()

        for i in range(len(waves)):
            corr, _ = pearsonr(waves[i]['l'], waves[i]['sa'])
            axs[i].set_title(f'sec:{waves[i]["t-i"]}, corr:{round(corr, 3)}')
            axs[i].plot(range(len(waves[i]['l'])), [x / 10 for x in waves[i]['l']], label="dist from target/10")
            axs[i].plot(range(len(waves[i]['sa'])), waves[i]['sa'], label="shoulder angle")
            axs[i].set_xlabel('frames')
            axs[i].legend()

        fig.tight_layout(pad=1.0)
        return fig

    if graph == 'corr elbow-shoulder':
        return make_ES_coor_graph(fig, waves)

    directory = os.path.dirname(filename)
    param_filename = os.path.join(directory, f'param.csv')
    if graph == 'parameters':
        return make_parameters_graph(fig, side, angle_data, trials, time, time_interval, angle_velocity,
                                     dist_from_target, param_filename)

    tasks_avg = calculate_avg_task(waves)

    if graph == 'compare angle/time':
        return make_all_trials_graph(fig, tasks_avg)

    if graph == 'compare corr elbow-shoulder':
        return make_ES_coor_graph(fig, tasks_avg)

    if graph == 'compare parameters':
        return make_parameters_graph(fig, angle_data, trials, time, time_interval, angle_velocity, dist_from_target,
                                     param_filename)

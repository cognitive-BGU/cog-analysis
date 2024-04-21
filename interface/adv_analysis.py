import json

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
WINDOW_LENGTH = 101
POLYNOM_ORDER = 3

data_dict = {}

def get_data_from_excel(side, filename):
    to_import = ["T (sec)"]
    for coor in ["X", "Y"]:
        to_import.append("LEFT_SHOULDER " + coor)
        to_import.append("RIGHT_SHOULDER " + coor)
        to_import.append(side + "_HIP " + coor)
        to_import.append(side + "_ELBOW " + coor)
        to_import.append(side + "_WRIST " + coor)

    data = pd.read_excel(filename, usecols=to_import)
    # data = data[(data["T (sec)"] >= time_interval[0]) & (data["T (sec)"] <= time_interval[1])]
    return data


def get_mp_data(filename, side, time_interval):
    key = (filename, side, WINDOW_LENGTH, POLYNOM_ORDER)
    if key not in data_dict:
        data = get_data_from_excel(side, filename)
        data_dict[key] = clean_data(data, WINDOW_LENGTH, POLYNOM_ORDER)
    return data_dict[key]


def load_trials_from_json(angle_velocity):
    json_file = 'trials.json'
    try:
        with open(json_file, 'r') as f:
            trials_data = json.load(f)
        trials = [[int(j) for j in item['trial']] for item in trials_data]
        max_v_indices = [item['max'] for item in trials_data]
    except FileNotFoundError:
        max_v_indices = argrelextrema(np.array(angle_velocity), np.greater_equal, order=n)[0]
        trials = [[int(j) for j in find_interval(angle_velocity, index)] for index in max_v_indices]
        trials_data = [{'max': int(max_v), 'trial': trial} for max_v, trial in zip(max_v_indices, trials)]
        with open(json_file, 'w') as f:
            json.dump(trials_data, f, indent=4)
    print(trials, max_v_indices)
    return trials, max_v_indices


def make_graph(filename, angle, graph, time_interval, task):
    side = "LEFT" if angle == "Left" else "RIGHT"
    fig = plt.figure(figsize=(13, 7))
    if graph == 'compare sides':
        return compare_sides(fig, filename)

    data = get_mp_data(filename, side, time_interval)
    angle_data = make_vector_angle(data, side, ['WRIST', 'SHOULDER', 'HIP'])
    time = list(data['T (sec)'].values)
    angle_velocity = calculate_velocity(time, angle_data)
    dist_from_target = calculate_dist_from_target(data, side)
    trials, max_v_indices = load_trials_from_json(angle_velocity)

    if graph == 'values':
        return make_values_graph(fig, trials, max_v_indices, angle_velocity, time,
                                 dist_from_target, angle_data, time_interval)

    elbow_angle_data = make_vector_angle(data, side, ['WRIST', 'ELBOW', 'SHOULDER'])
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
        #  location-angle pairs + corr
        axs = fig.subplots(3, len(waves) // 3 + 1)
        axs = axs.flatten()

        for i in range(len(waves)):
            corr, _ = pearsonr(waves[i]['l'], waves[i]['sa'])
            axs[i].set_title(f'sec:{waves[i]["t-i"]}, corr:{round(corr, 3)}')
            axs[i].plot(range(len(waves[i]['l'])), [x / 10 for x in waves[i]['l']], label="dist from target/10")
            axs[i].plot(range(len(waves[i]['sa'])), waves[i]['sa'], label="shoulder angle")
            axs[i].set_xlabel('frames')
            # axs[i].set_ylabel('location')
            axs[i].legend()

        fig.tight_layout(pad=1.0)
        return fig

    if graph == 'corr elbow-shoulder':
        return make_ES_coor_graph(fig, waves)

    if graph == 'parameters':
        return make_parameters_graph(fig, side, angle_data, trials, time, time_interval, angle_velocity,
                                     dist_from_target)

    # compare tasks
    tasks_avg = calculate_avg_task(waves)

    if graph == 'compare angle/time':
        return make_all_trials_graph(fig, tasks_avg)

    if graph == 'compare corr elbow-shoulder':
        return make_ES_coor_graph(fig, tasks_avg)

    if graph == 'compare parameters':
        return make_parameters_graph(fig, angle_data, trials, time, time_interval, angle_velocity, dist_from_target)

# make_graph("../2023-07-02_01-01-012D.xlsx", "LeftShoulderAngle", 0, [0, 0])

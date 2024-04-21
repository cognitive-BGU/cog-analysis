import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema
from scipy.stats import pearsonr
import seaborn as sns

from save_param_table import save_as_csv

LINE_WIDTH = 1


def make_parameters_graph(fig, side, angle_data, trials, time, time_interval, angle_velocity, dist_from_target):
    # max_angels_indices = argrelextrema(np.array(angle_data), np.greater_equal, order=n)[0]
    # max_angels = [angle_data[i] for i in max_angels_indices]
    # print(trials)
    table = []
    for interval in trials:
        if time[interval[0]] > time_interval[0] and time[interval[1]] < time_interval[1]:
            interval_time = time[interval[0]: interval[1] + 1]
            interval_angle_data = angle_data[interval[0]: interval[1] + 1]
            interval_angle_velocity = angle_velocity[interval[0]: interval[1]]
            interval_dist_from_corner = dist_from_target[interval[0]: interval[1] + 1]

            max_angle = max(interval_angle_data)
            duration_frames = len(interval_time)
            duration_seconds = interval_time[-1] - interval_time[0]
            max_velocity = max(interval_angle_velocity)
            min_distance = min(interval_dist_from_corner)

            table.append(
                [interval_time[0], max_angle, duration_frames, duration_seconds, max_velocity, min_distance])

    max_angles = [row[1] for row in table]
    durations = [row[3] for row in table]
    max_velocities = [row[4] for row in table]
    min_distances = [row[5] for row in table]

    x_coords = range(len(table))
    axs = fig.subplots(nrows=2, ncols=2, sharex=True)
    axs[0, 0].bar(x_coords, max_angles, color='red', label='Max Angle')
    axs[0, 0].set_ylabel('angle [deg]')
    axs[0, 1].bar(x_coords, durations, color='blue', label='Trial Duration')
    axs[0, 1].set_ylabel('time [sec]')
    axs[1, 0].bar(x_coords, max_velocities, color='green', label='Max Velocity')
    axs[1, 0].set_ylabel('angle/time [deg/sec]')
    axs[1, 1].bar(x_coords, min_distances, color='orange', label='Min Distance')
    axs[1, 1].set_ylabel('coordinate [#]')
    save_as_csv(table, side)

    for ax in axs[-1]:
        ax.set_xticks(x_coords)
        ax.set_xticklabels([str(round(row[0], 2)) for row in table], fontsize=10)

    for ax in axs.flat:
        ax.legend()
    return fig


def make_values_graph(fig, trials, max_v_indices, angle_velocity, time, dist_from_target, angle_data, time_interval):
    ax1, ax2, ax3 = fig.subplots(3, 1)
    max_v = [angle_velocity[i] for i in max_v_indices]
    max_v_times = [time[i] for i in max_v_indices]

    times_to_draw = []
    v_data_to_draw = []
    l_data_to_draw = []
    angle_data_to_draw = []
    for interval in trials:
        for index in interval:
            times_to_draw.append(time[index])
            v_data_to_draw.append(angle_velocity[index])
            l_data_to_draw.append(dist_from_target[index])
            angle_data_to_draw.append(angle_data[index])

    # location
    ax1.set_title(f'Coordinate Distant from the target')
    ax1.set_ylabel('dist from the target [#]')
    ax1.plot(time, dist_from_target, label="dist", linewidth=LINE_WIDTH)
    ax1.set_xlim(time_interval)
    # y_min, y_max = min(dist_from_target), max(dist_from_target)
    # y_range = y_max - y_min
    # ax1.set_ylim([y_min - 0.1 * y_range, y_max + 0.1 * y_range])
    max_x_val = [dist_from_target[i] for i in max_v_indices]
    ax1.scatter(max_v_times, max_x_val, c='g', label="max{v(angle)}")
    ax1.scatter(times_to_draw, l_data_to_draw, c='r', marker="X", label="trial")
    ax1.legend()

    # v(x)
    ax2.set_title(f'Shoulder Angle Velocity')
    ax2.set_ylabel('angle/time [deg/sec]')
    ax2.plot(time[1:], angle_velocity, label="v(angle)", linewidth=LINE_WIDTH)
    ax2.scatter(max_v_times, max_v, c='g')
    ax2.set_xlim(time_interval)
    # y_min, y_max = min(angle_velocity), max(angle_velocity)
    # y_range = y_max - y_min
    # ax2.set_ylim([y_min - 0.1 * y_range, y_max + 0.1 * y_range])
    ax2.scatter(times_to_draw, v_data_to_draw, c='r', marker="X")
    ax2.legend()

    # angle
    ax3.set_title(f'Shoulder Angle')
    ax3.set_xlabel('Time [sec]')
    ax3.set_ylabel('Angle [deg]')
    ax3.plot(time, angle_data, label="shoulder angle", linewidth=LINE_WIDTH)
    ax3.set_xlim(time_interval)
    # y_min, y_max = min(angle_data), max(angle_data)
    # y_range = y_max - y_min
    # ax3.set_ylim([y_min - 0.1 * y_range, y_max + 0.1 * y_range])
    max_angle_val = [angle_data[i] for i in max_v_indices]
    ax3.scatter(max_v_times, max_angle_val, c='g')
    ax3.scatter(times_to_draw, angle_data_to_draw, c='r', marker="X")
    ax3.legend()
    return fig


def make_all_trials_graph(fig, waves):
    axs = fig.subplots()
    axs.set_title('Shoulder Angle vs. Frame for Each Trial')
    for w in waves:
        axs.plot(range(len(w['sa'])), w['sa'], label=str(w['t-i']))
    axs.set_xlabel('frames [#]')
    axs.set_ylabel('angles [deg]')
    axs.legend(title='trial seconds')
    return fig


def make_ES_coor_graph(fig, waves):
    axs = fig.subplots(3, len(waves) // 3 + 1)
    axs = axs.flatten()

    for i in range(len(waves)):
        corr, _ = pearsonr(waves[i]['ea'], waves[i]['sa'])
        axs[i].set_title(f'sec:{waves[i]["t-i"]}, corr:{round(corr, 3)}')
        axs[i].plot(range(len(waves[i]['ea'])), waves[i]['ea'], label="elbow angle")
        axs[i].plot(range(len(waves[i]['sa'])), waves[i]['sa'], label="shoulder angle")
        axs[i].set_xlabel('frames')
        # axs[i].set_ylabel('location')
        axs[i].legend()

    fig.tight_layout(pad=1.0)
    return fig



def compare_sides(fig, filename, param='Min Distance'):
    df = pd.read_csv(filename)
    tasks = df['Task'].unique()
    colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    axs = fig.subplots(1, len(tasks), sharey=False)  # Set sharey to False

    for ax, task, color in zip(axs, tasks, colors):
        data = df[df['Task'] == task]
        sns.stripplot(data=data, y=param, x='Side', jitter=True, marker='X', size=10, color=color, ax=ax)

        ax.set_title(f'{task}')
        ax.set_ylabel(param)

    axs[-1].set_xlabel('Side')

    fig.subplots_adjust(wspace=0.5)
    fig.suptitle(f'Comparison of {param} for Different Tasks and Sides')

    return fig


"""
def make_compare_graph(fig, waves):
    tasks_avg = calculate_avg_task(waves)

    axs = fig.subplots(3, 1)  # Create 3 subplots vertically
    axs[0].set_title('Shoulder Angle vs. Frame for Each Trial')

    tasks = ['apple', 'hat', 'parrot']
    for i, task in enumerate(tasks):
        task_waves = [wave for wave in tasks_avg if wave['task'] == task]
        for w in task_waves:
            axs[i].plot(range(len(w['sa'])), w['sa'], label=w['task'])
        axs[i].set_xlabel('frames [#]')
        axs[i].set_ylabel('angles [deg]')
        axs[i].legend(title='trial seconds')
    return fig
"""

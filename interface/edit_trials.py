import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from adv_analysis import get_mp_data, load_trials_from_json
from calculate import make_vector_angle, calculate_velocity
from dist_from_target import calculate_dist_from_target
from make_graphs import LINE_WIDTH

FONTSIZE = 14


def edit_trials(filename, angle, time_interval):
    click_count = 0
    trial_end = None
    def make_graph(filename, side, time_interval):
        fig = plt.figure(figsize=(13, 7))

        data = get_mp_data(filename, side, time_interval)
        angle_data = make_vector_angle(data, side, ['WRIST', 'SHOULDER', 'HIP'])
        time = list(data['T (sec)'].values)
        angle_velocity = calculate_velocity(time, angle_data)
        dist_from_target = calculate_dist_from_target(data, side)
        trials, max_v_indices = load_trials_from_json(angle_velocity)

        return make_values_graph(fig, trials, max_v_indices, angle_velocity, time,
                                 dist_from_target, angle_data, time_interval)

    def make_values_graph(fig, trials, max_v_indices, angle_velocity, time, dist_from_target, angle_data, time_interval):
        print("max_v_indices:", max_v_indices)

        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

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

        # v(x)
        ax1.set_title(f'Shoulder Angle Velocity')
        ax1.set_ylabel('angle/time [deg/sec]')
        ax1.plot(time[1:], angle_velocity, label="v(angle)", linewidth=LINE_WIDTH)
        ax1.scatter(max_v_times, max_v, c='g')
        ax1.set_xlim(time_interval)
        ax1.scatter(times_to_draw, v_data_to_draw, c='r', marker="X")
        ax1.legend()

        # angle
        ax2.set_title(f'Shoulder Angle')
        ax2.set_xlabel('Time [sec]')
        ax2.set_ylabel('Angle [deg]')
        ax2.plot(time, angle_data, label="shoulder angle", linewidth=LINE_WIDTH)
        ax2.set_xlim(time_interval)
        max_angle_val = [angle_data[i] for i in max_v_indices]
        ax2.scatter(max_v_times, max_angle_val, c='g')
        ax2.scatter(times_to_draw, angle_data_to_draw, c='r', marker="X")
        ax2.legend()
        return fig, ax1, ax2

    def onclick(event, fig, ax1, ax2):
        nonlocal click_count
        nonlocal trials, trial_end
        nonlocal max_v_indices

        if event.inaxes is not None:
            x_clicked = event.xdata
            nearest_index = np.abs(np.array(time) - x_clicked).argmin()
            print(f"Clicked at x = {x_clicked:.2f}")

            if event.button == 1:  # Left click

                if click_count == 0:
                    max_v_indices.append(nearest_index)
                    click_count += 1

                elif click_count == 1:
                    trial_end = nearest_index
                    click_count += 1

                elif click_count == 2:
                    trial_start = nearest_index
                    trials.append([min(trial_start, trial_end), max(trial_start, trial_end)])

                    fig.clear()
                    ax1.clear()
                    ax2.clear()
                    make_values_graph(fig, trials, max_v_indices, angle_velocity, time,
                                      dist_from_target, angle_data, time_interval)

                    plt.show()
                    click_count = 0

            if event.button == 3:  # Right click
                for index in max_v_indices:
                    if abs(nearest_index - index) <= 10:
                        # Remove the max_v_index and its associated trial
                        max_v_indices.remove(index)
                        for trial in trials:
                            if trial[0] <= index <= trial[1]:
                                trials.remove(trial)
                                break

                        fig.clear()
                        ax1.clear()
                        ax2.clear()
                        make_values_graph(fig, trials, max_v_indices, angle_velocity, time,
                                         dist_from_target, angle_data, time_interval)

                        plt.show()
                        break

    # Load your data and initialize global variables
    data = get_mp_data(filename, angle, time_interval)
    angle_data = make_vector_angle(data, angle, ['WRIST', 'SHOULDER', 'HIP'])
    time = list(data['T (sec)'].values)
    angle_velocity = calculate_velocity(time, angle_data)
    dist_from_target = calculate_dist_from_target(data, angle)
    trials, max_v_indices = load_trials_from_json(angle_velocity)

    matplotlib.use('TkAgg')  # Use TkAgg backend
    fig, ax1, ax2 = make_graph(filename, angle, time_interval)
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, fig, ax1, ax2))
    plt.show()
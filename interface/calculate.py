import numpy as np

tasks_trails = {
    'apple': [0, 1, 2, 3, 4, 5],
    'hat': [6, 7, 8, 9],
    'parrot': [10, 11, 12, 13]
}


def find_start(data, index):
    max_val = data[index]
    check_index = index - 1
    while check_index > 0:
        if max_val * 0.05 >= data[check_index]:
            return check_index
        check_index -= 1
    return 0


def find_end(data, index):
    max_val = data[index]
    check_index = index
    while check_index < len(data) - 1:
        if max_val * 0.05 >= data[check_index]:
            return check_index
        check_index += 1
    return len(data) - 1


def find_interval(data, index):
    return [find_start(data, index), find_end(data, index)]


def calculate_angle(a, b, c):
    # Calculate the vectors AB and BC
    ab = np.array([a[0] - b[0], a[1] - b[1], a[2] - b[2]])
    bc = np.array([c[0] - b[0], c[1] - b[1], c[2] - b[2]])

    # Calculate the dot product and magnitudes of the vectors
    dot_product = np.dot(ab, bc)
    magnitude_ab = np.linalg.norm(ab)
    magnitude_bc = np.linalg.norm(bc)

    # Calculate the angle in radians and then convert to degrees
    angle = np.arccos(dot_product / (magnitude_ab * magnitude_bc))
    angle = np.degrees(angle)

    return angle


def make_vector_angle(data, side, points):
    return [calculate_angle(
        [data[f"{side}_{points[0]} X"][frame], data[f"{side}_{points[0]} Y"][frame],
         data[f"{side}_{points[0]} Z"][frame]],
        [data[f"{side}_{points[1]} X"][frame], data[f"{side}_{points[1]} Y"][frame],
         data[f"{side}_{points[1]} Z"][frame]],
        [data[f"{side}_{points[2]} X"][frame], data[f"{side}_{points[2]} Y"][frame],
         data[f"{side}_{points[2]} Z"][frame]]
    ) for frame in range(len(data))]

def calculate_center_3D(pose1, pose2):
    center = {
        'x': (pose1['x'] + pose2['x']) / 2,
        'y': (pose1['y'] + pose2['y']) / 2,
        'z': (pose1['z'] + pose2['z']) / 2
    }
    return center

def calculate_velocity(time, angle_data):
    time_diff = np.diff(time)
    time_diff[time_diff == 0] = 0.01
    return np.diff(angle_data) / time_diff


def clean_data(data, window_length, polyorder):
    from scipy.signal import savgol_filter
    for column in data.columns:
        if column != "T (sec)":
            smoothed_column = savgol_filter(data[column], window_length, polyorder)
            data[column] = smoothed_column
    return data


def calculate_avg_task(waves):
    tasks_avg = []
    for task in tasks_trails:
        task_waves = [waves[i] for i in tasks_trails[task]]
        min_length = min(len(wave['l']) for wave in task_waves)
        avg_wave = {
            'l': [sum(wave['l'][i] for wave in task_waves) / len(task_waves) for i in range(min_length)],
            'v': [sum(wave['v'][i] for wave in task_waves) / len(task_waves) for i in range(min_length)],
            'sa': [sum(wave['sa'][i] for wave in task_waves) / len(task_waves) for i in range(min_length)],
            'ea': [sum(wave['ea'][i] for wave in task_waves) / len(task_waves) for i in range(min_length)],
            't-i': task
        }
        tasks_avg.append(avg_wave)
    return tasks_avg


# def calculate_dist_from_target(data, side):
# task_points = make_points_vector(data, side)
# location = [[data[f'{side}_WRIST X'][i] * 1920, data[f'{side}_WRIST Y'][i] * 1080] for i in range(len(data))]
# return [math.dist(dot, point) for dot, point in zip(location, task_points)]


# def make_points_vector(data, side):
#     points = []
#     for frame in range(len(data)):
#         point = calculate_task(data, frame, side)
#         points.append(point)
#     return points

# def calculate_task(data, frame, side):
#     tasks_intervals = [[100, 4700], [6500, 9950], [10100, 12000]]
#
#     shoulder = [data[f"{side}_SHOULDER X"][frame], data[f"{side}_SHOULDER Y"][frame]]
#     elbow = [data[f"{side}_ELBOW X"][frame], data[f"{side}_ELBOW Y"][frame]]
#     wrist = [data[f"{side}_WRIST X"][frame], data[f"{side}_WRIST Y"][frame]]
#
#     upper_arm_length = np.sqrt((shoulder[0] - elbow[0]) ** 2 + (shoulder[1] - elbow[1]) ** 2)
#     forearm_length = np.sqrt((elbow[0] - wrist[0]) ** 2 + (elbow[1] - wrist[1]) ** 2)
#     arm_length = 1.3 * (upper_arm_length + forearm_length)
#
#     angle_radians = np.deg2rad(50)
#
#     return (int(shoulder[0] + arm_length * np.cos(angle_radians)),
#             int(shoulder[1] - arm_length * np.sin(angle_radians)))

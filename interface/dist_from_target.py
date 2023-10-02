import numpy as np

FIRST_APPLE_ANGLE = 20
SECOND_APPLE_ANGLE = 35


def calculate_distance(data, landmark1, landmark2, i):
    x1 = data.loc[i, f"{landmark1} X"] * 1920
    y1 = data.loc[i, f"{landmark1} Y"] * 1080
    x2 = data.loc[i, f"{landmark2} X"] * 1920
    y2 = data.loc[i, f"{landmark2} Y"] * 1080
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def calculate_center(data, landmark1, landmark2, i):
    x1 = data.loc[i, f"{landmark1} X"] * 1920
    y1 = data.loc[i, f"{landmark1} Y"] * 1080
    x2 = data.loc[i, f"{landmark2} X"] * 1920
    y2 = data.loc[i, f"{landmark2} Y"] * 1080
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return center_x, center_y


def calculate_target_location(data, side):
    tasks_intervals = [[100, 7300], [7400, 10500], [10400, 14100]]
    task_location = []

    for i in range(len(data)):
        shoulder_distance = calculate_distance(data, "LEFT_SHOULDER", "RIGHT_SHOULDER", i)
        task_dist = shoulder_distance * 2.1
        shoulder = [data[f"{side}_SHOULDER X"][i] * 1920, data[f"{side}_SHOULDER Y"][i] * 1080]

        if tasks_intervals[0][0] < i < tasks_intervals[0][1]:  # apple
            angle_radians = np.deg2rad(FIRST_APPLE_ANGLE if side == 'LEFT' else 180 - FIRST_APPLE_ANGLE)
            # angle_radians = np.deg2rad(SECOND_APPLE_ANGLE if side == 'LEFT' else 180 - SECOND_APPLE_ANGLE)
            task_location.append([int(shoulder[0] + task_dist * np.cos(angle_radians)),
                                  int(shoulder[1] - task_dist * np.sin(angle_radians))])

        elif tasks_intervals[1][0] < i < tasks_intervals[1][1]:  # hat
            shoulder_center = calculate_center(data, "LEFT_SHOULDER", "RIGHT_SHOULDER", i)
            image_size = int(shoulder_distance / 3)
            task_location.append(
                [int(shoulder_center[0] - shoulder_distance * 1.25), int(shoulder_center[1] - image_size / 2)])

        elif tasks_intervals[2][0] < i < tasks_intervals[2][1]:  # parrot
            image_size = int(shoulder_distance / 2)
            task_location.append([int(shoulder[0] - image_size), int(shoulder[1] - image_size / 2)])

        else:
            task_location.append(None)

    return task_location


def calculate_dist_from_target(data, side):
    task_location = calculate_target_location(data, side)
    dist_from_target = []
    for i in range(len(data)):
        if task_location[i] == None:
            dist_from_target.append(None)
        else:
            wrist = [data[f"{side}_WRIST X"][i] * 1920, data[f"{side}_WRIST Y"][i] * 1080]
            dist_from_target.append(
                np.sqrt((wrist[0] - task_location[i][0]) ** 2 + (wrist[1] - task_location[i][1]) ** 2))
    return dist_from_target


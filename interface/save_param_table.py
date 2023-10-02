import csv
from calculate import tasks_trails
import os


def save_as_csv(table, side):
    filename = 'params.csv'
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        column_labels = ['Side', 'Task', 'Time', 'Max Angle', 'Duration (frames)', 'Duration (seconds)', 'Max Velocity',
                         'Min Distance']
        if not file_exists:
            writer.writerow(column_labels)

        for i, row in enumerate(table):
            task = next((k for k, v in tasks_trails.items() if i in v), None)
            row = [side, task] + row
            writer.writerow(row)

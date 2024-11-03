import os
import xlsxwriter
from tkinter import filedialog as fd
import cv2
import mediapipe as mp
import time
from tqdm import tqdm

folder = fd.askdirectory()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0, min_tracking_confidence=0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0, min_tracking_confidence=0)

start_time = time.time()

# Ask for start and end times for each file before processing
file_times = {}
for vid_file in os.listdir(folder):
    start_sec = int(input(f"Enter start second for {vid_file} (default is 0): ") or "0")
    end_sec = int(input(f"Enter end second for {vid_file} (default is video length): ") or "-1")
    file_times[vid_file] = (start_sec, end_sec)

for vid_file in os.listdir(folder):
    workbook = xlsxwriter.Workbook(vid_file[:-4] + '.xlsx')
    worksheet = workbook.add_worksheet()

    # Write header row
    worksheet.write_row(0, 0, ["T (sec)"] +
                        [f"{landmark.name} X" for landmark in mp_pose.PoseLandmark] +
                        [f"{landmark.name} Y" for landmark in mp_pose.PoseLandmark] +
                        [f"{landmark.name} Z" for landmark in mp_pose.PoseLandmark] +
                        [f"{landmark.name} X" for landmark in mp_hands.HandLandmark] +
                        [f"{landmark.name} Y" for landmark in mp_hands.HandLandmark] +
                        [f"{landmark.name} Z" for landmark in mp_hands.HandLandmark])

    cap = cv2.VideoCapture(folder + '\\' + vid_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"FPS for {vid_file}: {fps}")


    # Get start and end times from the dictionary
    start_sec, end_sec = file_times[vid_file]

    # If end_sec is -1, set it to video length
    if end_sec == -1:
        end_sec = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)

    total_frames = int((end_sec - start_sec) * fps)

    row = 1
    pbar = tqdm(total=total_frames, desc=vid_file)  # Initialize progress bar with total frame count

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        duration = frame_num / fps

        if duration < start_sec:
            continue
        if duration > end_sec:
            break
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        pose_results = pose.process(image)
        hands_results = hands.process(image)

        data_row = [duration]

        if pose_results.pose_landmarks:
            pose_landmarks = pose_results.pose_landmarks.landmark

            # Write data row
            data_row += [landmark.x for landmark in pose_landmarks] + [landmark.y for landmark in pose_landmarks] + [landmark.z for landmark in pose_landmarks]

        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                hand_data_row = data_row + [landmark.x for landmark in hand_landmarks.landmark] + [landmark.y for landmark in hand_landmarks.landmark] + [landmark.z for landmark in hand_landmarks.landmark]
                worksheet.write_row(row, 0, hand_data_row)
                row += 1
        else:
            data_row += [None] * (len(mp_hands.HandLandmark) * 3)
            worksheet.write_row(row, 0, data_row)
            row += 1

        pbar.update(1)  # Update progress bar

    pbar.close()  # Close progress bar when done with file

    workbook.close()
    cap.release()

pose.close()
hands.close()
cv2.destroyAllWindows()

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Done in {elapsed_time:.2f} seconds")

'''
import os
import xlsxwriter
from tkinter import filedialog as fd
import cv2
import mediapipe as mp
import time
from tqdm import tqdm

folder = fd.askdirectory()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0, min_tracking_confidence=0)

start_time = time.time()

# List of required landmarks
required_landmarks = [
    mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP,
    mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.RIGHT_ELBOW,
    mp_pose.PoseLandmark.LEFT_WRIST, mp_pose.PoseLandmark.RIGHT_WRIST,
    mp_pose.PoseLandmark.NOSE
]

# Ask for start and end times for each file before processing
file_times = {}
for vid_file in os.listdir(folder):
    start_sec = int(input(f"Enter start second for {vid_file} (default is 0): ") or "0")
    end_sec = int(input(f"Enter end second for {vid_file} (default is video length): ") or "-1")
    file_times[vid_file] = (start_sec, end_sec)

for vid_file in os.listdir(folder):
    workbook = xlsxwriter.Workbook(vid_file[:-4] + '.xlsx')
    worksheet = workbook.add_worksheet()

    # Write header row
    header = ["T (sec)"]
    for landmark in required_landmarks:
        landmark_name = landmark.name if '.' not in landmark.name else landmark.name.split('.')[1]
        header += [f"{landmark_name} X", f"{landmark_name} Y", f"{landmark_name} Z"]
    worksheet.write_row(0, 0, header)

    cap = cv2.VideoCapture(os.path.join(folder, vid_file))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Get start and end times from the dictionary
    start_sec, end_sec = file_times[vid_file]

    # If end_sec is -1, set it to video length
    if end_sec == -1:
        end_sec = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)

    total_frames = int((end_sec - start_sec) * fps)

    row = 1
    pbar = tqdm(total=total_frames, desc=vid_file)  # Initialize progress bar with total frame count

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        duration = frame_num / fps

        if duration < start_sec:
            continue
        if duration > end_sec:
            break
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        pose_results = pose.process(image)

        data_row = [duration]

        if pose_results.pose_landmarks:
            pose_landmarks = pose_results.pose_landmarks.landmark

            # Write data row for required pose landmarks
            for landmark in required_landmarks:
                data_row.extend([pose_landmarks[landmark].x, pose_landmarks[landmark].y, pose_landmarks[landmark].z])
        else:
            data_row += [None] * (len(required_landmarks) * 3)

        worksheet.write_row(row, 0, data_row)
        row += 1

        pbar.update(1)  # Update progress bar

    pbar.close()  # Close progress bar when done with file

    workbook.close()
    cap.release()

pose.close()
cv2.destroyAllWindows()

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Done in {elapsed_time:.2f} seconds")
'''
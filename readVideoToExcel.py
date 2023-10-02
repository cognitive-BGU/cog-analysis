import os
import xlsxwriter
from tkinter import filedialog as fd
import cv2
import mediapipe as mp
import time

folder = fd.askdirectory()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0, min_tracking_confidence=0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0, min_tracking_confidence=0)

start_time = time.time()

for vid_file in os.listdir(folder):
    workbook = xlsxwriter.Workbook(vid_file[:-4] + '.xlsx')
    worksheet = workbook.add_worksheet()

    # Write header row
    worksheet.write_row(0, 0, ["T (sec)"] +
        [f"{landmark.name} X" for landmark in mp_pose.PoseLandmark] + [
        f"{landmark.name} Y" for landmark in mp_pose.PoseLandmark] +
        [f"{landmark.name} X" for landmark in mp_hands.HandLandmark] +
        [f"{landmark.name} Y" for landmark in mp_hands.HandLandmark])

    cap = cv2.VideoCapture(folder + '\\' + vid_file)
    fps = cap.get(cv2.CAP_PROP_FPS)

    row = 1
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        duration = frame_num / fps

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        pose_results = pose.process(image)
        hands_results = hands.process(image)

        data_row = [duration]

        if pose_results.pose_landmarks:
            pose_landmarks = pose_results.pose_landmarks.landmark

            # Write data row
            data_row += [landmark.x for landmark in pose_landmarks] + [landmark.y for landmark in pose_landmarks]

        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                hand_data_row = data_row + [landmark.x for landmark in hand_landmarks.landmark] + [landmark.y for landmark in hand_landmarks.landmark]
                worksheet.write_row(row, 0, hand_data_row)
                row += 1
        else:
            data_row += [None] * (len(mp_hands.HandLandmark) * 2)
            worksheet.write_row(row, 0, data_row)
            row += 1

    workbook.close()
    cap.release()

pose.close()
hands.close()
cv2.destroyAllWindows()

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Done in {elapsed_time:.2f} seconds")

import cv2
import torch
import math
import cvzone
from ultralytics import YOLO
from collections import deque
import time

def integrate_accident_detection():
    # Initialize video capture
    cap = cv2.VideoCapture("D:/ACE/Assets/Test-1.mp4")

    # Load the model (ensure it's using the GPU if available)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO("D:/ACE/Assets/Accident_Detection_Accuracy_Model.pt")  # Use the correct path to your model
    model.to(device)

    # Class names for the detection
    classNames = ['Accident']

    # Video properties
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second of the video
    pre_accident_frames = int(fps * 15)  # Store 15 seconds before accident
    post_accident_frames = int(fps * 15)  # Store 15 seconds after accident

    # Buffer to store 15 seconds of frames before accident
    frame_buffer = deque(maxlen=pre_accident_frames)

    # Flag to start recording post-accident frames
    recording_post_accident = False
    post_accident_countdown = post_accident_frames

    # VideoWriter setup (to save video after accident is detected)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_file = "D:/ACE/Assets/accident_footage.avi"  # Change path to desired location
    out = None  # Placeholder for the video writer object

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            print("Failed to capture image. Exiting...")
            break

        # Resize the image to a size divisible by 32 (e.g., 640x640)
        img_resized = cv2.resize(img, (640, 640))

        # Convert image to RGB and add batch dimension
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)

        # Store frames in buffer before accident detection
        frame_buffer.append(img_resized)

        # Run inference using the model
        results = model(img_rgb, stream=True)

        accident_detected = False
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Draw bounding boxes and display confidence
                w, h = x2 - x1, y2 - y1
                cvzone.cornerRect(img_resized, (x1, y1, w, h))

                # Get confidence and class ID
                conf = math.ceil(box.conf[0] * 100) / 100
                cls = int(box.cls[0])

                # Display detected class and confidence
                cvzone.putTextRect(img_resized, f"{classNames[cls]} {conf}",
                                   (max(0, x1), max(35, y1)), scale=0.7, thickness=1)

                # Check if the detected class is 'Accident'
                if classNames[cls] == 'Accident':
                    accident_detected = True
                    print("Accident detected!")

                    # Save a photograph of the accident
                    cv2.imwrite("D:/ACE/Assets/accident_photo.png", img_resized)

                    if out is None:  # Initialize video writer once accident is detected
                        out = cv2.VideoWriter(output_file, fourcc, fps, (640, 640))

                    # Save the accident frame and the 15 seconds before
                    for frame in frame_buffer:
                        out.write(frame)  # Write buffered frames (pre-accident footage)

                    out.write(img_resized)  # Write the current accident frame
                    recording_post_accident = True

        # Handle recording post-accident frames for 15 seconds
        if recording_post_accident:
            post_accident_countdown -= 1
            out.write(img_resized)  # Save the post-accident frame
            if post_accident_countdown == 0:  # After saving 15 seconds post-accident
                print("Post-accident footage saved.")
                break  # End the loop after capturing all necessary footage

        # Display the frame
        cv2.imshow("Accident Detection", img_resized)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    if out:
        out.release()  # Save the video file
    cv2.destroyAllWindows()


if __name__ == "__main__":
    integrate_accident_detection()

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import webbrowser
from ultralytics import YOLO
import cv2
import cvzone
import math
import os

# Constants
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SUBJECT = "⚠️Alert: Accident Detected⚠️"
BODY_TEMPLATE = "⚠️⚠️⚠️Alert: Accident detected at this coordinate⚠️⚠️⚠️\n\n Coordinates:\n Latitude: {latitude}\n Longitude: {longitude}\n\nClick the link to view the live location: {url}"

ACCIDENT_IMAGE_PATH = 'accident_frame.jpg'
LATITUDE = 26.775495  # Use constant values for latitude
LONGITUDE = 75.876831  # Use constant values for longitude

def open_google_maps(latitude, longitude):
    url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    webbrowser.open(url)

ACCIDENT_IMAGE_PATH="accident_photo.png"
def send_email(sender_email, sender_password, receiver_emails, latitude, longitude):
    url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

    # Initialize the server variable
    server = None

    # Set up the SMTP server
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)  # Login to the SMTP server

        # Create a MIME multipart message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['Bcc'] = ', '.join(receiver_emails)  # Set BCC recipients
        msg['Subject'] = SUBJECT

        # Construct the message body
        body = BODY_TEMPLATE.format(latitude=latitude, longitude=longitude, url=url)
        msg.attach(MIMEText(body, 'plain'))

        # Attach the accident image
        try:
            with open(ACCIDENT_IMAGE_PATH, 'rb') as attachment:

                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(ACCIDENT_IMAGE_PATH)}')
                msg.attach(part)

        except FileNotFoundError:
            print(f"Attachment file not found: {ACCIDENT_IMAGE_PATH}")
            return

            # Send the email
        server.sendmail(sender_email, receiver_emails, msg.as_string())
        print("Email sent successfully.")

    except Exception as e:
        print("An error occurred while sending the email:", e)

    finally:
        # Check if the server was initialized and quit the connection
        if server:
            server.quit()

def integrate_accident_detection():
    cap = cv2.VideoCapture("D:\\ACE\\Assets\\Test-1.mp4")
    model = YOLO("D:\\ACE\\Assets\\Accident_Detection_Accuracy_Model.pt")
    classNames = ['Accident']
    frame_count = 0  # Counter to keep track of frames
    while True:
        success, img = cap.read()
        if not success:
            break
        results = model(img, stream=True)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1
                cvzone.cornerRect(img, (x1, y1, w, h))
                # Convert tensor to a float for rounding
                conf = float(box.conf[0])  # Convert to float first
                conf = round(conf * 100, 2)  # Now round it
                cls = int(box.cls[0])
                cvzone.putTextRect(img, f"{classNames[cls]} {conf}", (max(0, x1), max(35, y1)), scale=0.7, thickness=1)
                # Check if accident class is detected
                if classNames[cls] == 'Accident':
                    # Save the frame where accident is detected
                    frame_count += 1
                    cv2.imwrite(f'accident_frame.jpg', img)
                    # Use constant latitude and longitude values
                    send_email(sender_email, sender_password, receiver_emails, LATITUDE, LONGITUDE)
                    print('Accident occurred! Help is on the way.')
                    # Stop the program after sending the email
                    return
        cv2.imshow("Video", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


# Example usage

sender_email = "aceswiftsteadyfast@gmail.com"
sender_password = "yhry hpqh udmx drls"
receiver_emails = ["rathoreatri@gmail.com", "batraprabal04@gmail.com"]

# Start integrated accident detection and live location tracking
integrate_accident_detection()







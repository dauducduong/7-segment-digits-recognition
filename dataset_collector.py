import cv2
import os
import time
from roboflow import Roboflow
import requests
from typing import Optional
import shutil
import serial

output_dir = './collected_data'
arduino = serial.Serial('COM3', 19200)
captureNum = 0


def internet_connected():
    try:
        requests.get('https://www.google.com/', timeout=5)
        print("Internet connected!")
        return True
    except requests.ConnectionError:
        print("No internet connection!")
        return False


def serial_receive():
    if arduino.in_waiting != 0:
        data_to_read = arduino.readline().decode('utf-8').strip()
        if data_to_read.find('H') == -1:
            global captureNum
            captureNum = 1


def save_img(input_img, name):
    global output_dir
    image_name = os.path.join(output_dir, f"{name}.png")
    cv2.imwrite(image_name, input_img)


def capture_img(amount: Optional[int] = None):
    if amount is None:
        amount = 200
    global output_dir
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    video = cv2.VideoCapture(0)
    if video.isOpened():
        print("Đang chụp ảnh...")
        for idx in range(amount):
            ret, frame = video.read()
            if ret:
                save_img(frame, idx + 1)
                print(f"Đã lưu ảnh thứ {idx + 1}")
            time.sleep(0.5)
        print("Đã chụp ảnh xong!")
    video.release()


def capture_mode(mode, speed):
    time.sleep(3)
    data_to_send = "S" + speed
    arduino.write(data_to_send.encode())
    print(f"SENT {data_to_send}")
    if mode == 'lcd':
        data_to_send = "M1"
        arduino.write(data_to_send.encode())
    else:
        data_to_send = "M2"
        arduino.write(data_to_send.encode())
    print(f"SENT {data_to_send}")


def capture_img2(amount: Optional[int] = None):
    if amount is None:
        amount = 200
    global output_dir
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    video = cv2.VideoCapture(0)
    if video.isOpened():
        global captureNum
        print("Đang chụp ảnh...")
        idx = 0
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
        while idx < amount:
            serial_receive()
            if captureNum == 1:
                ret, frame = video.read()
                idx = idx + 1
                if ret:
                    save_img(frame, idx)
                    print(f"Đã lưu ảnh thứ {idx}")
                captureNum = 0
        print("Đã chụp ảnh xong!")
    video.release()


def upload_img(project_type):
    if internet_connected():
        if project_type == 'lcd':
            project_type = 'lcd-bikij'
        if project_type == 'led':
            project_type = 'led-vucww'
        rf = Roboflow(api_key="MUwywNoqnrVcjtQRg5Ux")
        project = rf.workspace('datn-iurme').project(project_type)
        print("Đang upload ảnh đã chụp lên Roboflow...")
        global output_dir
        for filename in os.listdir(output_dir):
            image_path = os.path.join(output_dir, filename)
            if os.path.isfile(image_path):
                project.upload(image_path)
                print(f"Đã upload ảnh {filename}")
        print("Đã upload xong!")


if __name__ == '__main__':
    capture_mode('lcd', '0.5')
    capture_img2(100)
    #upload_img('led')

import subprocess
from datetime import datetime
from threading import Lock
import cv2
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import prediction
import os
import serial
from ultralytics import YOLO
import csv
import shutil

time_sleep = 1
thread = None
thread_lock = Lock()
client_connect = False
arduino = serial.Serial('COM3', 19200)
app = Flask(__name__)
ngrok_token = "2eUdIDUuojIHgr4eltPVnYKesr5_2TRUpFnAMz5uotahsQ6UX"
app.config['SECRET_KEY'] = 'datndd'
socketio = SocketIO(app, cors_allowed_origins='*')
video = cv2.VideoCapture(0)
result_dir = "run_history"
captured_img_dir = "captured_img"
cmd = f"ngrok config add-authtoken {ngrok_token}"
subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
os.environ['NUMEXPR_MAX_THREADS'] = '20'
model_led = YOLO('runs/detect/latest_train_led/weights/best.pt')
model_led.to('cuda')
model_lcd = YOLO('runs/detect/latest_train_lcd/weights/best.pt')
model_lcd.to('cuda')
model_merge = YOLO('runs/detect/latest_train_merge/weights/best.pt')
model_merge.to('cuda')
predict_model = 1
temp_value = "..."
humid_value = "..."
real_num = "..."
updatenumChart = 0
if os.path.exists(captured_img_dir):
    shutil.rmtree(captured_img_dir)
os.makedirs(captured_img_dir)


def capture_img():
    frame = []
    if video.isOpened():
        check, frame = video.read()
        if not check:
            print("Camera is not opened!")
    return frame


def start_ngrok():
    cmd_command = "ngrok http --domain=warm-cute-hare.ngrok-free.app 5000"
    subprocess.Popen(cmd_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")


def get_current_date():
    now = datetime.now()
    return now.strftime("%d-%m-%Y")


def get_current_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def write_log(data):
    if data[2] != "...":
        data[2] = int(data[2])
    global predict_model, time_sleep
    file_path = result_dir + "/" + get_current_date() + ".csv"
    if not (os.path.exists(file_path)):
        header = ['TIME', 'MODE', 'SPEED', 'TEMPERATURE', 'HUMIDITY', 'PREDICTED VALUE', 'REAL VALUE']
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
    if predict_model == 1:
        mode = "LCD"
    else:
        mode = "LED"
    new_line = [get_current_time(), mode, time_sleep, data[1], data[2], data[0], real_num]
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_line)


def save_img(img, i):
    global captured_img_dir
    image_name = os.path.join(captured_img_dir, f"{i}.png")
    cv2.imwrite(image_name, img)


def start_arduino():
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    data_to_send = 'R'
    arduino.write(data_to_send.encode())


def background_thread():
    global time_sleep, predict_model, temp_value, humid_value, updatenumChart
    i = 0
    start_ngrok()
    start_arduino()
    lasted_value = ""
    while True:
        serial_receive()
        img = capture_img()
        if predict_model == 1:
            value = prediction.get_predict(model_lcd, img, True)
        else:
            value = prediction.get_predict(model_led, img, True)
        if value != '' and updatenumChart == 1:
            save_img(img, i)
            i = i + 1
            if lasted_value != value:
                data_list = [value, temp_value, humid_value]
                write_log(data_list)
                lasted_value = value
        socketio.emit('updateData',
                      {'value': value, "time": get_current_time(), "date": get_current_date(),
                       "mode": predict_model,
                       "speed": time_sleep, "temp": temp_value, "humid": humid_value,
                       "updatenumChart": updatenumChart})
        updatenumChart = 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict_mode', methods=['POST'])
def predict_mode():
    data = request.form.get('data')
    global predict_model
    predict_model = int(data)
    if predict_model == 1:
        data_to_send = "M1"
        arduino.write(data_to_send.encode())
    else:
        data_to_send = "M2"
        arduino.write(data_to_send.encode())
    return data


@app.route('/run_speed', methods=['POST'])
def run_speed():
    data = request.form.get('data')
    global time_sleep
    time_sleep = float(data)
    data_to_send = "S" + data
    arduino.write(data_to_send.encode())
    return data


@socketio.on('connect')
def connect():
    print('Client connected')
    global client_connect
    client_connect = True


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')
    global client_connect
    client_connect = False


def serial_receive():
    if arduino.in_waiting != 0:
        data_to_read = arduino.readline().decode('utf-8').strip()
        arduino.reset_input_buffer()
        if data_to_read.find('H') == -1:
            global updatenumChart, real_num
            updatenumChart = 1
            real_num = data_to_read[1:]
        else:
            global temp_value, humid_value
            separator_index = data_to_read.find("H")
            temp_str = data_to_read[:separator_index]
            temp_value = temp_str.replace("T", "")
            humid_str = data_to_read[separator_index:]
            humid_value = humid_str.replace("H", "")


with thread_lock:
    if thread is None:
        thread = socketio.start_background_task(background_thread)

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)

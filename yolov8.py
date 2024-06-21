from ultralytics import YOLO
from roboflow import Roboflow
import shutil
import os
import requests

api_key = "MUwywNoqnrVcjtQRg5Ux"
workspace = "datn-iurme"
project = "led-vucww"
ver = 2
yaml_path = 'datasets/data.yaml'


def internet_connected():
    try:
        requests.get('https://www.google.com/', timeout=5)
        print("Internet connected!")
        return True
    except requests.ConnectionError:
        print("No internet connection!")
        return False


def print_rbf_info():
    global api_key, workspace, project, ver
    print(f"Workspace: {workspace}")
    print(f"Project: {project}")
    print(f"Dataset version: {ver}")


#Download datasets from roboflow
def download_datasets(project_type, ver_num):
    if internet_connected():
        global api_key, workspace, project, ver
        if project_type == 'lcd':
            project = 'lcd-bikij'
        if project_type == 'led':
            project = 'led-vucww'
        ver = ver_num
        print_rbf_info()
        location = './datasets'
        if os.path.exists(location):
            shutil.rmtree(location)
        rf = Roboflow(api_key=api_key)
        project1 = rf.workspace(workspace).project(project)
        version = project1.version(ver)
        version.download("yolov8", location=location, overwrite=1)
        global yaml_path
        update_yaml(yaml_path)


def update_yaml(file_path):
    new_3_line = ["test: ./test/images\n", "train: ./train/images\n", "val: ./valid/images\n"]
    with open(file_path, 'r') as file:
        lines = file.readlines()
    start_index = len(lines) - 3
    if start_index < 0:
        start_index = 0
    lines[start_index:] = new_3_line[0:]
    with open(file_path, 'w') as file:
        file.write(''.join(lines))


def train_model(project_type, epochs):
    location = ''
    name = ''
    if project_type == 'merge':
        location = './runs/detect/latest_train_merge'
        name = 'latest_train_merge'
    if project_type == 'led':
        location = './runs/detect/latest_train_led'
        name = 'latest_train_led'
    if project_type == 'lcd':
        location = './runs/detect/latest_train_lcd'
        name = 'latest_train_lcd'
    if project_type == 'else':
        location = './runs/detect/latest_train_else'
        name = 'latest_train_else'
    if os.path.exists(location):
        shutil.rmtree(location)
    global yaml_path
    model = YOLO('yolov8n.pt')
    model.train(data=yaml_path, epochs=epochs, name=name, exist_ok=True)
    #model.export(format='onnx')


def upload_model(project_type, ver_num):
    if internet_connected():
        global api_key, workspace, project, ver
        location = ""
        if project_type == 'lcd':
            project = 'lcd-bikij'
            location = 'runs/detect/latest_train_lcd/weights/'
        if project_type == 'led':
            project = 'led-vucww'
            location = './runs/detect/latest_train_led/weights/'
        ver = ver_num
        rf = Roboflow(api_key=api_key)
        project1 = rf.workspace(workspace).project(project)
        version = project1.version(ver)
        version.deploy("yolov8", location, "best.pt")
        print("Model deployed!")


if __name__ == '__main__':
    #download_datasets('lcd', 12)
    train_model('else', 50)
    #upload_model('lcd', 12)

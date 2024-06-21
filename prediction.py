def sort_lefttoright(input_cls, input_conf, input_x1, input_x2, input_y1, input_y2):
    leng = len(input_cls)
    output_cls = []
    output_x1 = []
    output_x2 = []
    output_conf = []
    output_y1 = []
    output_y2 = []
    for index in range(leng):
        min_value = min(input_x1)
        min_index = input_x1.index(min_value)
        output_x1.append(input_x1.pop(min_index))
        output_x2.append(input_x2.pop(min_index))
        output_cls.append(input_cls.pop(min_index))
        output_conf.append(input_conf.pop(min_index))
        output_y1.append(input_y1.pop(min_index))
        output_y2.append(input_y2.pop(min_index))
    return output_cls, output_conf, output_x1, output_x2, output_y1, output_y2


def remove_overlapping(input_cls, input_conf, input_x1, input_x2, input_y1, input_y2):
    idx = -1
    while True:
        idx = idx + 1
        if not input_x1:
            break
        if idx == len(input_x1) - 1:
            break
        if 3 >= input_x1[idx] - input_x1[idx + 1] >= -3:
            pop_index = idx
            if input_conf[idx] > input_conf[idx + 1]:
                pop_index = idx + 1
            input_cls.pop(pop_index)
            input_conf.pop(pop_index)
            input_x1.pop(pop_index)
            input_x2.pop(pop_index)
            input_y1.pop(pop_index)
            input_y2.pop(pop_index)
            idx -= 1
    return input_cls, input_conf, input_x1, input_x2, input_y1, input_y2


def remove_excess_number(input_cls, input_x1, input_x2, input_y1, input_y2):
    if len(input_cls) > 1:
        if input_cls[0] == 1:
            if input_x2[0] - input_x1[1] > (input_x2[1]-input_x1[1])/5:
                input_cls.pop(0)
                input_x1.pop(0)
                input_x2.pop(0)
                input_y1.pop(0)
                input_y2.pop(0)
    return input_cls, input_y1, input_y2


def limit_digit(input_cls, input_y1, input_y2):
    leng = len(input_cls)
    if leng > 4:
        y_top = (input_y1[1] + input_y1[2] + input_y1[3]) / 3
        y_bot = (input_y2[1] + input_y2[2] + input_y2[3]) / 3
        output_cls = []
        for i in range(leng):
            if y_top - 7 < input_y1[i] < y_top + 7 and y_bot - 7 < input_y2[i] < y_bot + 7:
                output_cls.append(input_cls[i])
                if len(output_cls) == 4:
                    return output_cls
        return output_cls
    else:
        return input_cls


def get_predict(model, source, show):
    results = model.predict(source=source, show=show, imgsz=320, iou=0.2, verbose=True)
    rst = ""
    for result in results:
        length = len(result.boxes.cls.cpu().numpy())
        list_cls = []
        list_x1 = []
        list_x2 = []
        list_conf = []
        list_y1 = []
        list_y2 = []
        for i in range(length):
            list_cls.append(int(result.boxes.cls[i].cpu().numpy()))
            list_x1.append(round(float(result.boxes.xyxy[i][0].cpu().numpy()), 4))
            list_x2.append(round(float(result.boxes.xyxy[i][2].cpu().numpy()), 4))
            list_y1.append(round(float(result.boxes.xyxy[i][1].cpu().numpy()), 4))
            list_y2.append(round(float(result.boxes.xyxy[i][3].cpu().numpy()), 4))
            list_conf.append(round(float(result.boxes.conf[i].cpu().numpy()), 4))
        sorted_cls, sorted_conf, sorted_x1, sorted_x2, sorted_y1, sorted_y2 = sort_lefttoright(list_cls, list_conf,
                                                                                               list_x1, list_x2,
                                                                                               list_y1,
                                                                                               list_y2)
        clean_cls, clean_conf, clean_x1, clean_x2, clean_y1, clean_y2 = remove_overlapping(sorted_cls, sorted_conf, sorted_x1, sorted_x2, sorted_y1, sorted_y2)
        clear_cls, clear_y1, clear_y2 = remove_excess_number(clean_cls, clean_x1, clean_x2, clean_y1, clean_y2)
        final_cls = limit_digit(clear_cls, clear_y1, clear_y2)
        for ele in final_cls:
            rst += str(ele)
    return rst

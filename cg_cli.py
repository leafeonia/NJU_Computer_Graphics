#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import cg_algorithms as alg
import numpy as np
from PIL import Image


if __name__ == '__main__':
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    item_dict = {}
    pen_color = np.zeros(3, np.uint8)
    width = 0
    height = 0

    with open(input_file, 'r') as fp:
        line = fp.readline()
        while line:
            line = line.strip().split(' ')
            if line[0] == 'resetCanvas':
                width = int(line[1])
                height = int(line[2])
                item_dict = {}
            elif line[0] == 'saveCanvas':
                save_name = line[1]
                canvas = np.zeros([height, width, 3], np.uint8)
                canvas.fill(255)
                for item_type, p_list, algorithm, color in item_dict.values():
                    if item_type == 'line':
                        pixels = alg.draw_line(p_list, algorithm)
                        if len(pixels) > 0:
                            for x, y in pixels:
                                canvas[height - 1 - y, x] = color
                    elif item_type == 'polygon':
                        pixels = alg.draw_polygon(p_list, algorithm)
                        for x, y in pixels:
                            canvas[height - 1 - y, x] = color
                    elif item_type == 'ellipse':
                        pixels = alg.draw_ellipse(p_list)
                        for x, y in pixels:
                            canvas[height - 1 - y, x] = color
                    elif item_type == 'curve':
                        pixels = alg.draw_curve(p_list, algorithm)
                        for x, y in pixels:
                            canvas[height - 1 - y, x] = color
                Image.fromarray(canvas).save(os.path.join(output_dir, save_name + '.bmp'), 'bmp')
            elif line[0] == 'setColor':
                pen_color[0] = int(line[1])
                pen_color[1] = int(line[2])
                pen_color[2] = int(line[3])
            elif line[0] == 'drawLine':
                item_id = line[1]
                x0 = int(line[2])
                y0 = int(line[3])
                x1 = int(line[4])
                y1 = int(line[5])
                algorithm = line[6]
                item_dict[item_id] = ['line', [[x0, y0], [x1, y1]], algorithm, np.array(pen_color)]
            elif line[0] == 'drawPolygon':
                item_id = line[1]
                p_list = []
                for i in range(2, len(line) - 1, 2):
                    p_list.append([int(line[i]), int(line[i + 1])])
                algorithm = line[len(line) - 1]
                item_dict[item_id] = ['polygon', p_list, algorithm, np.array(pen_color)]
            elif line[0] == 'drawEllipse':
                item_id = line[1]
                x0 = int(line[2])
                y0 = int(line[3])
                x1 = int(line[4])
                y1 = int(line[5])
                item_dict[item_id] = ['ellipse', [[x0, y0], [x1, y1]], 'dummy', np.array(pen_color)]
            elif line[0] == 'drawCurve':
                item_id = line[1]
                p_list = []
                for i in range(2, len(line) - 1, 2):
                    p_list.append([int(line[i]), int(line[i+1])])
                algorithm = line[len(line) - 1]
                item_dict[item_id] = ['curve', p_list, algorithm, np.array(pen_color)]
            elif line[0] == 'translate':
                item_id = line[1]
                dx = int(line[2])
                dy = int(line[3])
                item_dict[item_id][1] = alg.translate(item_dict[item_id][1], dx, dy)
            elif line[0] == 'clip':
                item_id = line[1]
                x0 = int(line[2])
                y0 = int(line[3])
                x1 = int(line[4])
                y1 = int(line[5])
                algorithm = line[6]
                item_dict[item_id][1] = alg.clip(item_dict[item_id][1], x0, y0, x1, y1, algorithm)
            elif line[0] == 'scale':
                item_id = line[1]
                x = int(line[2])
                y = int(line[3])
                s = float(line[4])
                item_dict[item_id][1] = alg.scale(item_dict[item_id][1], x, y, s)
            elif line[0] == 'rotate':
                item_id = line[1]
                x = int(line[2])
                y = int(line[3])
                r = int(line[4])
                item_dict[item_id][1] = alg.rotate(item_dict[item_id][1], x, y, -r)
            line = fp.readline()


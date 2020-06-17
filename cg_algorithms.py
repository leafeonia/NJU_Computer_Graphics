#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import copy
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if len(p_list) < 2:
        return []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        result.append((x0, y0))
        length = max(abs(x1 - x0), abs(y1 - y0))
        if length > 0:
            dx = (x1 - x0) / length
            dy = (y1 - y0) / length
            x, y = x0, y0
            for i in range(length):
                x = x + dx
                y = y + dy
                result.append((int(x), int(y)))

    elif algorithm == 'Bresenham':
        result.append((x0, y0))
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        if dy > dx:
            swap = 1
            dx, dy = dy, dx
        else:
            swap = 0
        if x1 > x0:
            sx = 1
        else:
            sx = -1
        if y1 > y0:
            sy = 1
        else:
            sy = -1
        p = 2 * dy - dx
        x, y = x0, y0
        for i in range(dx):
            if p >= 0:
                if swap:
                    x = x + sx
                else:
                    y = y + sy
                p = p + 2 * (dy - dx)
            else:
                p = p + 2 * dy
            if swap:
                y = y + sy
            else:
                x = x + sx
            result.append((x, y))

    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result

def addPoint(result, centerx, centery, x, y):
    result.append((centerx + x, centery + y))
    result.append((centerx - x, centery + y))
    result.append((centerx + x, centery - y))
    result.append((centerx - x, centery - y))

def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    centerx = (int)((x0 + x1) / 2)
    centery = (int)((y0 + y1) / 2)
    rx = (int)(abs((x1 - x0) / 2))
    ry = (int)(abs((y1 - y0) / 2))

    if ry > rx:
        rx, ry = ry, rx
        swap = 1
    else:
        swap = 0

    rx2 = rx * rx
    ry2 = ry * ry

    x = 0
    y = ry

    p = ry2 - rx2 * ry + rx2 / 4
    while ry2 * x < rx2 * y:
        x = x + 1
        if p < 0:
            p = p + 2 * ry2 * x + ry2
        else:
            y = y - 1
            p = p + 2 * ry2 * x - 2 * rx2 * y + ry2
        if swap:
            addPoint(result, centerx, centery, y, x)
        else:
            addPoint(result, centerx, centery, x, y)

    p = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        y = y - 1
        if p < 0:
            x = x + 1
            p = p + 2 * ry2 * x - 2 * rx2 * y + rx2
        else:
            p = p - 2 * rx2 * y + rx2
        if swap:
            addPoint(result, centerx, centery, y, x)
        else:
            addPoint(result, centerx, centery, x, y)

    return result

def fac(n):
    ret = 1
    for i in range(1, n+1):
        ret *= i
    return ret


def bezier(n, i, t):
    return fac(n) / (fac(n - i) * fac(i)) * pow(1 - t, n - i) * pow(t, i)


def N(i, j, t):
    if j == 0:
        if i <= t and t < i+1:
            return 1
        return 0
    return (t-i) / j * N(i, j-1, t) + (i+j+1-t) / j * N(i+1, j-1, t)


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    if algorithm == 'Bezier':
        t = 0
        num = 256 * len(p_list)
        interval = 1 / num
        for i in range(num):
            x = y = 0
            for j, point in enumerate(p_list):
                coeff = bezier(len(p_list) - 1, j, t)
                x += coeff * point[0]
                y += coeff * point[1]
            t += interval
            result.append((int(x), int(y)))
    elif algorithm == 'B-spline':
        t = 3
        m = 3 + len(p_list)
        interval = 1 / (64 * len(p_list))
        while t < m - 3:
            x = y = 0
            for i, point in enumerate(p_list):
                coeff = N(i, 3, t)
                x += point[0] * coeff
                y += point[1] * coeff
            t += interval
            result.append((int(x), int(y)))
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """

    return list(map(lambda p: [p[0] + dx, p[1] + dy], p_list))


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return list(map(lambda p: [int(x + (p[0]-x) * math.cos(r * math.pi / 180) - (p[1]-y) * math.sin(r * math.pi / 180)),
                               int(y + (p[0]-x) * math.sin(r * math.pi / 180) + (p[1]-y) * math.cos(r * math.pi / 180))], p_list))


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return list(map(lambda p: [int(p[0] * s + x * (1-s)), int(p[1] * s + y * (1-s))], p_list))

def cohen_encoder(point, x_min, y_min, x_max, y_max):
    [x, y] = point
    code = 0
    if x < x_min:
        code += 1
    if x > x_max:
        code += 2
    if y < y_min:
        code += 4
    if y > y_max:
        code += 8
    return code

def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    if algorithm == 'Cohen-Sutherland':
        a, b = p_list[0], p_list[1]
        x1, y1, x2, y2 = a[0], a[1], b[0], b[1]
        x, y = x1, y1
        code1 = cohen_encoder(a, x_min, y_min, x_max, y_max)
        code2 = cohen_encoder(b, x_min, y_min, x_max, y_max)
        while code1 or code2:
            if code1 & code2:
                return ''
            code = [code1, code2][code1 == 0]
            if code & 1:
                x = x_min
                y = int(y1 + (y2 - y1)*(x_min - x1)/(x2 - x1))
            elif code & 2:
                x = x_max
                y = int(y1 + (y2 - y1)*(x_max - x1)/(x2 - x1))
            elif code & 4:
                y = y_min
                x = int(x1 + (x2 - x1)*(y_min - y1)/(y2 - y1))
            elif code & 8:
                y = y_max
                x = int(x1 + (x2 - x1)*(y_max - y1)/(y2 - y1))
            if code == code1:
                x1, y1 = x, y
                code1 = cohen_encoder([x1, y1], x_min, y_min, x_max, y_max)
            else:
                x2, y2 = x, y
                code2 = cohen_encoder([x2, y2], x_min, y_min, x_max, y_max)
        return [[x1, y1], [x2, y2]]

    elif algorithm == 'Liang-Barsky':
        a, b = p_list[0], p_list[1]
        p = [a[0] - b[0], b[0] - a[0], a[1] - b[1], b[1] - a[1]]
        q = [a[0] - x_min, x_max - a[0], a[1] - y_min, y_max - a[1]]
        umax = 0
        umin = 1
        if p[0] == 0:
            if q[0] < 0 or q[1] < 0:
                return ''
            for i in range(2, 4):
                if p[i] < 0:
                    umax = max(umax, q[i] / p[i])
                elif p[i] > 0:
                    umin = min(umin, q[i] / p[i])
        elif p[2] == 0:
            if q[2] < 0 or q[3] < 0:
                return ''
            for i in range(2):
                if p[i] < 0:
                    umax = max(umax, q[i] / p[i])
                elif p[i] > 0:
                    umin = min(umin, q[i] / p[i])
        else:
            for i in range(4):
                if p[i] < 0:
                    umax = max(umax, q[i] / p[i])
                elif p[i] > 0:
                    umin = min(umin, q[i] / p[i])
        if umax > umin:
            return ''
        else:
            return [[int(a[0] + umax * p[1]), int(a[1] + umax * p[3])], [int(a[0] + umin * p[1]), int(a[1] + umin * p[3])]]


def inside(sp, ep, cp):  # startPoint, endPoint, checkPoint
    return (ep[0] - sp[0]) * (cp[1] - sp[1]) - (ep[1] - sp[1]) * (cp[0] - sp[0]) > 0

def intersectPoint(p1, p2, p3, p4):
    x1, x2, x3, x4, y1, y2, y3, y4 = p1[0], p2[0], p3[0], p4[0], p1[1], p2[1], p3[1], p4[1]
    return [int( ((x1*y2 - y1*x2) * (x3-x4) - (x1-x2) * (x3*y4 - y3*x4)) / ((x1-x2) * (y3-y4) - (y1-y2) * (x3-x4)) ),
            int( ((x1*y2 - y1*x2) * (y3-y4) - (y1-y2) * (x3*y4 - y3*x4)) / ((x1-x2) * (y3-y4) - (y1-y2) * (x3-x4)) )]

def clipPolygon(p_list, x_min, y_min, x_max, y_max):
    vectors = [ [[x_min, y_max], [x_min, y_min]], [[x_min, y_min], [x_max, y_min]], [[x_max, y_min], [x_max, y_max]], [[x_max, y_max], [x_min, y_max]]]
    # cannot use copy.deepcopy() in this file
    returnList = copy.deepcopy(p_list)
    for v in vectors:
        tempList = []
        for i in range(len(returnList)):
            start, end = returnList[i - 1], returnList[i]
            epInside = inside(v[0], v[1], end)
            spInside = inside(v[0], v[1], start)
            if spInside and epInside:
                tempList.append(end)
            elif spInside and not epInside:
                tempList.append(intersectPoint(start, end, v[0], v[1]))
            elif not spInside and epInside:
                tempList.append(intersectPoint(start, end, v[0], v[1]))
                tempList.append(end)
        returnList = copy.deepcopy(tempList)
    return returnList

def fillPolygon(p_list, x_min, y_min, x_max, y_max):
    line_list = []
    returnList = []
    for i in range(len(p_list)):
        line_list.append([p_list[i - 1], p_list[i]])
    for y in range(y_min, y_max):
        intersect_x = []
        for line in line_list:
            if y > max(line[0][1], line[1][1]) or y < min(line[0][1], line[1][1]):
                continue
            if line[0][1] == line[1][1]:
                continue
            intersect_x.append(intersectPoint([x_min, y], [x_max, y], line[0], line[1])[0])
        # remove overlap x
        intersect_x = list(dict.fromkeys(intersect_x))
        for i in range(len(intersect_x) - 1):
            if intersect_x[i] > intersect_x[i + 1]:
                intersect_x[i], intersect_x[i + 1] = intersect_x[i + 1], intersect_x[i]

        for i in range(0, len(intersect_x) - 1, 2):
            for x in range(intersect_x[i], intersect_x[i + 1]):
                returnList.append([x, y])
    return returnList

def fillEllipse(item_pixels, y_min, y_max):
    dic = {}
    returnList = []
    for y in range(y_min, y_max + 1):
        dic[y] = []
    for pixel in item_pixels:
        dic[pixel[1]].append(pixel[0])
    for y in range(y_min, y_max):
        if len(dic[y]) > 1:
            for x in range(dic[y][1], dic[y][0]):
                returnList.append([x, y])
    return returnList

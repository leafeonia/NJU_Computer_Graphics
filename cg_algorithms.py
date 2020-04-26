#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
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
        len = max(abs(x1 - x0), abs(y1 - y0))
        if len > 0:
            dx = (x1 - x0) / len
            dy = (y1 - y0) / len
            x, y = x0, y0
            for i in range(len):
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

def bspline(u):
    if 0 <= u and u < 1:
        return pow(u,3) / 6
    elif 1 <= u and u < 2:
        return (-3 * pow(u-1, 3) + 3 * pow(u-1, 2) + 3*(u-1) + 1) / 6
    elif 2 <= u and u < 3:
        return (3 * pow(u-2, 3) - 6 * pow(u-2, 2) + 4) / 6
    elif 3 <= u and u < 4:
        return pow(4-u, 3) / 6
    return 0

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
        print('FA')
        num = 256 * len(p_list)
        interval = 1 / num
        u = 3
        while u < len(p_list) + 1:
            x = y = 0
            for j, point in enumerate(p_list):
                coeff = bspline(u - j)
                x += coeff * point[0]
                y += coeff * point[1]
            u += interval
            result.append((int(x), int(y)))
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    ret = []
    for item in p_list:
        ret.append([item[0] + dx, item[1] + dy])
    return ret


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass

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




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


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    pass


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


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
    pass

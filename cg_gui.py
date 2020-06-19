#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math
import copy

class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.color = Qt.black
        self.fill_color = Qt.green
        self.line_width = 2
        self.paintingPolygon = False
        self.paintingCurve = False
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.copied_item = None
        self.clipPoint1 = [-1, -1]
        self.clipPoint2 = [-1, -1]
        self.translateOrigin = [-1, -1]

        self.temp_plist = []
        self.corePoint = [-1, -1]

        # scale
        self.scalePoint = [-1, -1]

        # rotate
        self.rotatePoint = [-1, -1]

        # helpers
        self.helperPoints_item = MyItem("helperPoints", "helperPoints", [])
        self.helperLines_item = MyItem("helperLines", "helperLines", [])
        self.helperPoints_item.setZValue(1)
        self.helperLines_item.setZValue(1)
        self.scene().addItem(self.helperPoints_item)
        self.scene().addItem(self.helperLines_item)

    def clearSettings(self):
        self.helperPoints_item.p_list = []
        self.helperLines_item.p_list = []
        self.translateOrigin = self.corePoint = self.scalePoint = self.rotatePoint = self.clipPoint1 = self.clipPoint2 = [-1, -1]

    def checkHelper(self):
        if self.status == 'rotate':
            if self.corePoint != [-1, -1]:
                self.helperPoints_item.p_list.append(self.corePoint)
        elif self.status == 'scale':
            if self.scalePoint != [-1, -1]:
                self.helperPoints_item.p_list.append(self.scalePoint)
                if self.temp_item is not None:
                    self.helperPoints_item.p_list.append(self.temp_item.corePoint())
        elif self.status == 'clip':
            if self.clipPoint1 != [-1, -1]:
                self.helperPoints_item.p_list.append(self.clipPoint1)
            if self.clipPoint2 != [-1, -1]:
                self.helperPoints_item.p_list.append(self.clipPoint2)
                self.helperLines_item.p_list = []
                xmin = min(self.clipPoint1[0], self.clipPoint2[0])
                xmax = max(self.clipPoint1[0], self.clipPoint2[0])
                ymin = min(self.clipPoint1[1], self.clipPoint2[1])
                ymax = max(self.clipPoint1[1], self.clipPoint2[1])
                self.helperLines_item.p_list.append([[xmin, ymin], [xmin, ymax]])
                self.helperLines_item.p_list.append([[xmin, ymin], [xmax, ymin]])
                self.helperLines_item.p_list.append([[xmin, ymax], [xmax, ymax]])
                self.helperLines_item.p_list.append([[xmax, ymin], [xmax, ymax]])

    def saveImage(self):
        filename = QFileDialog.getSaveFileName(self, "保存画布", "myGreatPainting",
                                              "Bitmap File Format (*.bmp);;"
                                              "Portable Network Graphics (*.png);;"
                                              "Joint Photographic Experts Group (*.jpg);;"
                                              "Joint Photographic Experts Group (*.jpeg)")
        if filename[0] == '':
            return
        self.clear_selection()
        self.scene().clearSelection()
        pixmap = self.grab(self.sceneRect().toRect())
        pixmap.save(filename[0])

    def reset_canvas(self):
        self.clear_selection()
        self.helperLines_item.p_list = []
        self.helperPoints_item.p_list = []
        self.scene().removeItem(self.helperPoints_item)
        self.scene().removeItem(self.helperLines_item)
        self.scene().clear()
        self.scene().addItem(self.helperPoints_item)
        self.scene().addItem(self.helperLines_item)
        self.item_dict = {}
        self.main_window.reset()
        self.temp_id = self.main_window.get_id(self.status, 0)

    def set_color(self):
        colorDialog = QColorDialog()
        self.color = colorDialog.getColor()
        return self.color

    def set_fill_color(self):
        colorDialog = QColorDialog()
        self.fill_color = colorDialog.getColor()
        return self.fill_color

    def fill(self):
        if self.selected_id == '' or (not (self.item_dict[self.selected_id].item_type == 'polygonDone' or self.item_dict[self.selected_id].item_type == 'ellipse')):
            return False
        else:
            self.item_dict[self.selected_id].fill_color = self.fill_color
            self.updateScene([self.sceneRect()])
            return True

    def set_alg(self, algorithm):
        self.temp_algorithm = algorithm

    def set_line_width(self, width):
        self.line_width = (width + 1) * 2

    def start_select(self):
        self.status = 'select'

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.setCursor(Qt.CrossCursor)

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.setCursor(Qt.CrossCursor)

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id
        self.setCursor(Qt.CrossCursor)

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.setCursor(Qt.CrossCursor)

    def start_clip(self, algorithm):
        self.status = 'clip'
        self.clearSettings()
        self.temp_algorithm = algorithm
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        if self.selected_id == '' or self.item_dict[self.selected_id].item_type != 'line':
            # self.status = ''
            return False
        else:
            self.temp_id = self.selected_id
            return True

    def start_translate(self):
        self.status = 'translate'
        self.clearSettings()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        if self.selected_id == '':
            # self.status = ''
            return False
        else:
            self.temp_id = self.selected_id
            self.temp_item = self.item_dict[self.temp_id]
            self.temp_plist = self.temp_item.p_list[:]
            self.translateOrigin = [-1, -1]
            return True

    def start_scale(self):
        self.status = 'scale'
        self.clearSettings()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        if self.selected_id == '':
            # self.status = ''
            return False
        else:
            self.temp_id = self.selected_id
            self.temp_item = self.item_dict[self.temp_id]
            self.scalePoint = [-1, -1]
            return True

    def start_rotate(self):
        self.status = 'rotate'
        self.clearSettings()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        if self.selected_id == '':
            # self.status = ''
            return False
        else:
            self.temp_id = self.selected_id
            self.temp_item = self.item_dict[self.temp_id]
            self.rotatePoint = [-1, -1]
            return True

    def finish_draw(self):
        self.selection_changed(self.temp_id)
        self.helperPoints_item.p_list = []
        self.helperLines_item.p_list = []
        self.temp_id = self.main_window.get_id(self.status, 1)

    def clear_selection(self):
        self.clearSettings()
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        if self.selected_id == selected:
            return
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        self.clearSettings()
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.temp_item = self.item_dict[selected]
        # self.status = ''
        self.updateScene([self.sceneRect()])

    def copy(self):
        if self.selected_id == '':
            return False
        self.main_window.statusBar().showMessage('图元复制： %s' % self.selected_id)
        self.copied_item = self.temp_item
        return True

    def paste(self):
        if not self.copied_item:
            return False
        new_p_list = copy.deepcopy(self.copied_item.p_list)
        for point in new_p_list:
            point[0] += 20
            point[1] += 20
        newId = self.main_window.get_id(self.copied_item.item_type, 0)
        newItem = MyItem(newId, self.copied_item.item_type, new_p_list, self.copied_item.color, self.copied_item.width,
                         self.copied_item.algorithm)
        newItem.fill_color = self.copied_item.fill_color
        self.scene().addItem(newItem)
        self.item_dict[newId] = newItem
        self.list_widget.addItem(newId)
        self.selection_changed(newId)
        self.main_window.get_id(self.copied_item.item_type, 1)
        self.main_window.statusBar().showMessage('图元粘贴： %s' % newId)
        return True


    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.color, self.line_width, self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if event.button() == Qt.LeftButton:
                if not self.paintingPolygon:
                    self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.color, self.line_width, self.temp_algorithm)
                    self.paintingPolygon = True
                    self.scene().addItem(self.temp_item)
                else:
                    self.temp_item.p_list.append([x, y])
            else:
                self.temp_item.item_type = 'polygonDone'
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.paintingPolygon = False
                self.updateScene([self.sceneRect()])
                self.finish_draw()
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.color, self.line_width)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if event.button() == Qt.LeftButton:
                if not self.paintingCurve:
                    self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.color, self.line_width, self.temp_algorithm)
                    self.paintingCurve = True
                    self.scene().addItem(self.temp_item)
                else:
                    if len(self.temp_item.p_list) >= 1:
                        self.helperLines_item.p_list.append([self.temp_item.p_list[-1], [x, y]])
                    self.temp_item.p_list.append([x, y])
            else:
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.paintingCurve = False
                self.finish_draw()
        elif self.status == 'clip' and (self.temp_item.item_type == 'line' or self.temp_item.item_type == 'polygonDone'):
            self.clipPoint1 = [x, y]
        elif self.status == 'translate':
            self.translateOrigin = [x, y]
            self.temp_plist = self.temp_item.p_list[:]
        elif self.status == 'scale':
            if self.scalePoint == [-1, -1]:
                self.scalePoint = [x, y]
                self.temp_plist = self.temp_item.p_list[:]
                self.corePoint = self.temp_item.corePoint()
        elif self.status == 'rotate':
            if self.rotatePoint == [-1, -1]:
                self.rotatePoint = [x, y]
                self.temp_plist = self.temp_item.p_list[:]
                self.corePoint = self.temp_item.corePoint()
        elif self.status == 'select':
            item = self.scene().itemAt(x, y, QTransform())
            if item is not None:
                self.selection_changed(item.id)
        if self.temp_item:
            self.helperPoints_item.p_list = self.temp_item.p_list[:]
        self.checkHelper()
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def projectPointToLine(self, a, b, point):
        x0, y0, x1, y1, x, y = a[0], a[1], b[0], b[1], point[0], point[1]
        if x0 == x1:
            return [x0, y]
        elif y0 == y1:
            return [x, y0]
        else:
            k = (y1 - y0) / (x1 - x0)
            b0 = y0 - k * x0
            projectx = (k * y + x - k * b0) / (k * k + 1)
            return [int(projectx), int(projectx * k + b0)]


    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'translate':
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            self.temp_item.p_list = alg.translate(self.temp_plist, x - self.translateOrigin[0], y - self.translateOrigin[1])
        elif self.status == 'scale':
            if self.scalePoint != [-1, -1]:
                QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                a1 = self.corePoint[0] - self.scalePoint[0]
                b1 = self.corePoint[1] - self.scalePoint[1]
                a2 = self.corePoint[0] - self.projectPointToLine(self.corePoint, self.scalePoint, [x, y])[0]
                b2 = self.corePoint[1] - self.projectPointToLine(self.corePoint, self.scalePoint, [x, y])[1]
                if a1 == 0:
                    pivotLength = b1
                    nowLength = b2
                elif b1 == 0:
                    pivotLength = a1
                    nowLength = a2
                else:
                    if abs(a1) > abs(b1):
                        pivotLength = a1
                        nowLength = a2
                    else:
                        pivotLength = b1
                        nowLength = b2
                s = nowLength / pivotLength
                self.temp_item.p_list = alg.scale(self.temp_plist, self.scalePoint[0], self.scalePoint[1], 1 - s)
                self.helperLines_item.p_list = []
                for point in self.temp_item.p_list:
                    self.helperLines_item.p_list.append([point, self.scalePoint])
        elif self.status == 'rotate':
            if self.rotatePoint != [-1, -1]:
                QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                x1, y1 = self.corePoint[0], self.corePoint[1]
                x2, y2 = self.rotatePoint[0] - x1, self.rotatePoint[1] - y1
                x3, y3 = x - x1, y - y1
                flip = False
                if x2 == 0:
                    if x3 < 0:
                        flip = True
                elif x2 < 0:
                    k = -y2 / x2
                    if -y3 < k * x3:
                        flip = True
                elif x2 > 0:
                    k = -y2 / x2
                    if -y3 > k * x3:
                        flip = True
                a = math.sqrt(pow(x3 - x2, 2) + pow(y3 - y2, 2))
                b = math.sqrt(x2 * x2 + y2 * y2)
                c = math.sqrt(x3 * x3 + y3 * y3)
                cosA = (b*b+c*c-a*a)/(2*b*c)
                r = int(math.acos(cosA) * 180 / math.pi)
                if flip:
                    r = 360 - r
                self.temp_item.p_list = alg.rotate(self.temp_plist, self.corePoint[0], self.corePoint[1], r)
                # if self.temp_item.item_type == 'polygon' or self.temp_item.item_type == 'curve':
                #
                self.helperLines_item.p_list = []
                for point in self.temp_item.p_list:
                    self.helperLines_item.p_list.append([point, self.rotatePoint])
        elif self.status == 'clip':
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            self.clipPoint2 = [x, y]
        if self.temp_item:
            self.helperPoints_item.p_list = self.temp_item.p_list[:]
        self.checkHelper()
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'clip' and (self.temp_item.item_type == 'line' or self.temp_item.item_type == 'polygon' or self.temp_item.item_type == 'polygonDone'):
            pos = self.mapToScene(event.localPos().toPoint())
            x = int(pos.x())
            y = int(pos.y())
            self.clipPoint2 = [x, y]
            if self.temp_item.item_type == 'line':
                clipped_list = alg.clip(self.temp_item.p_list,
                                    min(self.clipPoint1[0], self.clipPoint2[0]),
                                    min(self.clipPoint1[1], self.clipPoint2[1]),
                                    max(self.clipPoint1[0], self.clipPoint2[0]),
                                    max(self.clipPoint1[1], self.clipPoint2[1]),
                                    self.temp_algorithm)
            else:
                clipped_list = alg.clipPolygon(self.temp_item.p_list,
                                    min(self.clipPoint1[0], self.clipPoint2[0]),
                                    min(self.clipPoint1[1], self.clipPoint2[1]),
                                    max(self.clipPoint1[0], self.clipPoint2[0]),
                                    max(self.clipPoint1[1], self.clipPoint2[1]))
            if clipped_list == '':
                self.temp_item = ''
            else:
                self.temp_item.p_list = clipped_list
                self.temp_item.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            # self.status = ''
            self.temp_id = ''
            self.helperLines_item.p_list = []
            self.helperPoints_item.p_list = []
            self.updateScene([self.sceneRect()])

        elif self.status == 'translate' or self.status == 'rotate' or self.status == 'scale':
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            # self.status = ''
            self.temp_id = ''
            self.temp_plist = self.temp_item.p_list[:]
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, color: QColor = QColor(0, 0, 0), width: int = 1, algorithm: str = '', parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param color: 画笔颜色
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.color = color
        self.fill_color = Qt.transparent
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.width = width
        self.selected = False

        pointPen = QPen()
        pointPen.setColor(QColor(0, 0, 0))
        pointPen.setWidth(1)
        pointPen.setStyle(Qt.SolidLine)
        pointPen.setCapStyle(Qt.SquareCap)
        self.pointPen = pointPen

        self.linePen = QPen()
        self.linePen.setColor(QColor(0, 128, 255))
        self.linePen.setWidth(1)
        self.linePen.setStyle(Qt.DashLine)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'helperPoints':
            for point in self.p_list:
                x, y = point[0], point[1]
                painter.drawPoint(x, y)
                painter.setPen(self.pointPen)
                painter.drawLine(x - 2, y - 2, x - 2, y + 2)
                painter.drawLine(x + 2, y - 2, x + 2, y + 2)
                painter.drawLine(x - 2, y - 2, x + 2, y - 2)
                painter.drawLine(x - 2, y + 2, x + 2, y + 2)
            return
        if self.item_type == 'helperLines':
            painter.setPen(self.linePen)
            for line in self.p_list:
                painter.drawLine(line[0][0], line[0][1], line[1][0], line[1][1])
            return
        elif self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
        elif self.item_type == 'polygon':
            item_pixels = []
            for i in range(len(self.p_list) - 1):
                line = alg.draw_line([self.p_list[i], self.p_list[i + 1]], self.algorithm)
                item_pixels += line

        elif self.item_type == 'polygonDone':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            box = self.boundingRect()
            if self.fill_color != Qt.transparent:
                fill_pixels = alg.fillPolygon(self.p_list, int(box.x()), int(box.y()), int(box.x() + box.width()), int(box.y() + box.height()))
                pen2 = QPen()
                pen2.setBrush(QColor(self.fill_color))
                painter.setPen(pen2)
                for p in fill_pixels:
                    painter.drawPoint(*p)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            box = self.boundingRect()
            if self.fill_color != Qt.transparent:
                fill_pixels = alg.fillEllipse(item_pixels, int(box.y()), int(box.y() + box.height()))
                pen2 = QPen()
                pen2.setBrush(QColor(self.fill_color))
                painter.setPen(pen2)
                for p in fill_pixels:
                    painter.drawPoint(*p)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
        pen = QPen()
        pen.setWidth(self.width)
        pen.setBrush(self.color)
        painter.setPen(pen)

        for p in item_pixels:
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawRect(self.boundingRect())


    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'curve' or self.item_type == 'polygon' or self.item_type == 'polygonDone':
            xmin = ymin = 10000
            xmax = ymax = 0
            for point in self.p_list:
                xmin = min(point[0], xmin)
                xmax = max(point[0], xmax)
                ymin = min(point[1], ymin)
                ymax = max(point[1], ymax)
            return QRectF(xmin, ymin, xmax - xmin, ymax - ymin)
        elif self.item_type == 'helperPoints':
            xmin = ymin = 10000
            xmax = ymax = 0
            for point in self.p_list:
                xmin = min(point[0], xmin)
                xmax = max(point[0], xmax)
                ymin = min(point[1], ymin)
                ymax = max(point[1], ymax)
            return QRectF(xmin - 2, ymin - 2, xmax - xmin + 4, ymax - ymin + 4)
        elif self.item_type == 'helperLines':
            xmin = ymin = 10000
            xmax = ymax = 0
            for line in self.p_list:
                for point in line:
                    xmin = min(point[0], xmin)
                    xmax = max(point[0], xmax)
                    ymin = min(point[1], ymin)
                    ymax = max(point[1], ymax)
            return QRectF(xmin - 2, ymin - 2, xmax - xmin + 4, ymax - ymin + 4)

    def corePoint(self):
        bdRect = self.boundingRect()
        return [int(bdRect.x() + (bdRect.right() - bdRect.left()) / 2), int(bdRect.y() + (bdRect.bottom() - bdRect.top()) / 2)]


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0
        self.line_cnt = self.polygon_cnt = self.curve_cnt = self.ellipse_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 800, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(802, 602)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 工具栏
        toolBar = QToolBar()
        toolBar.setCursor(Qt.ArrowCursor)
        self.addToolBar(toolBar)

        newCanvas = QAction(QIcon("./icon/new.png"), "新建画布", toolBar)
        newCanvas.setStatusTip("新建画布")
        newCanvas.triggered.connect(self.new_canvas_action)
        toolBar.addAction(newCanvas)

        resetCanvas = QAction(QIcon("./icon/delete.png"), "清空画布", toolBar)
        resetCanvas.setStatusTip("清空画布")
        resetCanvas.triggered.connect(self.reset_canvas_action)
        toolBar.addAction(resetCanvas)

        saveCanvas = QAction(QIcon("./icon/saveas.png"), "保存画布", toolBar)
        saveCanvas.setStatusTip("保存画布")
        saveCanvas.triggered.connect(self.save_canvas_action)
        toolBar.addAction(saveCanvas)

        copyBtn = QAction(QIcon("./icon/copy.png"), "复制图元", toolBar)
        copyBtn.setStatusTip("复制图元")
        copyBtn.triggered.connect(self.copy_action)
        toolBar.addAction(copyBtn)

        pasteBtn = QAction(QIcon("./icon/paste.png"), "粘贴图元", toolBar)
        pasteBtn.setStatusTip("粘贴图元")
        pasteBtn.triggered.connect(self.paste_action)
        toolBar.addAction(pasteBtn)

        toolBar.addSeparator()

        # setColor = QAction(QIcon("./icon/palette.png"), "选择颜色", toolBar)
        # setColor.setStatusTip("选择颜色")
        # setColor.triggered.connect(self.set_pen_action)
        # toolBar.addAction(setColor)

        colorViewer = QToolButton(self)
        colorViewer.setFixedHeight(30)
        colorViewer.setFixedWidth(30)
        colorViewer.setStyleSheet("margin: 5px; background-color: black; border-radius: 5px;")
        colorViewer.setCheckable(True)
        colorViewer.toggled.connect(self.set_pen_action)
        toolBar.addWidget(colorViewer)
        self.colorViewer = colorViewer

        pad = QLabel()
        pad.setFixedWidth(10)
        toolBar.addWidget(pad)

        self.lineWidthSelector = QComboBox()
        self.lineWidthSelector.addItem(QIcon("./icon/line1.png"), "")
        self.lineWidthSelector.addItem(QIcon("./icon/line2.png"), "")
        self.lineWidthSelector.addItem(QIcon("./icon/line3.png"), "")
        self.lineWidthSelector.highlighted[int].connect(self.canvas_widget.set_line_width)
        toolBar.addWidget(self.lineWidthSelector)

        pad2 = QLabel()
        pad2.setFixedWidth(5)
        toolBar.addWidget(pad2)
        toolBar.addSeparator()

        fillColorViewer = QToolButton(self)
        fillColorViewer.setFixedHeight(30)
        fillColorViewer.setFixedWidth(30)
        fillColorViewer.setStyleSheet("margin: 5px; background-color: green; border-radius: 5px;")
        fillColorViewer.setCheckable(True)
        fillColorViewer.toggled.connect(self.set_fill_color_action)
        toolBar.addWidget(fillColorViewer)
        self.fillColorViewer = fillColorViewer

        fillBtn = QAction(QIcon("./icon/fill.png"), "图元填充", toolBar)
        fillBtn.setStatusTip("图元填充")
        fillBtn.triggered.connect(self.fill_action)
        toolBar.addAction(fillBtn)

        toolBar.addSeparator()

        drawLineBtn = QToolButton(self)
        drawLineBtn.setIcon(QIcon("./icon/line.png"))
        drawLineBtn.setStatusTip("绘制线段")
        drawLineBtn.pressed.connect(self.line_action)
        drawPolygonBtn = QToolButton(self)
        drawPolygonBtn.setIcon(QIcon("./icon/polygon.png"))
        drawPolygonBtn.setStatusTip("绘制多边形")
        drawPolygonBtn.pressed.connect(self.polygon_action)
        drawEllipseBtn = QToolButton(self)
        drawEllipseBtn.setIcon(QIcon("./icon/ellipse.png"))
        drawEllipseBtn.setStatusTip("绘制椭圆")
        drawEllipseBtn.pressed.connect(self.ellipse_action)
        drawCurveBtn = QToolButton(self)
        drawCurveBtn.setIcon(QIcon("./icon/curve.png"))
        drawCurveBtn.setStatusTip("绘制曲线")
        drawCurveBtn.pressed.connect(self.curve_action)
        selectBtn = QToolButton(self)
        selectBtn.setIcon(QIcon("./icon/select.png"))
        selectBtn.setStatusTip("图元选择")
        selectBtn.pressed.connect(self.select_action)
        translateBtn = QToolButton(self)
        translateBtn.setIcon(QIcon("./icon/translate.png"))
        translateBtn.setStatusTip("图元平移")
        translateBtn.pressed.connect(self.translate_action)
        rotateBtn = QToolButton(self)
        rotateBtn.setIcon(QIcon("./icon/rotate.png"))
        rotateBtn.setStatusTip("图元旋转")
        rotateBtn.pressed.connect(self.rotate_action)
        scaleBtn = QToolButton(self)
        scaleBtn.setIcon(QIcon("./icon/scale.png"))
        scaleBtn.setStatusTip("图元缩放")
        scaleBtn.pressed.connect(self.scale_action)
        clipBtn = QToolButton(self)
        clipBtn.setIcon(QIcon("./icon/clip.png"))
        clipBtn.setStatusTip("线段裁剪")
        clipBtn.pressed.connect(self.clip_action)


        self.group = QButtonGroup(self, exclusive=True)

        for button in (
            drawLineBtn,
            drawPolygonBtn,
            drawEllipseBtn,
            drawCurveBtn,
            selectBtn,
            translateBtn,
            rotateBtn,
            scaleBtn,
            clipBtn,
        ):
            button.setCheckable(True)
            toolBar.addWidget(button)
            self.group.addButton(button)

        toolBar.addSeparator()

        pad3 = QLabel()
        pad3.setFixedWidth(5)
        toolBar.addWidget(pad3)
        self.comboBox = QComboBox()
        self.comboBox.setFixedWidth(155)
        self.comboBox.highlighted[str].connect(self.canvas_widget.set_alg)

        toolBar.addWidget(self.comboBox)


        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self, type, add):
        if type == 'line':
            self.line_cnt += add
            print ('line ' + str(self.line_cnt))
            return 'line ' + str(self.line_cnt)
        elif type == 'polygon' or type == 'polygonDone':
            self.polygon_cnt += add
            return 'polygon ' + str(self.polygon_cnt)
        elif type == 'curve':
            self.curve_cnt += add
            return 'curve ' + str(self.curve_cnt)
        elif type == 'ellipse':
            self.ellipse_cnt += add
            return 'ellipse ' + str(self.ellipse_cnt)
        return "null"

    def reset(self):
        self.line_cnt = self.ellipse_cnt = self.curve_cnt = self.polygon_cnt = 0
        self.list_widget.clear()
        # checkedbutton = self.group.checkedButton()
        # if checkedbutton:
        #     self.group.setExclusive(False)
        #     checkedbutton.setChecked(False)
        #     self.group.setExclusive(True)

    def line_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.comboBox.clear()
        self.comboBox.addItem("DDA")
        self.comboBox.addItem("Bresenham")
        self.comboBox.addItem("Naive")
        self.canvas_widget.start_draw_line('DDA', self.get_id('line', 0))
        self.statusBar().showMessage('绘制线段')


    def polygon_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.comboBox.clear()
        self.comboBox.addItem("DDA")
        self.comboBox.addItem("Bresenham")
        self.canvas_widget.start_draw_polygon('DDA', self.get_id('polygon', 0))
        self.statusBar().showMessage('绘制多边形')


    def curve_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.comboBox.clear()
        self.comboBox.addItem("Bezier")
        self.comboBox.addItem("B-spline")
        self.canvas_widget.start_draw_curve('Bezier', self.get_id('curve', 0))
        self.statusBar().showMessage('绘制曲线')


    def clip_action(self):
        self.comboBox.clear()
        self.comboBox.addItem("Cohen-Sutherland")
        self.comboBox.addItem("Liang-Barsky")
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('线段裁剪')

    def select_action(self):
        self.canvas_widget.start_select()


    def ellipse_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.comboBox.clear()
        self.canvas_widget.start_draw_ellipse(self.get_id('ellipse', 0))
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()


    def translate_action(self):
        self.comboBox.clear()
        if not self.canvas_widget.start_translate():
            self.statusBar().showMessage('请选中图元')
        else:
            self.statusBar().showMessage('图元平移')

    def scale_action(self):
        self.comboBox.clear()
        if not self.canvas_widget.start_scale():
            self.statusBar().showMessage('请选中图元')
        else:
            self.statusBar().showMessage('图元缩放')

    def rotate_action(self):
        self.comboBox.clear()
        if not self.canvas_widget.start_rotate():
            self.statusBar().showMessage('请选中图元')
        else:
            self.statusBar().showMessage('图元旋转')

    def new_canvas_action(self):
        self.canvas_widget.reset_canvas()

        dialog = QDialog()
        layout = QFormLayout(dialog)
        heightEdit = QLineEdit(dialog)
        widthEdit = QLineEdit(dialog)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        layout.addRow("Height", heightEdit)
        layout.addRow("Width", widthEdit)
        layout.addWidget(buttonBox)

        if dialog.exec():
            height = int(heightEdit.text())
            width = int(widthEdit.text())
            self.scene.setSceneRect(0, 0, width, height)
            self.canvas_widget.setFixedSize(width+2, height+2)
        self.statusBar().showMessage('新建画布')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def reset_canvas_action(self):
        self.canvas_widget.reset_canvas()
        self.statusBar().showMessage('清空画布')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def set_pen_action(self):
        color = self.canvas_widget.set_color()
        if color.isValid():
            css = "margin: 5px; background-color: rgb({0},{1},{2}); border-radius: 5px;".format(color.red(), color.green(), color.blue())
            self.colorViewer.setStyleSheet(css)
        self.statusBar().showMessage('设置颜色')

    def set_fill_color_action(self):
        fill_color = self.canvas_widget.set_fill_color()
        if fill_color.isValid():
            css = "margin: 5px; background-color: rgb({0},{1},{2}); border-radius: 5px;".format(fill_color.red(),
                                                                                                fill_color.green(),
                                                                                                fill_color.blue())
            self.fillColorViewer.setStyleSheet(css)
        self.statusBar().showMessage('设置填充颜色')

    def fill_action(self):
        if self.canvas_widget.fill():
            self.statusBar().showMessage('填充图元')
        else:
            self.statusBar().showMessage('请选中多边形或椭圆图元进行填充')

    def copy_action(self):
        if not self.canvas_widget.copy():
            self.statusBar().showMessage('请选中图元进行复制')

    def paste_action(self):
        if not self.canvas_widget.paste():
            self.statusBar().showMessage('请先复制图元')

    def save_canvas_action(self):
        self.canvas_widget.saveImage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())

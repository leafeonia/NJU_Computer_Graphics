#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QGraphicsSceneMouseEvent)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPen
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math

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
        self.paintingPolygon = False
        self.paintingCurve = False
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.clipPoint1 = [-1, -1]
        self.clipPoint2 = [-1, -1]
        self.translateOrigin = [-1, -1]

        self.temp_plist = []
        self.corePoint = [-1, -1]

        # scale
        self.scalePoint = [-1, -1]

        # rotate
        self.rotatePoint = [-1, -1]

        # helperPoints
        self.helperPoints_item = MyItem("helperPoints", "helperPoints", [])
        self.scene().addItem(self.helperPoints_item)

    def clearSettings(self):
        self.helperPoints_item.p_list = []
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

    def saveImage(self):
        filename = QFileDialog.getSaveFileName(self, "保存画布", "myGreatPainting",
                                              "Bitmap File Format (*.bmp);;"
                                              "Portable Network Graphics (*.png);;"
                                              "Joint Photographic Experts Group (*.jpg);;"
                                              "Joint Photographic Experts Group (*.jpeg)")
        if filename[0] == '':
            return
        self.scene().clearSelection()
        pixmap = self.grab(self.sceneRect().toRect())
        pixmap.save(filename[0])

    def reset_canvas(self):
        self.clear_selection()
        self.scene().removeItem(self.helperPoints_item)
        self.scene().clear()
        self.scene().addItem(self.helperPoints_item)
        self.item_dict = {}


    def set_color(self):
        colorDialog = QColorDialog()
        self.color = colorDialog.getColor()

    def set_alg(self, algorithm):
        self.temp_algorithm = algorithm

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_clip(self, algorithm):
        self.status = 'clip'
        self.clearSettings()
        self.temp_algorithm = algorithm
        if self.selected_id == '' or self.item_dict[self.selected_id].item_type != 'line':
            # self.status = ''
            return False
        else:
            self.temp_id = self.selected_id
            return True

    def start_translate(self):
        self.status = 'translate'
        self.clearSettings()
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
        if self.selected_id == '':
            # self.status = ''
            return False
        else:
            self.temp_id = self.selected_id
            self.temp_item = self.item_dict[self.temp_id]
            self.rotatePoint = [-1, -1]
            return True

    def finish_draw(self):
        self.helperPoints_item.p_list = []
        self.temp_id = self.main_window.get_id()

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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.color, self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if not self.paintingPolygon:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.color, self.temp_algorithm)
                self.paintingPolygon = True
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x, y])
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if not self.paintingCurve:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.color, self.temp_algorithm)
                self.paintingCurve = True
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x, y])
        elif self.status == 'clip' and self.temp_item.item_type == 'line':
            self.clipPoint1 = [x, y]
        elif self.status == 'translate':
            self.translateOrigin = [x, y]
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
        self.helperPoints_item.p_list = self.temp_item.p_list[:]
        self.checkHelper()
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'curve':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.paintingCurve = False
            self.finish_draw()
        elif self.status == 'polygon':
            self.temp_item.item_type = 'polygonDone'
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.paintingPolygon = False
            self.updateScene([self.sceneRect()])
            self.finish_draw()

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
            self.temp_item.p_list = alg.translate(self.temp_plist, x - self.translateOrigin[0], y - self.translateOrigin[1])
        elif self.status == 'scale':
            if self.scalePoint != [-1, -1]:
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
        elif self.status == 'rotate':
            if self.rotatePoint != [-1, -1]:
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
        elif self.status == 'clip' and self.temp_item.item_type == 'line':
            pos = self.mapToScene(event.localPos().toPoint())
            x = int(pos.x())
            y = int(pos.y())
            self.clipPoint2 = [x, y]
            clipped_list = alg.clip(self.temp_item.p_list,
                                    min(self.clipPoint1[0], self.clipPoint2[0]),
                                    min(self.clipPoint1[1], self.clipPoint2[1]),
                                    max(self.clipPoint1[0], self.clipPoint2[0]),
                                    max(self.clipPoint1[1], self.clipPoint2[1]),
                                    self.temp_algorithm)
            if clipped_list == '':
                self.temp_item = ''
            else:
                self.temp_item.p_list = clipped_list
                self.temp_item.update()
            # self.status = ''
            self.temp_id = ''
            self.updateScene([self.sceneRect()])

        elif self.status == 'translate' or self.status == 'rotate' or self.status == 'scale':
            # self.status = ''
            self.temp_id = ''
            self.temp_plist = self.temp_item.p_list[:]
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, color: QColor = QColor(0, 0, 0), algorithm: str = '', parent: QGraphicsItem = None):
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
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False

        pointPen = QPen()
        pointPen.setColor(QColor(0, 0, 0))
        pointPen.setWidth(1)
        pointPen.setStyle(Qt.SolidLine)
        pointPen.setCapStyle(Qt.SquareCap)
        self.pointPen = pointPen

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

        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
        elif self.item_type == 'polygon':
            item_pixels = []
            for i in range(len(self.p_list) - 1):
                line = alg.draw_line([self.p_list[i], self.p_list[i + 1]], self.algorithm)
                item_pixels += line
        elif self.item_type == 'polygonDone':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
        for p in item_pixels:
            painter.setPen(self.color)
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(Qt.red)
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

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(602, 602)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 工具栏
        toolBar = QToolBar()
        self.addToolBar(toolBar)

        newCanvas = QAction(QIcon("./icon/new.png"), "重置画布", toolBar)
        newCanvas.setStatusTip("重置画布")
        newCanvas.triggered.connect(self.reset_canvas_action)
        toolBar.addAction(newCanvas)

        # newCanvas = QToolButton(self)
        # newCanvas.setIcon(QIcon("./icon/new.png"))
        # newCanvas.setCheckable(True)
        # newCanvas.toggled.connect(self.reset_canvas_action)
        # toolBar.addWidget(newCanvas)


        saveCanvas = QAction(QIcon("./icon/saveas.png"), "保存画布", toolBar)
        saveCanvas.setStatusTip("保存画布")
        saveCanvas.triggered.connect(self.save_canvas_action)
        toolBar.addAction(saveCanvas)

        setColor = QAction(QIcon("./icon/palette.png"), "选择颜色", toolBar)
        setColor.setStatusTip("选择颜色")
        setColor.triggered.connect(self.set_pen_action)
        toolBar.addAction(setColor)

        colorViewer = QToolButton(self)
        colorViewer.setFixedHeight(30)
        colorViewer.setFixedWidth(30)
        colorViewer.setStyleSheet("margin: 5px; background-color: red; border-radius: 5px;")
        toolBar.addWidget(colorViewer)

        toolBar.addSeparator()

        drawLineBtn = QToolButton(self)
        drawLineBtn.setIcon(QIcon("./icon/line.png"))
        drawLineBtn.setStatusTip("绘制线段")
        drawLineBtn.toggled.connect(self.line_action)
        drawPolygonBtn = QToolButton(self)
        drawPolygonBtn.setIcon(QIcon("./icon/polygon.png"))
        drawPolygonBtn.setStatusTip("绘制多边形")
        drawPolygonBtn.toggled.connect(self.polygon_action)
        drawEllipseBtn = QToolButton(self)
        drawEllipseBtn.setIcon(QIcon("./icon/ellipse.png"))
        drawEllipseBtn.setStatusTip("绘制椭圆")
        drawEllipseBtn.toggled.connect(self.ellipse_action)
        drawCurveBtn = QToolButton(self)
        drawCurveBtn.setIcon(QIcon("./icon/curve.png"))
        drawCurveBtn.setStatusTip("绘制曲线")
        drawCurveBtn.toggled.connect(self.curve_action)
        translateBtn = QToolButton(self)
        translateBtn.setIcon(QIcon("./icon/select.png"))
        translateBtn.setStatusTip("图元平移")
        translateBtn.toggled.connect(self.translate_action)
        rotateBtn = QToolButton(self)
        rotateBtn.setIcon(QIcon("./icon/rotate.png"))
        rotateBtn.setStatusTip("图元旋转")
        rotateBtn.toggled.connect(self.rotate_action)
        scaleBtn = QToolButton(self)
        scaleBtn.setIcon(QIcon("./icon/scale.png"))
        scaleBtn.setStatusTip("图元缩放")
        scaleBtn.toggled.connect(self.scale_action)
        clipBtn = QToolButton(self)
        clipBtn.setIcon(QIcon("./icon/clip.png"))
        clipBtn.setStatusTip("线段裁剪")
        clipBtn.toggled.connect(self.clip_action)


        group = QButtonGroup(self, exclusive=True)

        for button in (
            drawLineBtn,
            drawPolygonBtn,
            drawEllipseBtn,
            drawCurveBtn,
            translateBtn,
            rotateBtn,
            scaleBtn,
            clipBtn,
        ):
            button.setCheckable(True)
            toolBar.addWidget(button)
            group.addButton(button)

        toolBar.addSeparator()

        self.comboBox = QComboBox()
        self.comboBox.setFixedWidth(150)
        self.comboBox.highlighted[str].connect(self.canvas_widget.set_alg)


        toolBar.addWidget(self.comboBox)


        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        translate_act.triggered.connect(self.translate_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        scale_act.triggered.connect(self.scale_action)
        rotate_act.triggered.connect(self.rotate_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        set_pen_act.triggered.connect(self.set_pen_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
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

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def line_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.comboBox.clear()
        self.comboBox.addItem("DDA")
        self.comboBox.addItem("Bresenham")
        self.comboBox.addItem("Naive")
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('绘制线段')


    def polygon_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.comboBox.clear()
        self.comboBox.addItem("DDA")
        self.comboBox.addItem("Bresenham")
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('绘制多边形')


    def curve_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.comboBox.clear()
        self.comboBox.addItem("Bezier")
        self.comboBox.addItem("B-spline")
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('绘制曲线')


    def clip_action(self):
        self.comboBox.clear()
        self.comboBox.addItem("Cohen-Sutherland")
        self.comboBox.addItem("Liang-Barsky")
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('线段裁剪')

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.comboBox.clear()
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('B样条算法绘制曲线')
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

    def reset_canvas_action(self):
        self.canvas_widget.reset_canvas()
        self.statusBar().showMessage('清空画布')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def set_pen_action(self):
        self.canvas_widget.set_color()
        self.statusBar().showMessage('设置颜色')

    def save_canvas_action(self):
        self.canvas_widget.saveImage()

    def clip_cohen_sutherland_action(self):
        if not self.canvas_widget.start_clip('Cohen-Sutherland'):
            self.statusBar().showMessage('请选中线段图元')
        else:
            self.statusBar().showMessage('Cohen-Sutherland算法裁剪')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def clip_liang_barsky_action(self):
        if not self.canvas_widget.start_clip('Liang-Barsky'):
            self.statusBar().showMessage('请选中线段图元')
        else:
            self.statusBar().showMessage('Liang-Barsky算法裁剪')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPolygonF, QPainter, QColor, QPixmap, QFont, QPainterPath
from PyQt5.QtWidgets import QWidget
import ms_toollib as ms
from PyQt5.QtCore import QPoint, Qt
# from PyQt5.QtSvg import QSvgWidget


class mineLabel(QtWidgets.QLabel):
    # 一整个局面的控件，而不是一个格子
    leftRelease = QtCore.pyqtSignal (int, int)  # 定义信号
    rightRelease = QtCore.pyqtSignal (int, int)
    leftPressed = QtCore.pyqtSignal (int, int)
    rightPressed = QtCore.pyqtSignal (int, int)
    leftAndRightPressed = QtCore.pyqtSignal (int, int)
    leftAndRightRelease = QtCore.pyqtSignal (int, int)
    mouseMove = QtCore.pyqtSignal (int, int)
    mousewheelEvent = QtCore.pyqtSignal (int)
    row = 0
    column = 0

    def __init__(self, parent):
        super (mineLabel, self).__init__ (parent)
        points = []
        mouse_ = QPolygonF(points)
        self.mouse = QPainterPath()
        self.mouse.addPolygon(mouse_)
        self.paint_cursor = False # 是否画光标。不仅控制画光标，还代表了是游戏还是播放录像。
        
    def set_rcp(self, row, column, pixSize): # 重设一下宽、高、大小
        self.pixSize = pixSize
        self.paintPossibility = False  # 是否打印概率
        if (self.row, self.column) != (row, column): # 如果不相等，重新实例化
            self.row = row
            self.column = column
            self.ms_board = ms.MinesweeperBoard([[0] * self.column for _ in range(self.row)])
            self.boardPossibility = [[0.0] * self.ms_board.column for _ in range(self.ms_board.row)]
        self.importCellPic(self.pixSize)
        self.resize(QtCore.QSize(self.pixSize * self.column + 8, self.pixSize * self.row + 8))
        self.current_x = self.row # 鼠标坐标，和高亮的展示有关
        self.current_y = self.column
        
        points = [ QPoint(0, 0),
                  QPoint(0, pixSize),
                QPoint(0.227 * pixSize, 0.773 * pixSize),
                QPoint(0.359 * pixSize, 1.125 * pixSize),
                QPoint(0.493 * pixSize, 1.066 * pixSize),
                QPoint(0.357 * pixSize, 0.72 * pixSize),
                QPoint(0.666 * pixSize, 0.72 * pixSize) ]
        mouse_ = QPolygonF(points)
        self.mouse = QPainterPath()
        self.mouse.addPolygon(mouse_)

    def mousePressEvent(self, e):  # 重载一下鼠标点击事件
        xx = int(e.localPos().x() // self.pixSize)
        yy = int(e.localPos().y() // self.pixSize)
        if yy < 0 or xx < 0 or yy >= self.row or xx >= self.column:
            self.current_x = self.row
            self.current_y = self.column
        else:
            self.current_x = yy
            self.current_y = xx
        # xx和yy是反的，列、行
        if e.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.RightButton:
            self.leftAndRightPressed.emit(self.current_x, self.current_y)
        else:
            if e.buttons () == QtCore.Qt.LeftButton:
                self.leftPressed.emit(self.current_x, self.current_y)
            elif e.buttons () == QtCore.Qt.RightButton:
                self.rightPressed.emit(self.current_x, self.current_y)

    def mouseReleaseEvent(self, e):
        #每个标签的鼠标事件发射给槽的都是自身的坐标
        #所以获取释放点相对本标签的偏移量，矫正发射的信号
        xx = int(e.localPos().x() // self.pixSize)
        yy = int(e.localPos().y() // self.pixSize)
        # print('抬起位置{}, {}'.format(xx, yy))
        # print(e.button ())
        if yy < 0 or xx < 0 or yy >= self.row or xx >= self.column:
            self.current_x = self.row
            self.current_y = self.column
        else:
            self.current_x = yy
            self.current_y = xx
        if e.button() == QtCore.Qt.LeftButton:
            self.leftRelease.emit(self.current_x, self.current_y)
        elif e.button () == QtCore.Qt.RightButton:
            self.rightRelease.emit(self.current_x, self.current_y)

    def mouseMoveEvent(self, e):
        xx = int(e.localPos().x() // self.pixSize)
        yy = int(e.localPos().y() // self.pixSize)
        # print('移动位置{}, {}'.format(xx, yy))
        if yy < 0 or xx < 0 or yy >= self.row or xx >= self.column:
            self.current_x = self.row
            self.current_y = self.column
        else:
            self.current_x = yy
            self.current_y = xx
        self.mouseMove.emit(yy, xx)
        
    def wheelEvent(self, event):
        # 滚轮事件
        angle=event.angleDelta()
        angleY=angle.y()
        self.mousewheelEvent.emit(angleY)

    def paintEvent(self, event):
        super().paintEvent(event)
        pix_size = self.pixSize
        painter = QPainter()
        game_board = self.ms_board.game_board
        mouse_state = self.ms_board.mouse_state
        if self.paint_cursor: # 播放录像
            game_board_state = 1
            (x, y) = self.ms_board.x_y
            current_x = y // 16
            current_y = x // 16
            # poss = self.ms_board.game_board_poss
        else: # 游戏
            game_board_state = self.ms_board.game_board_state
            current_x = self.current_x
            current_y = self.current_y
            # poss = self.boardPossibility
        painter.begin(self)
        # 画游戏局面
        for i in range(self.row):
            for j in range(self.column):
                if game_board[i][j] == 10:
                    painter.drawPixmap(j * pix_size + 4, i * pix_size + 4, QPixmap(self.pixmapNum[10]))
                    if self.paintPossibility: # 画概率
                        if self.paint_cursor:
                            painter.setOpacity(self.ms_board.game_board_poss[i][j])
                        else:
                            painter.setOpacity(self.boardPossibility[i][j])
                        painter.drawPixmap(j * pix_size + 4, i * pix_size + 4, QPixmap(self.pixmapNum[100]))
                        painter.setOpacity(1.0)
                else:
                    painter.drawPixmap(j * pix_size + 4, i * pix_size + 4, QPixmap(self.pixmapNum[game_board[i][j]]))
        
        
        # 画高亮
        if (game_board_state == 2 or game_board_state == 1) and\
            not self.paintPossibility and current_x < self.row and current_y < self.column:
            if mouse_state == 5 or mouse_state == 6:
                for r in range(max(current_x - 1, 0), min(current_x + 2, self.row)):
                    for c in range(max(current_y - 1, 0), min(current_y + 2, self.column)):
                        if game_board[r][c] == 10:
                            painter.drawPixmap(c * pix_size + 4, r * pix_size + 4, QPixmap(self.pixmapNum[0]))
            elif mouse_state == 4 and game_board[current_x][current_y] == 10:
                painter.drawPixmap(current_y * pix_size + 4, current_x * pix_size + 4, QPixmap(self.pixmapNum[0]))
        # 画光标
        if self.paint_cursor:
            painter.translate(x * pix_size / 16, y * pix_size / 16)
            painter.drawPath(self.mouse)
            painter.fillPath(self.mouse,Qt.white)
        painter.end()

    def importCellPic(self, pixSize):
        # 从磁盘导入资源，并缩放到希望的尺寸、比例
        celldown = QPixmap("media/celldown.svg")
        cell1 = QPixmap("media/cell1.svg")
        cell2 = QPixmap("media/cell2.svg")
        cell3 = QPixmap("media/cell3.svg")
        cell4 = QPixmap("media/cell4.svg")
        cell5 = QPixmap("media/cell5.svg")
        cell6 = QPixmap("media/cell6.svg")
        cell7 = QPixmap("media/cell7.svg")
        cell8 = QPixmap("media/cell8.svg")
        cellup = QPixmap("media/cellup.svg")
        cellmine = QPixmap("media/cellmine.svg") # 白雷
        cellflag = QPixmap("media/cellflag.svg") # 标雷
        blast = QPixmap("media/blast.svg") # 红雷
        falsemine = QPixmap("media/falsemine.svg") # 叉雷
        mine = QPixmap("media/mine.svg") # 透明雷
        self.pixmapNumBack = {0: celldown, 1: cell1, 2: cell2, 3: cell3, 4: cell4,
                     5: cell5, 6: cell6, 7: cell7, 8: cell8,
                     10: cellup, 11: cellflag, 14: falsemine,
                     15: blast, 16: cellmine, 100: mine}
        celldown_ = celldown.copy().scaled(pixSize, pixSize)
        cell1_ = cell1.copy().scaled(pixSize, pixSize)
        cell2_ = cell2.copy().scaled(pixSize, pixSize)
        cell3_ = cell3.copy().scaled(pixSize, pixSize)
        cell4_ = cell4.copy().scaled(pixSize, pixSize)
        cell5_ = cell5.copy().scaled(pixSize, pixSize)
        cell6_ = cell6.copy().scaled(pixSize, pixSize)
        cell7_ = cell7.copy().scaled(pixSize, pixSize)
        cell8_ = cell8.copy().scaled(pixSize, pixSize)
        cellup_ = cellup.copy().scaled(pixSize, pixSize)
        cellmine_ = cellmine.copy().scaled(pixSize, pixSize)
        cellflag_ = cellflag.copy().scaled(pixSize, pixSize)
        blast_ = blast.copy().scaled(pixSize, pixSize)
        falsemine_ = falsemine.copy().scaled(pixSize, pixSize)
        mine_ = mine.copy().scaled(pixSize, pixSize)
        self.pixmapNum = {0: celldown_, 1: cell1_, 2: cell2_, 3: cell3_, 4: cell4_,
                     5: cell5_, 6: cell6_, 7: cell7_, 8: cell8_,
                     10: cellup_, 11: cellflag_, 14: falsemine_,
                     15: blast_, 16: cellmine_, 100: mine_}
    
    def reloadCellPic(self, pixSize):
        # 从内存导入资源，并缩放到希望的尺寸、比例。
        self.pixmapNum = {key:value.copy().scaled(pixSize, pixSize) for key,value in self.pixmapNumBack.items()}
        



#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import sys
import os
import random
import webbrowser
import xml.etree.cElementTree as ET
import xml

font12 = QtGui.QFont("Verdana", 12, 60)

#Класс вывода сообщения с номером
class Info(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 3

    def __init__(self):
        super(Info, self).__init__()
        self.drawed = False
        self.number = None
        self.setZValue(2)

    def boundingRect(self):
        return QtCore.QRectF(-25, -45, 55, 30)

    def paint(self, painter, option, widget):
        if self.drawed == True:
            #Синтаксический сахар
            self.rect = self.boundingRect()
            #Градиент
            gradient = QtGui.QLinearGradient(self.rect.x(),
                                             self.rect.y(),
                                             self.rect.x(),
                                             self.rect.y() + self.rect.height())
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.white))
            gradient.setColorAt(1, QtGui.QColor(176, 176, 176))
            #Прорисовка самого объекта
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor(31, 31, 28))
            painter.drawRect(-21, -41, 50, 25)
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRect(-25, -45, 50, 25)
            #Выставление свойств для цифры
            textOption = QtGui.QTextOption()
            textOption.setAlignment(QtCore.Qt.AlignHCenter)
            staticText = QtGui.QStaticText(str(self.number))
            staticText.setTextOption(textOption)
            staticText.setTextWidth(50)
            painter.setFont(font12)
            #Прорисовка цифры на объекте
            painter.drawStaticText(-25, -42, staticText)         

    #Метод на обновление объекта 
    def adjust(self):
        self.prepareGeometryChange()
        self.update()

class Edge(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        super(Edge, self).__init__()

        self.highlighted = False

        #Точки построения линии
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()

        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        #Выставление начальных координат начала и конца
        self.source = sourceNode
        self.dest = destNode
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.adjust()

    #Метод регулировки 
    def adjust(self):
        if not self.source or not self.dest:
            return

        #Вычисление координат линии
        line = QtCore.QLineF(self.mapFromItem(self.source, 0, 0),
                             self.mapFromItem(self.dest, 0, 0))
        length = line.length()

        self.prepareGeometryChange()

        if length > 20.0:
            edgeOffset = QtCore.QPointF((line.dx() * 10) / length,
                    (line.dy() * 10) / length)

            self.sourcePoint = line.p1() + edgeOffset
            self.destPoint = line.p2() - edgeOffset
        else:
            self.sourcePoint = line.p1()
            self.destPoint = line.p1()        

    #Метод ограничения прямоугольника в который будет помещено ребро
    def boundingRect(self):
        if not self.source or not self.dest:
            return QtCore.QRectF()

        penWidth = 1.0
        extra = (penWidth) / 2.0

        return QtCore.QRectF(self.sourcePoint,
                QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                             self.destPoint.y() - self.sourcePoint.y())).\
                             normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if not self.source or not self.dest:
            return

        #Прорисовка самой линии
        line = QtCore.QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        if self.highlighted == False:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 171, 73), 1,
                                      QtCore.Qt.SolidLine,
                                      QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        elif self.highlighted == True:
            painter.setPen(QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine,
                                      QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1
    
    def __init__(self, graphWidget):
        super(Node, self).__init__()

        self.number = None
        self.graph = graphWidget
        self.edgeList = []
        self.newPos = QtCore.QPointF()
        self.highlighted = False
        self.color = None

        #Выставление свойств для вершин
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(2)
        self.setAcceptHoverEvents(True)

    #Метод добавления ребра в список ребер
    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    #Метод ограничения прямоугольника в который будет помещена точка
    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust,
                             23 + adjust, 23 + adjust)
                             
    def paint(self, painter, option, widget):
        #Прорисовка тени вершины
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(31, 31, 28))
        painter.drawEllipse(-7, -7, 20, 20)

        #Прорисовка градиента 
        gradient = QtGui.QRadialGradient(-3, -3, 10)
        
        #Если это связующая вершина
        if self.color == "gray":
            gradient.setColorAt(1, QtGui.QColor(59, 59, 59))
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.gray))
        elif self.color == "black":
            gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.black))
            gradient.setColorAt(0, QtGui.QColor(75, 75, 75))
        elif self.highlighted == True:
            gradient.setColorAt(1, QtGui.QColor(176, 176, 176))
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.white))
        #Если указатель мыши над вершиной
        elif option.state & QtGui.QStyle.State_MouseOver:
            gradient.setColorAt(1, QtGui.QColor(176, 176, 176))
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.white))
        #Обычное состояние
        else:
            gradient.setColorAt(0, QtGui.QColor(255, 171, 73))
            gradient.setColorAt(1, QtGui.QColor(191, 101, 0))

        #Прорисовка вершины
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(-10, -10, 20, 20)

    #Метод на изменение объекта
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edgeList:
                edge.adjust()
            #Смена позиции окна информации
            try:
                mainWindow.view.infoBox.setPos(self.pos())
                mainWindow.view.infoBox.adjust()
            except AttributeError:
                pass

        return super(Node, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.update()
        super(Node, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.update()
        super(Node, self).mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self.update()
        #Если мы выделили вершину, то перейти по всем соединенным с этой
        #вершиной вершинам и ребрам и выделить их
        for i in range(len(self.edgeList)):
            self.edgeList[i].highlighted = True
            self.edgeList[i].update()
            if self.edgeList[i].source.number == self.number:
                self.edgeList[i].dest.highlighted = True
                self.edgeList[i].dest.update()
            else: 
                self.edgeList[i].source.highlighted = True
                self.edgeList[i].source.update()

        #Присвоение определенных параметров окну с сообщением
        mainWindow.view.infoBox.drawed = True
        mainWindow.view.infoBox.number = self.number
        mainWindow.view.infoBox.setPos(self.pos())
        mainWindow.view.infoBox.adjust()

    def hoverLeaveEvent(self, event):
        self.update()
        #Если мы убрали курсор с вершины, то перейти по всем соединенным с этой
        #вершиной вершинам и ребрам и отменить выделение
        for i in range(len(self.edgeList)):
            self.edgeList[i].highlighted = False
            self.edgeList[i].update()
            if self.edgeList[i].source.number == self.number:
                self.edgeList[i].dest.highlighted = False
                self.edgeList[i].dest.update()
            else: 
                self.edgeList[i].source.highlighted = False
                self.edgeList[i].source.update()

        #Присвоение определенных параметров окну с сообщением
        mainWindow.view.infoBox.drawed = False
        mainWindow.view.infoBox.adjust()
        
class GraphWidget(QtGui.QGraphicsView):
    def __init__(self):
        super(GraphWidget, self).__init__()

        #Синтаксический сахар
        viewPortUpdate = QtGui.QGraphicsView.BoundingRectViewportUpdate

        self.timerId = 0

        #Выставление свойств для GraphicsView и сцены
        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(viewPortUpdate)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        #Градиент для фона
        gradient = QtGui.QLinearGradient(self.rect().topLeft(),
                                         self.rect().bottomLeft())
        gradient.setColorAt(1, QtGui.QColor(48, 48, 48))
        gradient.setColorAt(0, QtGui.QColor(80, 80, 80))
        self.setBackgroundBrush(QtGui.QBrush(gradient))

        #Добавление вершин и связей между ними
        self.nodes = []
        
        #Вершины сортировки
        self.lis = []

        #Стартовые позиции точек
        maximum = 100
        minimum = -100

        #Количество размещенных точек и переменные для последовательного
        #распределения точек
        count = 0
        countConst = 8
        mult = 1
        
        #Создание вершин, перемещение их в массив и присвоение им значений
        for i in range(len(mainWindow.bytesArray)):
            node = Node(self)
            node.number = mainWindow.bytesArray[i]
            self.nodes.append(node)
            
        #Генерация дерева
        for i in range(len(self.nodes)):
            count += 1
            scene.addItem(self.nodes[i])
            if i == 0:
                self.nodes[i].setPos(random.randint(minimum, maximum),
                                     random.randint(minimum, maximum))
            elif i > 0:
                #Выставляем позицию будущей точки
                self.nodes[i].setPos(random.randint(minimum, maximum),
                                     random.randint(minimum, maximum))
                #Проверяаем, пока новая точка пересекается с уже имеющимися
                #Задаем случайное расположение новой точки
                while self.nodes[i].collidingItems() != []:
                    self.nodes[i].setPos(random.randint(minimum, maximum),
                                         random.randint(minimum, maximum))

            #Если количество вершин больше чем задано в области, то
            #увеличиваем область
            if count > countConst * mult:
                mult += 2
                maximum += 50
                minimum -= 50

        #Соединяем вершины графа
        for i in range(len(mainWindow.edgesArray)):
            first = None
            second = None
            for j in range(len(self.nodes)):
                if mainWindow.edgesArray[i][0] == self.nodes[j].number:
                    first = self.nodes[j]
                if mainWindow.edgesArray[i][1] == self.nodes[j].number:
                    second = self.nodes[j]
            if first != second:
                scene.addItem(Edge(first, second))

        #Добавление на сцену сообщения с информацией
        self.infoBox = Info()
        scene.addItem(self.infoBox)

    #Событие на прокрутку ролика мыши (отдаление и приближение)
    def wheelEvent(self, event):
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        scaleFactor = 1.15
        if event.delta() > 0:
            self.scale(scaleFactor, scaleFactor)
        else:
            self.scale(1.0 / scaleFactor, 1.0 / scaleFactor)

class MainWindow(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle("GPcreater")
        self.resize(800, 600)

        #Уникальные вершины
        self.bytesArray = set()
        #Cписок смежности
        self.edgesArray = []

        #Данные вершин
        self.gest = dict()
        self.edgesGest = dict()

        #Меню
        self.menuBar = QtGui.QMenuBar(self)
        self.fileMenu = QtGui.QMenu("Меню")
        self.fileMenu.addAction("Відкрити файл", self.openFile)
        self.fileMenu.addAction("Відкрити XML файл", self.openXML)
        self.fileMenu.addAction("Зберегти у XML", self.createXML)
        self.fileMenu.addAction("Вихід", self.closingEvent)
        self.menuBar.addMenu(self.fileMenu)
        
        self.algMenu = QtGui.QMenu("Алгоритм")
        self.algMenu.addAction("Виконати пошук в ширину", self.dialogSearch)
        self.algMenu.addAction("Очистити", self.clean)
        self.menuBar.addMenu(self.algMenu)

        self.helpMenu = QtGui.QMenu("Допомога")
        self.helpMenu.addAction("Керівництво користувача", self.userHelp)
        self.helpMenu.addAction("Про програму", self.aboutApp)
        self.menuBar.addMenu(self.helpMenu)

        #Layout и свойства
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.setMenuBar(self.menuBar)
        self.setLayout(self.mainLayout)

        #Вкладки и их свойства 
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Triangular)
        self.tabWidget.tabCloseRequested.connect(self.tabWidget.removeTab)
        
        self.mainLayout.addWidget(self.tabWidget)

    def openFile(self):
        self.question = DialogCountBytes()
        self.question.show()

    def dialogSearch(self):
        if mainWindow.tabWidget.count() == 1:
            if len(self.gest) == 0:
                self.dlg = QtGui.QMessageBox(QtGui.QMessageBox.Information,
                                        "Нема побудованих графів",
                                        "Для запуску пошуку необхідно побудувати граф")
                self.dlg.show()
            else:       
                self.BFSDialog = DialogBFSSearch()
                self.BFSDialog.show()
        elif mainWindow.tabWidget.count == 0:
            pass

    #Метод на обновление цвета, после поиска в ширину
    def clean(self):
        try:
            for i in range(len(self.view.nodes)):
                self.view.nodes[i].color = None
                self.view.nodes[i].update()
        except AttributeError:
            pass

    #Алгоритм поиска в ширину
    def BFSSearch(self, number, arr):
        array = []
        fifo = [number]
        temp = []
        exclude = set()
        exclude.add(number)

        for i in range(len(arr)):
            if arr[i] != [number, number]:
                array.append(arr[i])

        while True:
            for k in range(len(fifo)):
                for i in range(len(array)):
                    for j in range(len(array[i])):
                        if fifo[k] in array[i] and array[i][j] != fifo[k]:
                            if array[i][j] not in temp and array[i][j] not in exclude:
                                temp.append(array[i][j])
                                exclude.add(array[i][j])
                        if k == len(fifo) - 1 and i == len(array) - 1 and j == len(array[i]) - 1:
                            if len(temp) == 0:
                                return
                            else:
                                mainWindow.view.lis.append(temp)
                                fifo = temp
                                temp = []

    def aboutApp(self):
        self.about = About()
        self.about.show()

    def userHelp(self):
        webbrowser.open(os.getcwd() + r"\help\about.HTML")

    #Открытие XML файла
    def openXML(self):
        try:
            path = QtGui.QFileDialog.getOpenFileName(self)

            try:
                tree = ET.parse(path)
                nodes = tree.getroot()

                #Обнуление значений вершин и ребер
                self.edgesArray.clear()
                self.bytesArray.clear()

                #Считываем значения
                for i in range(len(nodes)):
                    temporary = nodes[i].text.split(",")
                    #Первый "байт"
                    first = int(temporary[0])
                    #Второй "байт"
                    second = int(temporary[1])

                    #Добавляем в множество что бы выделить уникальные
                    self.bytesArray.add(first)
                    self.bytesArray.add(second)

                    #Добавляем в список смежности
                    self.edgesArray.append([first, second])

                self.bytesArray = list(self.bytesArray)

                #Создание закладки
                self.tab = QtGui.QWidget()
                #Присвоение индекса для вкладки и внесени значений в словарь
                i = 0
                while True:
                    if i not in self.gest:
                        self.gest[i] = self.bytesArray
                        self.edgesGest[i] = self.edgesArray
                        self.tab.number = i
                        break
                    i += 1

                self.bytesArray.sort()            
                #Непосредственное добавление
                self.tabWidget.removeTab(self.tabWidget.currentIndex())
                self.tabWidget.addTab(self.tab, os.path.basename(path))
                
                #Layout для закладки
                self.tabLayout = QtGui.QVBoxLayout()
                self.tabLayout.setMargin(0)
                self.tab.setLayout(self.tabLayout)
                
                #Сцена для закладки
                self.view = GraphWidget()
                self.tabLayout.addWidget(self.view)
                self.bytesArray = set(self.bytesArray)
            except xml.etree.ElementTree.ParseError:
                self.dlg = QtGui.QMessageBox(QtGui.QMessageBox.Warning, " ",
                                             "Файл не у форматі XML.")
                self.dlg.show()
        except FileNotFoundError:
            pass

    #Запись в XML
    def createXML(self):
        try:
            nodes = ET.Element("nodes")

            for i in range(len(mainWindow.edgesArray)):
                field = ET.SubElement(nodes, "field")
                field.text = str(mainWindow.edgesArray[i][0]) + "," + str(mainWindow.edgesArray[i][1])

            tree = ET.ElementTree(nodes)
            tree.write("result.txt")
            if mainWindow.tabWidget.count() == 1:
                self.dlg = QtGui.QMessageBox(QtGui.QMessageBox.Information,
                                        " ",
                                        "Результати успішно записані.")
            else:       
                self.dlg = QtGui.QMessageBox(QtGui.QMessageBox.Information,
                                        " ",
                                        "Нема відкритих файлів.")
            self.dlg.show()
        except AttributeError:
            pass
                    
    def closingEvent(self):
        self.close()

#Диалгоговое окно для старта поиска в ширину
class DialogBFSSearch(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle("Пошук в ширину")
        self.resize(200, 300)
        self.setFont(font12)

        self.i = 0
        self.j = 0
        
        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"),
                     self.time_click)
        

        self.layout = QtGui.QVBoxLayout()

        self.label = QtGui.QLabel("Оберіть вершину зі списку")
        self.layout.addWidget(self.label)
        
        #Создание списка и заполнение его значениями вершин
        self.listWidget = QtGui.QListWidget()
        for i in range(len(mainWindow.gest[mainWindow.tabWidget.currentIndex()])):
            self.listWidget.addItem(str(mainWindow.gest[mainWindow.tabWidget.currentIndex()][i]))
            
        self.layout.addWidget(self.listWidget) 
        
        self.button = QtGui.QPushButton("Почати пошук")
        self.button.clicked.connect(self.btnClick)
        self.layout.addWidget(self.button)
        
        self.setLayout(self.layout)

    #Запуск поиска в ширину
    def btnClick(self):
        self.close()
        #Окрас первой вершины
        for i in range(len(mainWindow.view.nodes)):
            if mainWindow.view.nodes[i].number == int(self.listWidget.currentItem().text()):
                mainWindow.view.nodes[i].color = "gray"
                mainWindow.view.nodes[i].update()
                mainWindow.view.nodes[i].color = "black"
                mainWindow.view.nodes[i].update()
                mainWindow.BFSSearch(int(self.listWidget.currentItem().text()),
                                     mainWindow.edgesGest[mainWindow.tabWidget.currentIndex()])

        #Запуск таймера
        self.timer.start(200)

    #Обработка события на клик таймера
    def time_click(self):
        if self.i == len(mainWindow.view.lis):
            self.timer.stop()
            mainWindow.bytesArray = list(mainWindow.bytesArray)
            for i in range(len(mainWindow.bytesArray)):
                for j in range(len(mainWindow.view.lis)):
                    for k in range(len(mainWindow.view.nodes)):
                        if mainWindow.bytesArray[i] not in mainWindow.view.lis[j]:
                            mainWindow.view.nodes[k].color = "black"
                            mainWindow.view.nodes[k].update()

            mainWindow.bytesArray = set(mainWindow.bytesArray)
            
            mainWindow.view.lis = []
            self.i = 0
            self.j = 0
            self.exclude = set()
            self.dial = QtGui.QMessageBox(QtGui.QMessageBox.Information, " ",
                                     "Пошук у ширину завершено!")
            self.dial.show()
        elif self.j == len(mainWindow.view.lis[self.i]):
            for k in range(len(mainWindow.view.nodes)):
                if mainWindow.view.nodes[k].number in mainWindow.view.lis[self.i]:
                    mainWindow.view.nodes[k].color = "black"
                    mainWindow.view.nodes[k].update()
            self.i += 1
            self.j = 0
        else:
            for k in range(len(mainWindow.view.nodes)):
                if mainWindow.view.lis[self.i][self.j] == mainWindow.view.nodes[k].number:
                    if mainWindow.view.nodes[k].color == "black":
                        pass
                    else:
                        mainWindow.view.nodes[k].color = "gray"
                        mainWindow.view.nodes[k].update()
            self.j += 1

#Диалоговое окно на количество считываемых байтов
class DialogCountBytes(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle(" ")
        self.resize(300, 100)
        self.setFont(font12)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.layout = QtGui.QVBoxLayout()
        
        self.label = QtGui.QLabel("Введіть число від 1 до 2048.")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.spinBox = QtGui.QSpinBox()
        self.spinBox.setSingleStep(2)
        self.spinBox.setMaximum(2048)
        self.spinBox.setValue(2048)
        self.layout.addWidget(self.spinBox)

        self.btnLayout = QtGui.QHBoxLayout()
        self.buttonOk = QtGui.QPushButton("Підтвердити")
        self.buttonOk.clicked.connect(self.btnOkAction)
        self.btnLayout.addWidget(self.buttonOk)
        self.buttonNo = QtGui.QPushButton("Відмініти")
        self.buttonNo.clicked.connect(self.btnNoAction)
        self.btnLayout.addWidget(self.buttonNo)

        self.layout.addLayout(self.btnLayout)
        self.setLayout(self.layout)

    def btnOkAction(self):
        #Обнуление значений вершин и ребер
        mainWindow.edgesArray.clear()
        mainWindow.bytesArray.clear()
        
        #Выбор, чтение файла
        self.count = self.spinBox.value() // 2
        path = QtGui.QFileDialog.getOpenFileName(self)
        try:
            f = open(path, "rb")
            for i in range(0, self.count):
                #Считываем первый байт
                first = int.from_bytes(f.read(1), byteorder = "little")
                #Считываем второй байт
                second = int.from_bytes(f.read(1), byteorder = "little")
                #Добавляем в множество что бы выделить уникальные вершины
                mainWindow.bytesArray.add(first)
                mainWindow.bytesArray.add(second)
                #Добавляем в список смежности
                mainWindow.edgesArray.append([first, second])
            f.close()

            mainWindow.bytesArray = list(mainWindow.bytesArray)

            #Создание закладки
            mainWindow.tab = QtGui.QWidget()
            #Присвоение индекса для вкладки и внесени значений в словарь
            i = 0
            while True:
                if i not in mainWindow.gest:
                    mainWindow.gest[i] = mainWindow.bytesArray
                    mainWindow.edgesGest[i] = mainWindow.edgesArray
                    mainWindow.tab.number = i
                    break
                i += 1

            mainWindow.bytesArray.sort()            
            #Непосредственное добавление
            mainWindow.tabWidget.removeTab(mainWindow.tabWidget.currentIndex())
            mainWindow.tabWidget.addTab(mainWindow.tab, os.path.basename(path))
            
            #Layout для закладки
            mainWindow.tabLayout = QtGui.QVBoxLayout()
            mainWindow.tabLayout.setMargin(0)
            mainWindow.tab.setLayout(mainWindow.tabLayout)
            
            #Сцена для закладки
            mainWindow.view = GraphWidget()
            mainWindow.tabLayout.addWidget(mainWindow.view)
            mainWindow.bytesArray = set(mainWindow.bytesArray)
            self.close()
        except FileNotFoundError:
            pass

    def btnNoAction(self):
        self.close()
#Диалоговое окно о программе
class About(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle("Про програму")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setFixedSize(370, 250)

        self.layout = QtGui.QVBoxLayout()

        self.iconLabel = QtGui.QLabel()
        self.iconLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.iconLabel.setPixmap(QtGui.QPixmap("GPcreater.png"))
        self.layout.addWidget(self.iconLabel)

        self.GPLabel = QtGui.QLabel("GPcreater")
        self.GPLabel.setFont(font12)
        self.GPLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.GPLabel)

        self.labelVersion = QtGui.QLabel("v. 1.00")
        self.labelVersion.setFont(font12)
        self.labelVersion.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.labelVersion)

        self.label = QtGui.QLabel("Програма розроблена Клименко Олегом")
        self.label.setFont(font12)
        self.layout.addWidget(self.label)

        self.labelMail = QtGui.QLabel("oleg_klimenko@inbox.ru")
        self.labelMail.setFont(font12)
        self.labelMail.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.labelMail)
        
        self.setLayout(self.layout)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("GPcreater.png"))

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())

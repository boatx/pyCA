import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Cell(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.speed = 250
        self.run=False
        self.table=[ [ 0 for i in range(36) ] for j in range(36) ]
        self.border()
        self.setWindowTitle('Automat komorkowy-piasek')
        self.setToolTip('Zaznacz komorki')
        self.stbn=QPushButton('Start',self)
        self.stbn.setToolTip('Start Symulacji')
        self.clbn=QPushButton('Wyczysc',self)
        self.clbn.setToolTip('Wyczysc plansze')
        self.timer = QTimer(self)
        self.slider = QSlider(Qt.Horizontal,self)
        self.slider.setMinimum(1)
        self.slider.setMaximum(500)
        self.slider.setToolTip('Predkosc symulacji')
        self.slider.setValue(self.speed)
        self.connect(self.timer, SIGNAL("timeout()"),self.sand)
        self.connect(self.stbn, SIGNAL("clicked()"),self.start)
        self.connect(self.clbn, SIGNAL("clicked()"),self.clean)
        self.connect(self.slider, SIGNAL('valueChanged(int)'),self.setValue)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.stbn)
        buttonLayout.addWidget(self.clbn)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignBottom)
        layout.addLayout(buttonLayout, Qt.AlignCenter)
        layout.addWidget(self.slider, Qt.AlignCenter)
        self.setLayout(layout)
        self.resize(450, 480)

    def border(self):
        for i in (0, 35):
            for j in range(36):
                self.table[j][i] = 2
        for i in range(1, 35):
            self.table[35][i] = 2

    def setValue(self):
        self.speed = self.slider.value()
        if self.run == True:
            self.timer.stop()
            self.timer.start(self.speed)

    def start(self):
        if self.run == False:
            self.run = True
            self.stbn.setToolTip('Koniec Symulacji')
            self.stbn.setText('Koniec')
            self.timer.start(self.speed)
        else:
            self.run = False
            self.stbn.setToolTip('Start')
            self.stbn.setText('Start Symulacji')
            self.timer.stop()

    def clean(self):
        for i in range(36):
            for j in range(36):
                self.table[i][j] = 0
        self.border()
        self.repaint()

    def mousePressEvent(self, event):
        x = (event.x()-50)/10
        y = (event.y()-50)/10
        button = event.button()
        if (x<=34 and x>=1) and (y<=34 and y>=1):
            if button == 1:
                if self.table[y][x] == 1:
                    self.table[y][x] = 0
                else:
                    self.table[y][x] = 1

            elif button == 2:
                if self.table[y][x] == 2:
                    self.table[y][x] = 0
                else:
                    self.table[y][x] = 2

            self.repaint()
        else:
            pass

    def mouseMoveEvent(self, event):
        x = (event.x()-50)/10
        y = (event.y()-50)/10
        button = event.button()
        if (x <= 34 and x >=1) and (y<=34 and y>=1):
            if button == 1:
                if self.table[y][x] == 1:
                    self.table[y][x] = 0
                else:
                    self.table[y][x] = 1

            elif button == 2:
                if self.table[y][x] == 2:
                    self.table[y][x] = 0
                else:
                    self.table[y][x] = 2

            self.repaint()
        else:
            pass

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), QBrush(Qt.white))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QBrush(Qt.gray), 1, Qt.SolidLine))
        for i in range(36):
            a = i*10+50
            for j in range(36):
                b = j*10+50
                if self.table[j][i]==1:
                    painter.fillRect(a,b,10,10,QBrush(Qt.blue))
                elif self.table[j][i]==2:
                    painter.fillRect(a,b,10,10,QBrush(Qt.black))
                #rysowanie siatki linii
        for i in range(60, 410, 10):
            painter.drawLine(60, i, 400, i)
        for i in range(60, 410, 10):
            painter.drawLine(i, 60, i, 400)
        painter.end()

    def sand(self):
        for l in range(34, -1, -1):
            for k in range(34, -1, -1):
                if self.table[l][k] == 1:
                    if self.table[l+1][k] == 0:
                        self.table[l][k] = 0
                        self.table[l+1][k] = 1
                    elif self.table[l+1][k+1] == 0 and self.table[l][k+1] != 2:
                        self.table[l][k] = 0
                        self.table[l+1][k+1] = 1
                    elif self.table[l+1][k-1] == 0 and self.table[l][k-1] == 0:
                        self.table[l][k]=0
                        self.table[l+1][k-1] = 1
        self.repaint()





if __name__ == "__main__":

    app = QApplication(sys.argv)
    life = Cell()
    life.show()
    sys.exit(app.exec_())

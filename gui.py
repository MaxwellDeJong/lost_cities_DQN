# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
import cardstable

from Rocketman_ddqn import Environment, Agent, RandomAgent
        
class CardTableWidgetExtend(cardstable.cardTableWidget):
    """ extension of CardTableWidget """
    def __init__(self, env):

        super(CardTableWidgetExtend, self).__init__(env)

        
class MainWindow(QMainWindow):
    def __init__(self, env, parent=None):
        super(MainWindow, self).__init__(parent)

        # create widgets             
        self.label1 = QLabel("DDQN+PR Rocketman")
        self.label1.setFont(QFont('Andalus', 24))        
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setMaximumHeight(30)        
        self.label1.setStyleSheet("QLabel { background-color : black; color : white; font: bold }")
        self.cardsTable = CardTableWidgetExtend(env)
        
        # main layout
        self.mainLayout = QVBoxLayout()
        
        # add all widgets to the main vLayout
        self.mainLayout.addWidget(self.label1)
        self.mainLayout.addWidget(self.cardsTable)
        
        # central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)        
#        
#        # set central widget
        self.setCentralWidget(self.centralWidget)
        
        # PLAYGROUND        
#        self.cardsTable.dealDeck()
        #self.cardsTable.addCard('c_K')
        #self.cardsTable.getCardsList()[0].setPos(0,0)        
#        self.cardsTable.addCard('d_8')
#        self.cardsTable.addCard('j_r')
#        self.cardsTable.changeCard(1,'h_J', faceDown=True)
#        self.cardsTable.removeCard(51)
        
        self.cardsTable.getCardsList()               
#        self.cardsTable.deal1()

        
if __name__ == "__main__":

    env = Environment()

    stateCnt  = env.env.observation_space.shape[0]
    actionCnt = env.env.action_space.n

    agent = Agent(stateCnt, actionCnt)

    load_random_samples = True
    n_rand_games = 0

    randomAgent = RandomAgent(load_random_samples)

    app = QApplication(sys.argv)
    widget = MainWindow(env.env)
    widget.setWindowTitle("Rocketman")
    widget.setWindowIcon(QIcon('icon.png'))    
    widget.show()
    sys.exit(app.exec_())


from __future__ import print_function
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
from PyQt4 import QtSvg


def get_initial_state():

        p1_hand = [0, 18, 7, 22, 50, 35, 41, 47]
        p2_hand = [3, 10, 49, 30, 5, 11, 29, 21]

        deck = range(52)

        for card in p1_hand:
            deck.remove(card)

        for card in p2_hand:
            deck.remove(card)

        discarded_clubs = [1]
        discarded_diamonds = [16]
        discarded_hearts = [28]
        discarded_spades = [51]

        deck.remove(1)
        deck.remove(16)
        deck.remove(28)
        deck.remove(51)

        discarded_cards = [discarded_clubs, discarded_diamonds, discarded_hearts, discarded_spades]

        p1_played_clubs = [2, 4]
        p1_played_diamonds = []
        p1_played_hearts = [26, 31]
        p1_played_spades = [40]

        p1_played = [p1_played_clubs, p1_played_diamonds, p1_played_hearts, p1_played_spades]

        p2_played_clubs = [6]
        p2_played_diamonds = [13, 14, 15, 17]
        p2_played_hearts = []
        p2_played_spades = [42]

        p2_played = [p2_played_clubs, p2_played_diamonds, p2_played_hearts, p2_played_spades]

        all_played = [p1_played, p2_played]

        for player in range(2):
            for suit in range(4):
                for card in self.all_played[player][suit]:

                    deck.remove(card)

        return (p1_hand, p2_hand, discarded_cards, all_played, deck)


class QGraphicsViewExtend(QGraphicsView):
    """ extends QGraphicsView for resize event handling  """

    def __init__(self, parent=None):

        super(QGraphicsViewExtend, self).__init__(parent)               
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    
    def resizeEvent(self, event):

        self.fitInView(QRectF(0,0,1280,1080),Qt.KeepAspectRatio)
        # self.fitInView(QRectF(self.viewport().rect()),Qt.KeepAspectRatio)


class CardGraphicsItem(QtSvg.QGraphicsSvgItem):
    """ Extends Qt.QGraphicsItem for card items graphics """ 

    def __init__(self, card, ind, svgFile, player, faceDown=False):

        super(CardGraphicsItem, self).__init__(svgFile)

        # special properties
        self.card = card        
        self.ind = ind # index
        self.svgFile = svgFile # svg file for card graphics
        self.player = player # which player holds the card
        self.faceDown = faceDown # does the card faceDown
        self.anim = QPropertyAnimation(self, "pos") # will use to animate card movement
        
        #default properties
        self.setAcceptHoverEvents(True) #by Qt default it is set to False                 


    def hoverEnterEvent(self, event):
        """ event when mouse enter a card """    

        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(15)
        effect.setColor(Qt.red)        
        effect.setOffset(QPointF(-5,0))
        self.setGraphicsEffect(effect)        
    

    def hoverLeaveEvent(self, event):
        """ event when mouse leave a card """    

        self.setGraphicsEffect(None) 
    
    
#    def __repr__(self):                
#        return '<CardGraphicsItem: %d>' % self.card
     
        
class cardTableWidget(QWidget):
    """ main widget for handling the card table """

    def __init__(self, env, parent=None):

        gameboard = env.gameboard

        self.p1_board = gameboard.p1_board
        self.p2_board = gameboard.p2_board

        self.p1_hand = self.p1_board.hand[:]
        self.p2_hand = self.p2_board.hand[:]

        p1_played = [[], [], [], []]
        p2_played = [[], [], [], []]

        self.all_discarded = []

        self.all_played = [p1_played, p2_played]

        self.deck = gameboard.env

        self.p1_card_to_change = None
        self.p1_card_graphics_to_change = None
        self.p1_play = False
        self.p1_discard = False
        self.p1_card_to_draw = None
        self.p1_card_graphics_to_draw = None

        super(QWidget, self).__init__(parent)       

        self.initUI()

        
    def initUI(self):
        """ initialize the view-scene graphic environment """

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 1920, 1080)

        self.view = QGraphicsViewExtend(self.scene)
        self.view.setSceneRect(QRectF(self.view.viewport().rect()))
        self.view.setSceneRect(QRectF(0, 0, 1920, 1080))
        self.view.setRenderHint(QPainter.Antialiasing)        

        layout = QGridLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)        
        self.setBackgroundColor(QColor('green'))

        # special properties
        self.svgCardsPath = "SVG"
        self.cardsGraphItems = [] #holds all the cards items
        self.defInsertionPos = QPointF(0,0)
        self.defAngle = 0
        self.scale = 0.3

        self.numOfPlayers = 2

        self.card_width = 691
        self.card_height = 1056

        deck_x = 10 + self.card_height * self.scale
        discard_y = 60

        self.defHandSpacing = 68
        self.playersHandsPos = [(380, 700, 0), (380, 50, 180)] #(x,y,angle)

        draw_offset = 990 / 4.
        self.discardPos = [(deck_x, discard_y, 90), (deck_x, discard_y + draw_offset, 90), (deck_x, discard_y + 2 * draw_offset, 90), (deck_x, discard_y + 3 * draw_offset, 90)]

        self.deckPos = (deck_x + 540, discard_y + 1.5 * draw_offset, 90)

        self.boardSpacing = 54
        p1_y = 580
        p2_y = 500 - self.card_height * self.scale
        suit_spacing = 220
        self.boardPos = [[(1100, p1_y, 0), (1100 + suit_spacing, p1_y, 0), (1100 + 2 * suit_spacing, p1_y, 0), (1100 + 3 * suit_spacing, p1_y, 0)], 
                [(1100, p2_y, 0), (1100 + suit_spacing, p2_y, 0), (1100 + 2 * suit_spacing, p2_y, 0), (1100 + 3 * suit_spacing, p2_y, 0)]]

        #pen = QPen("cyan")
        pen = QPen()
        #brush = QBrush("blue")
        brush = QBrush()
        self.scene.addRect(QRectF(0,40,340,1000), pen, brush)
#        c = QtSvg.QGraphicsSvgItem('svg\j_b.svg')
#        c.setPos(0,0)
#        self.scene.addItem(c)

        self.dealHands()
        self.dealDeck()

        # self.dealDiscards()

        # self.dealPlayed()
        # print(self.scene.itemAt(110,110))


    def process_click(self, card_graphics):

        card = card_graphics.card
        suit = int(card / 13)

        # If there isn't yet a card to play, update the card to be played
        if (self.p1_hand_card_to_play is None):

            if (card in self.p1_hand):

                self.p1_card_to_change = card
                self.p1_card_to_change = card_graphics

                self.p1_play = -1
                self.p1_discard = -1
                self.p1_card_to_draw = None
                self.p1_card_graphics_to_draw = None

        else:

            # If we have not decided if we will play or discard yet, use
            # this click to make the distinction
            if ((self.p1_play and self.p1_discard) == -1):

                if (card in self.all_discarded[suit]):
                    
                    self.p1_discard = 1
                    self.p1_play = 0

                else:

                    if (self.p1_board.valid_play(card)):

                        self.p1_discard = 0
                        self.p1_play = 1

                    else:

                        self.p1_play = -1
                        self.p1_discard = -1
                        self.p1_card_to_change = None
                        self.p1_card_graphics_to_change = None

                if ((self.p1_play and self.p1_discard) != -1):

                    # animate move
                    card_graphics.anim.setDuration(150)

                    end_pos = find_new_card_pos(card_graphics, 0, self.p1_discard)
                    card_graphics.anim.setEndValue(end_pos)
                    card_graphics.anim.start() 

            else:

                self.p1_card_to_draw = card

                # animate move
                card_graphics.anim.setDuration(150)

                end_pos = find_new_card_pos(card_graphics, 1, 0)
                card_graphics.anim.setEndValue(end_pos)
                card_graphics.anim.start() 

                if (card in deck):

                    draw_int = 0

                else:

                    draw_int = suit + 1

                action = (self.p1_card_to_change, self.p1_play, draw_int)

                self.p1_play = -1
                self.p1_discard = -1
                self.p1_card_to_change = None
                self.p1_card_graphics_to_change = None
                self.p1_card_to_draw = None
                self.p1_card_graphics_to_draw = None

                perform_action()
                
    
    def mousePressEvent(self, event):

        # check if item is a CardGraphicsItem  
        p = event.pos()
        print(p)
        p -= QPoint(10,10) #correction to mouse click. not sure why this happen        
        itemAt = self.view.itemAt(p)       
        print(itemAt)

        if isinstance(itemAt, CardGraphicsItem):

            # Give the card a black outline
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(15)
            effect.setColor(Qt.black)        
            effect.setOffset(QPointF(-5,0))
            self.setGraphicsEffect(effect)        

            # Update figure out the correct action from the click
            self.process_click(card_graphics)

        print(p)

        print("All items at pos: ", end="")
        print(self.view.items(p))

        print("view.mapToScene: ",end="")
        print(self.view.mapToScene(p))

        
    def find_new_card_pos(card_graphics, draw, discard, player=1):

        card = card_graphics.card

        if (player == 1):
            hand = self.p1_hand
        else:
            hand = self.p2_hand

        if (card not in hand):
            return None

        if (draw == 1):

            return self.find_new_card_pos_hand(player)

        if (discard == 1):

            return self.find_new_card_pos_discard(card, player)

        return self.find_new_card_pos_play(card, player)


    def find_new_card_pos_discard(self, card):
        '''Finds postition of card to be discarded.'''

        suit = int(card / 13)

        (x_i, y_i, ang) = self.discardPos[suit]

        return QPointF(x_i, y_i)


    def find_new_card_pos_play(self, card, player=1):
        '''Finds postition of card to be played.'''

        suit = int(card / 13)

        (x_i, y_i, ang) = self.boardPos[player-1][suit]
        current_n_played_cards = len(self.all_played[player-1][suit])
        
        if (player == 1):
            dy = self.boardSpacing
        else:
            dy = -1 * self.boardSpacing

        x_f = x_i
        y_f = y_i + (current_n_played_cards + 1)

        return QPointF(x_f, y_f)


    def find_new_card_pos_hand(self, player=1):
        '''Finds position of card to be added to hand.'''

        if (player == 1):
            (x, y) = self.last_p1_card

        elif (player == 2):
            (x, y) = self.last_p2_card

        return QPointF(x, y)


    def getCenterPoint(self):
        """ finds screen center point """       

        rect = self.view.geometry()       
        print(rect)
        return QPointF(rect.width()/2,rect.height()/2)       

    
    def setBackgroundColor(self, color):
        """ add background color """
        
        brush = QBrush(color)
        self.scene.setBackgroundBrush(brush)
        self.scene.backgroundBrush() 


    def cardsvgFile(self, card):

        if (card == -1):
            name = 'blue_back'

        else:

            suit = int(card / 13)
            face_val = card % 13

            if (suit == 0):
                suit_str = 'C'
            elif (suit == 1):
                suit_str = 'D'
            elif (suit == 2):
                suit_str = 'H'
            elif (suit == 3):
                suit_str = 'S'

            if (face_val == 0):
                face_str = 'A'
            elif (face_val == 10):
                face_str = 'J'
            elif (face_val == 11):
                face_str = 'Q'
            elif (face_val == 12):
                face_str = 'K'
            else:
                face_str = str(face_val + 1)

            name = face_str + suit_str

        fn = os.path.join(self.svgCardsPath, name + ".svg")        
        return fn

            
    def addCard(self, card, player, scale, faceDown=False):
        """ adds CardGraphicsItem graphics to board.
        also updates the total cards list
        """        
        # svg file of the card graphics
        if faceDown:
            svgFile = self.cardsvgFile(-1)
        else:
            svgFile = self.cardsvgFile(card)

        # create CardGraphicsItem instance
        ind = len(self.getCardsList()) + 1
        tmp = CardGraphicsItem(card, ind, svgFile, player, faceDown)

        tmp.setScale(scale)
        tmp.setZValue(ind) # set ZValue as index (last in is up)        
#        self.cardsGraphItems.append(tmp)
        self.scene.addItem(tmp)
        # sanity check
        
        #print("num of cards=" + str(len(self.cardsList)))


    def removeCard(self, card):
        """ removes CardGraphicsItem graphics from board 
        also removes from the total cards list
        """
        if isinstance(card,int):
            allCards = self.getCardsList()
            indices = [c.ind for c in allCards]
            ind = indices.index(card)            
            self.scene.removeItem(allCards[ind])            
        if isinstance(card,CardGraphicsItem):
            self.scene.removeItem(card)


    def changeCard(self, cardIndRemove, card, faceDown=False):       
        """ replace CardGraphicsItem         
        keeps same index and ZValue !
        """
        zValueTmp = self.cardsGraphItems[cardIndRemove].zValue()
        position = self.cardsGraphItems[cardIndRemove].pos()
        angle = self.cardsGraphItems[cardIndRemove].rotation()
        scale = self.cardsGraphItems[cardIndRemove].scale()
        self.scene.removeItem(self.cardsGraphItems[cardIndRemove])
        self.cardsGraphItems.pop(cardIndRemove)
        player = self.cardsList[cardIndRemove].player
        self.cardsList.pop(cardIndRemove)

        # svg file of the card graphics
        if faceDown:
            svgFile = self.cardSvgFile(-1)
        else:
            svgFile = self.cardSvgFile(card)

        ind = cardIndRemove
        self.cardsList.insert(ind,CardItem(card,self.value(card),player,faceDown))        
        tmp = CardGraphicsItem(card, ind, position, svgFile, angle, scale)
        tmp.setZValue(zValueTmp) # set ZValue as previous
        self.cardsGraphItems.insert(ind, tmp)
        self.scene.addItem(self.cardsGraphItems[ind])
        self.checkLists()


    def getCardsList(self):
        """ returns and prints all CardGraphicsItem in scene (disregard other graphics items) """        
        itemsOut=[]
        #print("Cards List:")
        for item in self.scene.items():
            if isinstance(item,CardGraphicsItem):                
                itemsOut.append(item)
                #print("Ind=%3d |card=%4s | Player=%d | faceDown=%r " % \
                #     (item.ind, item.card, item.player, item.faceDown) )                
        #print("Total cards num = " + str(len(itemsOut)))
        return itemsOut


    def dealHands(self):

        hands = [self.p1_hand, self.p2_hand]

        for player in range(1, 3):

            offset = 0

            dx = self.defHandSpacing
            dy = 0

            x, y, ang = self.playersHandsPos[player-1]

            for offset in range(8):

                card = hands[player-1][offset]

                faceDown = False

                if (player == 2):
                    faceDown = True

                self.addCard(card, player, self.scale, faceDown)
                self.getCardsList()[0].setPos(x+dx*offset, y + dy*offset)


    def dealDeck(self):

        player = 0
        faceDown = True
        ang = 90

        (x, y, ang) = self.deckPos

        for card in self.deck:

            self.addCard(card, player, self.scale, faceDown)
            self.getCardsList()[0].setPos(x, y)
            self.getCardsList()[0].rotate(ang)



    def dealDiscards(self):

        player = 0

        for suit in range(4):

            discard_suit = self.discarded_cards[suit]

            (x, y, ang) = self.discardPos[suit]
            print('y: ', y)

            for card in discard_suit:

                self.addCard(card, player, self.scale)
                self.getCardsList()[0].setPos(x, y)
                self.getCardsList()[0].rotate(ang)


    def dealPlayed(self):

        for player in range(1, 3):

            played_cards = self.all_played[player-1]

            if (player == 1):
                dy = self.boardSpacing
            else:
                dy = -1 * self.boardSpacing

            for suit in range(4):

                n_cards_laid = 0

                played_suit = played_cards[suit]

                (x, y, ang) = self.boardPos[player-1][suit]

                if (played_suit):

                    for card in played_suit:

                        card_x = x
                        card_y = y + n_cards_laid * dy

                        print('card: ', card, 'player: ', player, ', x: ', card_x, 'y: ', card_y)

                        self.addCard(card, player, self.scale)
                        self.getCardsList()[0].setPos(x, y + n_cards_laid * dy)
                        self.getCardsList()[0].rotate(ang)

                        n_cards_laid += 1




    def update_scene(action, player):
        pass



def main():

    app = QApplication(sys.argv)
    form = cardTableWidget()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()

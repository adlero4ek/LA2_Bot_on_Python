import cv2

from Targets import *
from AppWindows import *
from PartyMember import *
from ImageProcessing import *

PatryMember1 = PatryMember("1", "K1tty", "K1tty - Flauron.com Lineage 2")
PatryMember1.FillCoordinates(GetWindowInfo(PatryMember1.WindowTitle))
#PatryMember1.debugGetHPLine()
#PatryMember1.debugGetMPLine()


while True:

    print("HP: " + str(PatryMember1.GetPercentOfHP()) + "/ MP: " + str(PatryMember1.GetPercentOfMP()))


#Targets = Target()
#Targets.debugGetHPLine(PatryMember1)
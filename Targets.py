import os
import cv2
import numpy as np

from mss import mss
from MouseAndKeyboard import *

TargetMss = mss()

class Target:
    
    def __init__(self):
    
        self.HpColors   = [[118,37,35]]
        self.HpPanelX1  = 408
        self.HpPanelY1  = 58
        self.HpPanelX2  = 557
        self.HpPanelY2  = 59
        
        self.TargetListColor     = (  0, 255,   0) #Green
        self.TargetStopListColor = (  0,   0, 255) #Red
        self.NextTargetColor     = (255,   0,   0) #Blue

        # Список имен целей для поиска и атаки за ислючением агресивных. В целом если для конрутного случае
        # не требется разделять цели, то достаточно определить один список

        self.TargetList = []
        
        # Список имен целей, которые являются агресивными. При анализце целей сначала выполнятеся
        # поиск агресивных целей, чтобы не нацеплять дополнительных монстров по пути к прочим целям. 
        # При анализе будет сравниваться расстояние до обычной цели и агрусивной, если они "рядом",
        # то приоритет будет определеться не только расстоянием

        self.TargetAgressiveList = []

        # Список имен целей, которых необходимо избегать. Бывают случаи когда на "соседней" поляне кроме целей 
        # для поиска и атаки находятся социальные или агресивные монстры. Если в процессе поиска такие цели выявлены
        # в напрелении ближайщего подходящего монстра для атаки, то меняется направление атаки

        self.TargetStoptList = []

    def LoadTargetList(self, Location):

        LoadTargetListFromImagesDir(Location, self.TargetList, "TargetList")
        LoadTargetListFromImagesDir(Location, self.TargetStoptList, "TargetStoptList")
        LoadTargetListFromImagesDir(Location, self.TargetAgressiveList, "TargetAgressiveList")

    def debugGetHPLine(self, PatryMember):
    
        self.HpPanelX1  = 0
        self.HpPanelY1  = 0
        self.HpPanelX2  = 0
        self.HpPanelY2  = 0
    
        GetHPLine(self, PatryMember)

    def GetPercentOfHealth(self):

        percent = 0
        filled_red_pixels = 0

        bounding_box = {'top': self.HpPanelY1, 
            'left':  self.HpPanelX1, 
            'width': self.HpPanelX2 - self.HpPanelX1, 
            'height': 1}

        cscreen = TargetMss.grab({'top': 0, 'left': 0, 'width': 1, 'height': 1})
        cscreen = TargetMss.grab(bounding_box)

        pixels = np.array(cscreen.pixels).tolist()
        pixels = pixels[0]
        
        if len(pixels) == 0: 
            return percent  

        for pixel in pixels:
            
            if pixel in self.HpColors:
                
                filled_red_pixels += 1

        percent = 100 * filled_red_pixels / len(pixels)

        return percent  

def CheckColorPixel(X, Y, Colors):

    cscreen = TargetMss.grab({'top': Y, 'left': X, 'width': 1, 'height': 1})
    pixels  = np.array(cscreen.pixels).tolist()
    
    if pixels[0][0] in Colors:
        return True

    return False           

def SetYLine(Target, FixX, maxY):

    Y = 1

    while Y <= maxY:
    
        Mouse_Move(FixX, Y)
    
        if CheckColorPixel(FixX, Y, Target.HpColors):
            
            Target.HpPanelY1 = Y
            Target.HpPanelY2 = Y + 1

            break

        Y = Y + 1   

def SetXLeftLine(Target, X, FixY):

    while X > 0:

        Mouse_Move(X, FixY)
     
        if not CheckColorPixel(X, FixY, Target.HpColors):
            
           Target.HpPanelX1 = X + 1;  
           break

        X = X - 1 

def SetXRightLine(Target, CentrX, MaxX, FixY):

    X = CentrX
        
    while X <= MaxX:

        Mouse_Move(X, FixY)
     
        if not CheckColorPixel(X, FixY, Target.HpColors):
            
            Target.HpPanelX2 = X - 1;  
            break

        X = X + 1          

def GetHPLine(Target, PatryMember):

    SetYLine(Target, PatryMember.WindowCentrX,  
        PatryMember.WindowCentrY - 400)

    SetXLeftLine(Target, PatryMember.WindowCentrX, 
        Target.HpPanelY1)

    SetXRightLine(Target,  PatryMember.WindowCentrX,
        PatryMember.WindowWidth, Target.HpPanelY1)

    print("HpPanelX1" + str(Target.HpPanelX1))
    print("HpPanelY1" + str(Target.HpPanelY1))
    print("HpPanelX2" + str(Target.HpPanelX2))
    print("HpPanelY2" + str(Target.HpPanelY2))

def LoadTargetListFromImagesDir(Location, TargetList, ImagesDir):

    Path = "./img/Locations/" + Location + "/" + ImagesDir

    if not os.path.isdir(Path):
        return None

    Files = os.listdir(Path)

    for File in Files:

        TargetName = File.replace(".png", "")
        TargetNameImage = cv2.imread(Path + "/" + File, 0)

        TargetList.append([TargetName, TargetNameImage])  
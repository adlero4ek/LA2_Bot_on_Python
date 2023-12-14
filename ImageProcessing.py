import cv2
import math
import easyocr
import numpy as np

from mss import mss

MainMss = mss()
reader  = easyocr.Reader(['en'], gpu = False)

def GetDistance(MobCenterX, MobCenterY, PatryMember):

    distanceEvcl  = abs(math.hypot(MobCenterX - PatryMember.WindowCentrX, MobCenterY - PatryMember.WindowCentrY))
    distanceJustY = abs(PatryMember.WindowCentrY - MobCenterY)
    distanceJustX = abs(PatryMember.WindowCentrX - MobCenterX)
    
    return (distanceEvcl + distanceJustY + distanceJustX) / 2


def GetBoundingBox(top, left, width, height):

    return {'top': top, 'left': left, 'width': width, 'height': height}

def GetScreen(BoundingBox, PatryMember, ForRadar):

    image = MainMss.grab(GetBoundingBox(0, 0, 1, 1))
    image = MainMss.grab(BoundingBox)
    
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGRA2BGR)
    
    if ForRadar:

        image[0:PatryMember.WindowHeight, 0:(PatryMember.WindowCentrX-300)] = (0, 0, 0)                          # Левая часть экрана, скрывающая персонажей
        image[0:PatryMember.WindowHeight, (PatryMember.WindowCentrX+300):(PatryMember.WindowWidth)] = (0, 0, 0)  # Правая часть экрана, скрывающая карту
        image[0:(PatryMember.WindowCentrY-300), 0:(PatryMember.WindowWidth)] = (0, 0, 0)                         # Верхняя часть экрана, скрывающая бафы, именя целей

    else:

        image[0:200, 0:180] = (0, 0, 0)                  # Левая часть экрана, скрывающая персонажей
        image[0:50,  0:BoundingBox['width']] = (0, 0, 0) # Верхняя часть экрана, скрывающая бафы, именя целей

    return image

def GetContours(image):

    # Значения получены экперементальным путем. Модуль CheckImageConvert используется для 
    # определения значений на конретных условиях использования

    # lower = np.array([0, 0, 190])
    # upper = np.array([40, 40, 255])

    lower = np.array([150, 0, 255])
    upper = np.array([180, 255, 255])

    # Convert to HSV format and color threshold
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)

    # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
    
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    # dilate , more the iteration more the dilation
    # Используется для более четкого определение границ с имена целей

    dilated = cv2.dilate(mask, kernel, iterations=9)
    
     # findContours returns 3 variables for getting contours

    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)         

    # Испольузется для сохранения в файлы имен целей

    DilatedToCreateFiles = cv2.dilate(mask, kernel, iterations=1)
    
    return contours, mask, DilatedToCreateFiles 

def GetCurrentTargetsFromContours(Targets, Contours, DilatedImage, PatryMember):

    CurrentTargets = {}

    for contour in Contours:
    
        [x, y, w, h] = cv2.boundingRect(contour)

        if (w < 35 and h < 35) or (w > 200):
            continue

        ImageFromContour = DilatedImage[y:y + h, x:x + w]
       
        TargetName, TargetType = GetTargetNameFromTargetsListImage(Targets, ImageFromContour)

        if TargetName is None:
            continue

        MobCenterX  = int(x + (w/2)) - 5
        MobCenterY  = int(y + h) #int(y + (h/2)) + 20#50 Отступ от нижней гранцы рамки (имени) до "головы" монстра  
        distance    = GetDistance(MobCenterX, MobCenterY, PatryMember)

        CurrentTargets[distance] = {'TargetName': TargetName, 'TargetType': TargetType, 
            'CenterX': MobCenterX, 'CenterY': MobCenterY, 
            'rectangleX': x, 'rectangleY': y,
            'rectangleW': x + w, 'rectangleH': y + h}

    return CurrentTargets   

def MatchTemplate(TargetNameImage, ImageFromContour):

    wth, hth = ImageFromContour.shape
    wtp, htp = TargetNameImage.shape

    if not (wth >= wtp and hth >= htp):
       return False    

    res = cv2.matchTemplate(TargetNameImage, ImageFromContour, cv2.TM_CCORR_NORMED)

    if not res.any():
        return False    
        
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > 0.8:
        return True

    return False


def GetTargetNameFromTargetsListImage(Targets, ImageFromContour):

    #TargetType = 1 - TargetFromList
    #TargetType = 2 - TargetAgressiveList
    #TargetType = 3 - TargetStoptList

    for TargetFromList in Targets.TargetList:

        if MatchTemplate(TargetFromList[1], ImageFromContour):
            return TargetFromList[0], 1

    for TargetFromList in Targets.TargetAgressiveList:

        if MatchTemplate(TargetFromList[1], ImageFromContour):
            return TargetFromList[0], 2
     
    for TargetFromList in Targets.TargetStoptList:

        if MatchTemplate(TargetFromList[1], ImageFromContour):
            return TargetFromList[0], 3

    return None, None 

def GetTargetNameFromImage(image, reader, TargetCacheNames):
    

    # Распознование текта по картинке не совсем точное и главное быстрое, например,
    # для имени Glow могут возвращаться следующие комбинации: 'Glot', 'Glo#', 'Glow', 'Gloit IWied', 'Gio#'
    # что затрудянет опознование, но использование кеша с именама и данными изображений скорость работы
    # заметно увеличивается 
     
    TargetName = ""
    TargetKey  = image.tobytes() 

    img      = cv2.resize(image, (0,0), fx=3, fy=3)
    kernel   = np.ones((5,5), np.uint8)
    dilation = cv2.dilate(img, kernel, iterations = 1)

    if not TargetKey in TargetCacheNames:
        
        bounds = reader.readtext(dilation)
        
        if len(bounds) > 0:

          TargetName = bounds[0][1]
          TargetCacheNames[TargetKey] = TargetName

    else: 

        TargetName = TargetCacheNames[TargetKey]

    return  TargetName


def GetNearestTarget(image, Targets, CurrentTargets, PatryMember, DisplayGraphicElements):

    nearestX   = 0
    nearestY   = 0
    TargetType = 0

    distanceMinTargetList = 10000
    distanceMinTargetStoptList = 10000
    distanceMinTargetAgressiveList = 10000

    for TargetID in CurrentTargets:

        CurrentTarget = CurrentTargets[TargetID]

        TargetName     = CurrentTarget["TargetName"]
        TargetColor    = None
        TargetDistance = TargetID

        if CurrentTarget["TargetType"] == 1:

            TargetColor = Targets.TargetListColor
            distanceMinTargetList = min(distanceMinTargetList, TargetDistance)

        elif CurrentTarget["TargetType"]  == 2:
            
            TargetColor = Targets.TargetListColor
            distanceMinTargetAgressiveList = min(distanceMinTargetAgressiveList, TargetDistance)

        elif CurrentTarget["TargetType"]  == 3:
            
            TargetColor = Targets.TargetStopListColor
            distanceMinTargetStoptList = min(distanceMinTargetStoptList, TargetDistance)
        
        if DisplayGraphicElements:
        
            if not TargetColor is None:        
                
                cv2.rectangle(image, (CurrentTarget["rectangleX"], CurrentTarget["rectangleY"]), (CurrentTarget["rectangleW"], CurrentTarget["rectangleH"]), 
                    TargetColor, 1)

                cv2.line(image, (PatryMember.WindowCentrX, PatryMember.WindowCentrY),
                        (CurrentTarget["CenterX"], CurrentTarget["CenterY"]), TargetColor, 1)

                cv2.putText(image, str(round(TargetDistance, 2)), 
                    (CurrentTarget["rectangleX"], CurrentTarget["rectangleY"] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, TargetColor)

            else: 

                cv2.rectangle(image, (CurrentTarget["rectangleX"], CurrentTarget["rectangleY"]), (CurrentTarget["rectangleW"], CurrentTarget["rectangleH"]),
                    (0, 255, 255), 2)

                cv2.putText(image, TargetName, 
                    (CurrentTarget["rectangleX"], CurrentTarget["rectangleY"] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255))
    
    distanceMin = min(distanceMinTargetList, distanceMinTargetAgressiveList)
    
    if distanceMinTargetAgressiveList < 250:
        distanceMin = distanceMinTargetAgressiveList

    if distanceMin < 10000 and distanceMinTargetStoptList > 250:
        
        CurrentTarget = CurrentTargets[distanceMin]
        
        nearestX   = CurrentTarget["CenterX"]
        nearestY   = CurrentTarget["CenterY"]
        TargetType = CurrentTarget["TargetType"]

        if DisplayGraphicElements:

            cv2.rectangle(image, (CurrentTarget["rectangleX"], CurrentTarget["rectangleY"]), 
                (CurrentTarget["rectangleW"], CurrentTarget["rectangleH"]),
                Targets.NextTargetColor, 2)

            cv2.line(image, (PatryMember.WindowCentrX, PatryMember.WindowCentrY),
                (CurrentTarget["CenterX"], CurrentTarget["CenterY"]), Targets.NextTargetColor, 2)

    return nearestX, nearestY, TargetType

def CheckTargetMarker(roi, template):

    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    ret, th1 = cv2.threshold(roi, 224, 255, cv2.THRESH_TOZERO_INV)
    #cv2.imwrite('./Screens/th1.png', th1)

    ret, th2 = cv2.threshold(th1, 135, 255, cv2.THRESH_BINARY)
    #cv2.imwrite('./Screens/th2.png', th2)

    ret, tp1 = cv2.threshold(template, 224, 255, cv2.THRESH_TOZERO_INV)
    #cv2.imwrite('./Screens/tp1.png', tp1)

    ret, tp2 = cv2.threshold(tp1, 135, 255, cv2.THRESH_BINARY)
    #cv2.imwrite('./Screens/tp2.png', tp2)

    if not hasattr(th2, 'shape'):
        return False

    wth, hth = th2.shape
    wtp, htp = tp2.shape

    if wth > wtp and hth > htp:
        res = cv2.matchTemplate(th2, tp2, cv2.TM_CCORR_NORMED)
        if res.any():
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.7:
                return True
            else:
                return False

    return False

def TargetIsPet(PetNameTemplateImage):

    BoundingBox  = GetBoundingBox(34, 390, 170, 20)

    roi = MainMss.grab(BoundingBox)
    roi = cv2.cvtColor(np.array(roi), cv2.COLOR_BGR2GRAY)

    ret, th1 = cv2.threshold(roi, 224, 255, cv2.THRESH_TOZERO_INV)
    ret, th2 = cv2.threshold(th1, 135, 255, cv2.THRESH_BINARY)

    return MatchTemplate(th2, PetNameTemplateImage)

def PersonIsDied(DiedTargetTemplateImage, Image):

    roi = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)

    ret, th1 = cv2.threshold(roi, 224, 255, cv2.THRESH_TOZERO_INV)
    ret, th2 = cv2.threshold(th1, 135, 255, cv2.THRESH_BINARY)

    return MatchTemplate(DiedTargetTemplateImage, th2)   
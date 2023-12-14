import cv2

from Targets import *
from AppWindows import *
from PartyMember import *
from ImageProcessing import *

def PerformGeneralInitialization():
   
    PatryMember1 = PatryMember("1", "K1tty", "K1tty - Flauron.com Lineage 2")
    PatryMember1.FillCoordinates(GetWindowInfo(PatryMember1.WindowTitle))

    return PatryMember1

def СreateImageFilesByTargetNames():

    # Формирование изображений имен целей (монстров) в файлы с целью будущей классификации по папкам (типам) 
    #   TargetType = 1 - TargetFromList
    #   TargetType = 2 - TargetAgressiveList
    #   TargetType = 3 - TargetStoptList
    
    PatryMember1 = PerformGeneralInitialization()

    Targets = Target()
    TargetCacheNames = {}
    
    BoundingBoxPatryMember = GetBoundingBox(PatryMember1.WindowY1, PatryMember1.WindowX1, 
        PatryMember1.WindowWidth, int(PatryMember1.WindowHeight * 0.7))

    while True:

        image = GetScreen(BoundingBoxPatryMember, PatryMember1, False)

        contours, mask, dilated = GetContours(image)

        for contour in contours:
            
            [x, y, w, h] = cv2.boundingRect(contour)

            if (w < 35 and h < 35) or (w > 200):
                continue

            image_mask    = mask[y:y + h, x:x + w]
            image_dilated = dilated[y:y + h, x:x + w]

            TargetName = GetTargetNameFromImage(image_mask, 
                reader, TargetCacheNames)

            if TargetName == '' or TargetName == "Treasure Chest" or len(TargetName) < 3:
                continue

            cv2.putText(image, TargetName, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255))
            
            cv2.rectangle(image, (x, y), (x + w, y + h), Targets.TargetListColor, 2)
                       
            cv2.imwrite("img/temp/" + TargetName + ".png", image_dilated) 

        cv2.imshow('image', image)

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break

def AnalyseLocationTargets():
    
    PatryMember1 = PerformGeneralInitialization()

    Targets = Target()
    Targets.LoadTargetList("School of Magic")

    BoundingBoxPatryMember = GetBoundingBox(PatryMember1.WindowY1, PatryMember1.WindowX1, 
        PatryMember1.WindowWidth, int(PatryMember1.WindowHeight * 0.7))

    while True:

        # Формирование снимка экрана в необходимых границах. 
        image = GetScreen(BoundingBoxPatryMember, PatryMember1, False)
        
        # Получение контуров имен целей по цветовой маске
        contours, mask, DilatedImage = GetContours(image)

        # Получение текущих целей на экране для расчета расстояний и визуальной отрисовки
        CurrentTargets = GetCurrentTargetsFromContours(Targets, contours, DilatedImage, PatryMember1)

        if len(CurrentTargets) > 0:

            # Расчет cледующей к атаке цели c учетом расстояния и вида цели        
            GetNearestTarget(image, Targets, CurrentTargets, PatryMember1, True)

        cv2.imshow('screen', np.array(image))

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break

#СreateImageFilesByTargetNames()
AnalyseLocationTargets()
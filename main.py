import cv2
import time

from Targets import *
from AppWindows import *
from PartyMember import *
from ImageProcessing import *
from MouseAndKeyboard import *

from threading import Thread

PatryMember1 = None
PatryMember2 = None

NearestTargetFromRadar = {'X': 0, 'Y': 0, 
    'Distance': 0, 'TargetType': 0,
    'CountTargets': 0}

def TimeDifference(TestTime):

    return time.time() - TestTime 
        
def TimeDifferenceGreaterThanValue(TestTime, Value):

    if time.time() - TestTime > Value:
        return True
    else:
        return False

def PrintLog(Srt, DebugMode):

    if DebugMode:
        print(Srt)  

def RandomXY(A, B):
    
    return int(random.uniform(A, B))

def ActivePatryMember2(ToAttack):

    global PatryMember1
    global PatryMember2

    if not PatryMember2 is None:
    
        X = 1050 + RandomXY(50, 250)
        Y = 330  + RandomXY(50, 150)

        Mouse_SmoothMoveRandomSpeed(X, Y)
        Mouse_LeftClick(X, Y)
        
        PatryMember2.PickUp()
        PatryMember2.SelfBuffsCheck()

        if ToAttack:
            Keyboard_ClickButton("F2")
        else:    
            Keyboard_ClickButton("F3")

        X = PatryMember1.WindowCentrX
        Y = PatryMember1.WindowCentrY

        Mouse_Move(X, Y)
        Mouse_LeftClick(X, Y)

    PatryMember1.SelfBuffsCheck()

def FillDataOfNearestTargetFromRadar(X, Y, TargetType, PatryMember1, CountTargets):

    global NearestTargetFromRadar

    if X > 0 and Y > 0:

        NearestTargetFromRadar = {'X': X,'Y': Y, 
            'Distance': GetDistance(X, Y, PatryMember1), 'TargetType': TargetType,
            'CountTargets': CountTargets}
    else:

        NearestTargetFromRadar = {'X': 0, 'Y': 0,
            'Distance':  10000, 'TargetType': 0,
            'CountTargets': 0}       

def StartRadar(BoundingBoxRadar, PatryMember1, Location, DebugMode):
    
    global NearestTargetFromRadar

    RadarTargets = Target()
    RadarTargets.LoadTargetList(Location)

    while True:

        # Формирование снимка экрана в необходимых границах. 
        image = GetScreen(BoundingBoxRadar, PatryMember1, False)
        
        # Получение контуров имен целей по цветовой маске
        contours, mask, DilatedImage = GetContours(image)

        # Получение текущих целей на экране для расчета расстояний и визуальной отрисовки
        CurrentTargets = GetCurrentTargetsFromContours(RadarTargets, contours, DilatedImage, PatryMember1)

        if len(CurrentTargets) > 0:

           # Расчет cледующей к атаке цели c учетом расстояния и вида цели        

           CenterX, CenterY, TargetType = GetNearestTarget(image, RadarTargets, CurrentTargets, PatryMember1, DebugMode)

           FillDataOfNearestTargetFromRadar(CenterX, CenterY, TargetType, PatryMember1, len(CurrentTargets))

        else:

            FillDataOfNearestTargetFromRadar(0, 0, None, None, None)
                    
        if DebugMode:
            
            cv2.imshow("Radar", image)

            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                break

def main():

    # True - Отображение отладочных сообщений 

    DebugMode = False

    # Определение персонажей 
    
    global PatryMember1
    global PatryMember2

    PatryMember1 = Warlock("1", "Kltty", "Kltty - Flauron.com Lineage 2")
    #PatryMember1 = BountyHunter("1",  "GoDie",  "GoDie - MasterWork II")
    PatryMember1.FillCoordinates(GetWindowInfo(PatryMember1.WindowTitle))
    PatryMember1.SelfBuffsInit()
    PatryMember1.SelfBuffsCheck()

    #PatryMember2 = PhantomRanger("2", "AdlerOFF", "AdlerOFF - MasterWork II")
    #PatryMember2.SelfBuffsInit()
    #PatryMember2.SelfBuffsCheck()
    
    # Определение целей в текущей локации прокачки

    global NearestTargetFromRadar

    Location = "School of Magic"
    
    Targets = Target()
    Targets.LoadTargetList(Location)

    # Изображение, которое показыается игрой если мышка на цел указан
    
    TargetTemplateImage     = cv2.imread('img/template_target.png', 0)
    PetNameTemplateImage    = cv2.imread('img/Improved Baby Buffalo.png', 0)
    DiedTargetTemplateImage = cv2.imread('img/To Village.png', 0)

    # Время начала поиска цели. Если в течении TargetSearchTimeout секунд цель не найдена, то персонаж поворачивается вокруг своей оси,
    # используя метод: TurnLeft

    StarTimeOfSearch = time.time()
    StarTimeOfAttack = 0

    # Максимальное количество секунд поиска цели. Если в течении данного времени цель не найдена, то персонаж поворачивается 
    
    TargetSearchTimeout = 5

    # Максимальное количество секунд атаки цели. Если в течении данного времени цель не убита, то выполянется поиск новой цели. Цель может быть
    # далеко / выбран сундук /  персонаж застрял и прочее

    TargetAttackTimeout = 10

    # Границы отображаемеого экрана для поиска монстров. используется как ограничение скриншотов игры.

    BoundingBoxPatryMember = GetBoundingBox(PatryMember1.WindowY1, PatryMember1.WindowX1, 
        PatryMember1.WindowWidth, int(PatryMember1.WindowHeight * 0.7))
    
    th = Thread(target = StartRadar, args = (BoundingBoxPatryMember, PatryMember1, Location, DebugMode))
    th.start()

    while True:

        if PersonIsDied(DiedTargetTemplateImage, GetScreen(BoundingBoxPatryMember, PatryMember1, False)):
            break

        if PatryMember1.GetPercentOfHP() < 60 or PatryMember1.GetPercentOfMP() < 30:
            continue

        if NearestTargetFromRadar['X'] == 0:

            PrintLog("Поиск цели...." + str(TimeDifference(StarTimeOfSearch)), DebugMode)
            
            if TimeDifferenceGreaterThanValue(StarTimeOfSearch, TargetSearchTimeout):
                
                PatryMember1.PickUp()
                PatryMember1.TurnLeft()
                PatryMember1.GoForward()
                
                StarTimeOfSearch = time.time() 

            continue

        PrintLog("Ближайшая цель найдена по имени: " + str(TimeDifference(StarTimeOfSearch)), DebugMode)

        if TimeDifference(StarTimeOfSearch) > 10:
            
            PatryMember1.TurnLeft()
            PatryMember1.GoForward()
            
            StarTimeOfSearch = time.time()

            continue

        # Плавное перемещение курсора мышки ближайшей цели с целью определения возможности атаки.
        # Если цель далеко, то используем мышку для наведения, чтобы не зацепить команду NextTarget далеких монстров и не палиться

        nearestX = NearestTargetFromRadar['X']# - 10
        nearestY = NearestTargetFromRadar['Y']

        PatryMember1.PickUp()

        Mouse_SmoothMoveRandomSpeed(nearestX, nearestY)
        
        # Здесь ожидается, чтопри попадании курсора мыши на цель рядом с именем цели появится дополнительные визуальные эффекты, 
        # которые хранятся в файле: img/template_target.png

        if not CheckTargetMarker(GetScreen(BoundingBoxPatryMember, PatryMember1, False), TargetTemplateImage):
            continue

        PrintLog(("Ближайшая цель может быть атакована: " + str(TimeDifference(StarTimeOfSearch))), DebugMode)

        # Если цель далеко, то используем мышку для наведения, чтобы не зацепить команду NextTarget далеких монстров и не палиться
        Mouse_LeftClick(nearestX, nearestY)

        # Если целью выбран пет (такое бывает при клике мышкой рядом с персонажем), то выполяем поиск дальше
        if TargetIsPet(PetNameTemplateImage):
            continue

        if not CheckColorPixel(Targets.HpPanelX1, Targets.HpPanelY1, Targets.HpColors):
            continue

        StarTimeOfAttack = time.time()
        PatryMember1.Attack()
        
        # Переключение на второго персонажа, использование макроса-ассист, 
        # возврат на первого первонажа
        
        ActivePatryMember2(True)
        
        PatryMember1.Attack()
        PatryMember1.UsedSkillsWhenAttackingInit()
        
        # Контроль уровня здоровья

        PercentOfHealthPrevious = Targets.GetPercentOfHealth()
        PercentOfHealthCurrent  = PercentOfHealthPrevious
        
        while True:

            PatryMember1.UsedSkillsWhenAttackingCheck()

            RadarDistance = NearestTargetFromRadar['Distance']
            RadarTargetType = NearestTargetFromRadar['TargetType']

            PrintLog("Атакуем цель:" + str(TimeDifference(StarTimeOfAttack)), DebugMode)
            
            # Цель убита 
            if PercentOfHealthCurrent <= 0:
                break

            # Рядом обнаружена агресивная цель, переключаемся на неё
            if RadarTargetType == 2 and (100 > RadarDistance < 150):
                break    

            PercentOfHealthCurrent = Targets.GetPercentOfHealth()

            # Использование атакующих умений при условии, что фактическая атака началась, т.е. % здоровья < 100
            #if PercentOfHealthCurrent < 100:
            # PatryMember1.UsedSkillsWhenAttackingCheck()

            # Уровень здоровья изменился, значит цель выбрана правильно и урон наносится.
            if PercentOfHealthCurrent != PercentOfHealthPrevious:
                StarTimeOfAttack = time.time()

            if TimeDifferenceGreaterThanValue(StarTimeOfAttack, 2):
                PatryMember1.Attack()

            if TimeDifferenceGreaterThanValue(StarTimeOfAttack, TargetAttackTimeout):
                PatryMember1.Attack()
                PrintLog("Уровень здоровья цели не уменьшается больше максимального ожидания: " + str(TimeDifference(StarTimeOfAttack)) + str(TargetAttackTimeout), DebugMode)
                break
       
            PercentOfHealthPrevious = PercentOfHealthCurrent

            time.sleep(1)

        # Поднятие дропа
                
        PatryMember1.PickUp()
        PatryMember1.PickUp()
        #PatryMember1.Sweep()

        # Переключение на второго персонажа, использование макроса-ассист, 
        # возврат на первого первонажа
        
        ActivePatryMember2(False)
            
        StarTimeOfSearch = time.time()

main()
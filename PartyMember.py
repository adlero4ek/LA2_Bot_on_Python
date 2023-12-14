import numpy as np

from MouseAndKeyboard import *
from mss import mss
from MouseAndKeyboard import *

TargetMss = mss()

class PatryMember:
    
  def __init__(self, Number, Name, WindowTitle):
    
    self.Number = Number
    self.Name = Name
    
    self.WindowTitle = WindowTitle
    self.WindowX1 = 0
    self.WindowY1 = 0
    self.WindowX2 = 0
    self.WindowY2 = 0
    self.WindowWidth  = 0
    self.WindowHeight = 0
    self.WindowCentrX = 0
    self.WindowCentrY = 0

    self.HpColors  = [
      [165, 48, 33],
      [165, 48, 34],
      [165, 48, 35],
      [165, 48, 36],
      [165, 48, 37],
      [165, 49, 34],
      [165, 49, 35],
      [165, 49, 36],
      [165, 49, 37],
      [165, 50, 34],
      [165, 50, 35],
      [165, 50, 36],
      [165, 50, 37],
      [165, 50, 38],
      [165, 51, 38],
      [165, 51, 39],
      [165, 51, 40],
      [165, 52, 40],
      [165, 52, 41]]
    
    self.HpPanelX1 = 17
    self.HpPanelY1 = 82
    self.HpPanelX2 = 166
    self.HpPanelY2 = 83

    self.MpColors  = [
      [74, 103, 143],
      [74, 103, 143]]
    
    self.MpPanelX1 = 17
    self.MpPanelY1 = 86
    self.MpPanelX2 = 166
    self.MpPanelY2 = 87
    
  def FillCoordinates(self, WindowInfo):

    self.WindowX1 = WindowInfo['x1']
    self.WindowY1 = WindowInfo['y1']
    self.WindowX2 = WindowInfo['x2']
    self.WindowY2 = WindowInfo['x2']

    self.WindowWidth  = WindowInfo['width']
    self.WindowHeight = WindowInfo['height']
    self.WindowCentrX = WindowInfo['centrX']
    self.WindowCentrY = WindowInfo['centrY']  

  def debugGetHPLine(self):
      
    self.HpPanelX1 = 0 # 100% HP
    self.HpPanelY1 = 83
    self.HpPanelX2 = 0 #  0% HP
    self.HpPanelY2 = 83

    GetHPLine(self)

  def debugGetMPLine(self):
      
    self.MpPanelX1 = 0
    self.MpPanelY1 = 0
    self.MpPanelX2 = 0
    self.MpPanelY2 = 0

    GetMPLine(self)

  def GetPercentOfHP(self):

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

  def GetPercentOfMP(self):

    percent = 0
    filled_red_pixels = 0

    bounding_box = {'top': self.MpPanelY1, 
        'left':  self.MpPanelX1, 
        'width': self.MpPanelX2 - self.MpPanelX1, 
        'height': 1}

    cscreen = TargetMss.grab({'top': 0, 'left': 0, 'width': 1, 'height': 1})
    cscreen = TargetMss.grab(bounding_box)

    pixels = np.array(cscreen.pixels).tolist()
    pixels = pixels[0]
    
    if len(pixels) == 0: 
        return percent  

    for pixel in pixels:
        
        if pixel in self.MpColors:
            
            filled_red_pixels += 1

    percent = 100 * filled_red_pixels / len(pixels)

    return percent  

  # Управление движением персонажа

  def TurnLeft(self):

      Keyboard_PushButton("LeftArrow")
      time.sleep(random.uniform(0.5, 1.5))
      Keyboard_UnPushButton("LeftArrow")

  def TurnRight(self):

      Keyboard_PushButton("RightArrow")
      time.sleep(random.uniform(0.5, 1.5))
      Keyboard_UnPushButton("RightArrow")

  def GoForward(self):

      Keyboard_PushButton("UpArrow")
      time.sleep(random.uniform(0.5, 1.0))
      Keyboard_UnPushButton("UpArrow")
  
  # Управление поведением

  def Attack(self):
  
    Keyboard_ClickButton("F1")
  
  def NextTarget(self):
      
    Keyboard_ClickButton("F8")
    Keyboard_ClickButton("F1")
  
  def PickUp(self):

    Keyboard_ClickButton("F4")                          

  # Управление бафами персонажа

  def SelfBuffsInit(self):

    for SelfBuff in self.SelfBuffs:
      SelfBuff[3] = 0

  def SelfBuffsCheck(self):

    СurrentTime = time.time()

    for SelfBuff in self.SelfBuffs:

        if SelfBuff[3] > СurrentTime:
            continue

        RandomDalay()
        Keyboard_ClickButton(SelfBuff[2])

        SelfBuff[3] = СurrentTime + 60 * SelfBuff[1]

  # Управление атакующми умениями

  def UsedSkillsWhenAttackingInit(self):

    # 0 - Умение
    # 1 - Горячая клавиша (Hotkey)
    # 2 - Количество секунд "отката" умнения (Cooldown)
    # 3 - Количество использования на одной цели
    # 4 - Следующие время использование
    # 5 - Оставщиеся количество использования умения на одной цели

    СurrentTime = time.time()
    
    # Сдвиг в 1 секунду меду применениями умений

    i = 0

    for UsedSkill in self.UsedSkillsWhenAttacking:
      
      UsedSkill[4] = СurrentTime + i
      UsedSkill[5] = UsedSkill[3]
      i+=3

  def UsedSkillsWhenAttackingCheck(self):

    # 0 - Умение
    # 1 - Горячая клавиша (Hotkey)
    # 2 - Количество секунд "отката" умнения (Cooldown)
    # 3 - Количество использования на одной цели
    # 4 - Следующие время использование
    # 5 - Оставщиеся количество использования умения на одной цели

    СurrentTime = time.time()

    for UsedSkill in self.UsedSkillsWhenAttacking:

        if UsedSkill[4] > СurrentTime or UsedSkill[5] == 0:
            continue

        RandomDalay()
        
        Keyboard_ClickButton(UsedSkill[1])
        
        # if UsedSkill[0] == "Wind strike":
        #   Mouse_LeftClick(self.WindowCentrX, self.WindowCentrY + 150)

        UsedSkill[4] = UsedSkill[2] + СurrentTime
        UsedSkill[5] = UsedSkill[5] - 1   

class BountyHunter(PatryMember):

  # Управление бафами персонажа
  
  SelfBuffs = [["FighterBuffControl", 30, "F9", 0]]
  
  # 0 - Умение
  # 1 - Горячая клавиша (Hotkey)
  # 2 - Количество секунд "отката" умнения (Cooldown)
  # 3 - Количество использования на одной цели
  # 4 - Следующие время использование
  # 5 - Оставщиеся количество использования умения на одной цели

  UsedSkillsWhenAttacking = [["Spoil", "F2", 3, 1, 0, 0],
    ["Stun", "F5", 3, 1, 0, 0]]

  def Stun(self):

    Keyboard_ClickButton("F5")                          

  def Spol(self):

    Keyboard_ClickButton("F2")  

  def Sweep(self):

    Keyboard_ClickButton("F3") 

class PhantomRanger(PatryMember):

  # Управление бафами персонажа

  SelfBuffs = [["FighterBuffControl", 30, "F9", 0],
               ["RapidShot", 15, "F10",  0]] 
  
class Warlock(PatryMember):

  # Управление бафами персонажа
  
  SelfBuffs = []
  
  # 0 - Умение
  # 1 - Горячая клавиша (Hotkey)
  # 2 - Количество секунд "отката" умнения (Cooldown)
  # 3 - Количество использования на одной цели
  # 4 - Следующие время использование
  # 5 - Оставщиеся количество использования умения на одной цели

  UsedSkillsWhenAttacking = [["Wind strike", "F1", 5, 4, 0, 0],
    ["Ice bolt", "F2", 2, 4, 0, 0]]

def GetMPLine(PatryMember):

  PatryMember.MpPanelY1, PatryMember.MpPanelY2 = SetYLine(PatryMember.MpColors, 20, PatryMember.WindowCentrY - 400)

  PatryMember.MpPanelX1 = SetXLeftLine(PatryMember.MpColors, 20, PatryMember.MpPanelY1)

  PatryMember.MpPanelX2 = SetXRightLine(PatryMember.MpColors, 20, PatryMember.WindowCentrX, PatryMember.MpPanelY1)

  print("MpPanelX1" + str(PatryMember.MpPanelX1))
  print("MpPanelY1" + str(PatryMember.MpPanelY1))
  print("MpPanelX2" + str(PatryMember.MpPanelX2))
  print("MpPanelY2" + str(PatryMember.MpPanelY2))

def GetHPLine(PatryMember):

  PatryMember.HpPanelY1, PatryMember.HpPanelY2 = SetYLine(PatryMember.HpColors, 20, PatryMember.WindowCentrY - 400)
  
  PatryMember.HpPanelX1 = SetXLeftLine(PatryMember.HpColors, 20, PatryMember.HpPanelY1)
    
  PatryMember.HpPanelX2 = SetXRightLine(PatryMember.HpColors, 20, PatryMember.WindowCentrX, PatryMember.HpPanelY1)
  
  print("HpPanelX1" + str(PatryMember.HpPanelX1))
  print("HpPanelY1" + str(PatryMember.HpPanelY1))
  print("HpPanelX2" + str(PatryMember.HpPanelX2))
  print("HpPanelY2" + str(PatryMember.HpPanelY2))

def CheckColorPixel(X, Y, Colors):

    cscreen = TargetMss.grab({'top': Y, 'left': X, 'width': 1, 'height': 1})
    pixels  = np.array(cscreen.pixels).tolist()
    
    #print("X: "+ str(X) + " Y: " + str(Y) + " clr:" + str(pixels[0][0]))

    if pixels[0][0] in Colors:
        return True

    return False  
  
def SetYLine(Color, FixX, maxY):

  Y = 1

  while Y <= maxY:
  
    Mouse_Move(FixX, Y)
    
    if CheckColorPixel(FixX, Y, Color):
        break

    Y = Y + 1   

  return Y, Y + 1     

def SetXLeftLine(Color, X, FixY):

  while X > 0:

    Mouse_Move(X, FixY)
  
    if not CheckColorPixel(X, FixY, Color):
        break

    X = X - 1 

  return X + 1

def SetXRightLine(Color, CentrX, MaxX, FixY):

  X = CentrX
      
  while X <= MaxX:

    Mouse_Move(X, FixY)
  
    if not CheckColorPixel(X, FixY, Color):
        break

    X = X + 1  

  return X - 1    
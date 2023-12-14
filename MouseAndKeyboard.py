import time
import random

from ctypes import *

lib = cdll.LoadLibrary("./DLL/mydll_x64.dll")  # Загрузка библиотеки
b5  = "vid_a7fe&pid_bb23"                      # Идентификатор устройства
b6  = 1189                                     # Серийный номер устройства

KeyboardButtons = {"F1": 58, "F2": 59, "F3": 60, "F4":  61, "F5":  62, "F6":  63, 
                   "F7": 64, "F8": 65, "F9": 66, "F10": 67, "F11": 68, "F12": 69,
                   "PageDown":   78,
                   "RightArrow": 79,
                   "LeftArrow":  80,
                   "DownArrow":  81,
                   "UpArrow":    82}

# Общая функциональность

def RandomDalay():

    dalay = random.uniform(0.01, 0.05)
    time.sleep(dalay)

# Управление клавиатурой

def ButtonID(ButtonName):
    
    return KeyboardButtons[ButtonName]

def Keyboard_ClickButton(ButtonName): 
          
    if ButtonName in KeyboardButtons:
        
        RandomDalay()

        lib.roche(1, ButtonID(ButtonName), 0, 0, b5, b6)
        lib.roche(8, ButtonID(ButtonName), 0, 0, b5, b6)

def Keyboard_PushButton(ButtonName): 

    if ButtonName in KeyboardButtons:

        RandomDalay()

        lib.roche(1, ButtonID(ButtonName), 0, 0, b5, b6)     

def Keyboard_UnPushButton(ButtonName): 

    if ButtonName in KeyboardButtons:

        RandomDalay()
        lib.roche(8, ButtonID(ButtonName), 0, 0, b5, b6)    

# Управление мышкой

class POINT(Structure):

    _fields_ = [("x", c_long), ("y", c_long)]

def DrawLine(x1=0, y1=0, x2=0, y2=0):

    coordinates = []

    dx = x2 - x1
    dy = y2 - y1

    sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
    sign_y = 1 if dy > 0 else -1 if dy < 0 else 0

    if dx < 0:
        dx = -dx
    if dy < 0:
        dy = -dy

    if dx > dy:
        pdx, pdy = sign_x, 0
        es, el = dy, dx
    else:
        pdx, pdy = 0, sign_y
        es, el = dx, dy

    x, y = x1, y1

    error, t = el / 2, 0

    coordinates.append([x, y])

    while t < el:
        error -= es
        if error < 0:
            error += el
            x += sign_x
            y += sign_y
        else:
            x += pdx
            y += pdy
        t += 1
        coordinates.append([x, y])

    return coordinates

def Mouse_Move(X,Y):
        
    lib.roche(3, 0, X, Y, b5, b6) 
   
def Mouse_LeftClick(X,Y):

    # Одиночный клик левой кнопкой мыши

    RandomDalay()

    lib.roche(3, 1, X, Y, b5, b6) 
    lib.roche(3, 0, X, Y, b5, b6)

def Mouse_LeftDblClick(X,Y):

    # Двойной клик левой кнопкой мыши

    RandomDalay()

    lib.roche(3, 1, X, Y, b5, b6) 
    lib.roche(3, 0, X, Y, b5, b6)
    lib.roche(3, 1, X, Y, b5, b6) 
    lib.roche(3, 0, X, Y, b5, b6)

def Mouse_GetCursorPosition():
    
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y}

def Mouse_SmoothMove(x, y):
    
    pt = Mouse_GetCursorPosition()

    coordinates = DrawLine(pt['x'], pt['y'], x, y)

    x = 0
    for dot in coordinates:
        x += 1
        if x % 2 == 0 and x % 3 == 0:
            Mouse_Move(dot[0], dot[1])

def Mouse_SmoothMoveRandomSpeed(x, y):
         
    pt = Mouse_GetCursorPosition()

    coordinates    = DrawLine(pt['x'], pt['y'], x, y)
    coordinatesLen = len(coordinates)
    
    #для точного позиционирования за 30 пикелей будем идти по одному 
    
    CoordinatesLenForPrecisePositioning = min(coordinatesLen, abs(coordinatesLen - 30))

    x = 0

    while x < coordinatesLen:

        dot = coordinates[x]
        Mouse_Move(dot[0], dot[1])
        
        if x > CoordinatesLenForPrecisePositioning:
            x = x + 1    
        else:
            x = x + int(random.uniform(10, 20))
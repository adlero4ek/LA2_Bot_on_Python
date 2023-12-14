import ctypes

WindowInfo  = {}
WindowTitle = ""

# import pyautogui

# for x in pyautogui.getAllWindows():  
#     print(x.title)

def GetWindowInfo(SearchWindowTitle):

    global WindowInfo
    global WindowTitle

    WindowTitle = SearchWindowTitle

    EnumWindows = ctypes.windll.user32.EnumWindows
    
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, 
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    
    EnumWindows(EnumWindowsProc(GetWindowCoordinates), 0)

    return WindowInfo

def GetWindowCoordinates(hwnd, lParam):
    
    global WindowInfo
    global WindowTitle

    GetWindowTextW       = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible      = ctypes.windll.user32.IsWindowVisible

    length = GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    
    GetWindowTextW(hwnd, buff, length + 1)

    if IsWindowVisible(hwnd):

        if len(buff.value) > 0 and buff.value.find(WindowTitle) > -1:

            rect = ctypes.wintypes.RECT()
            
            GetWindowRect  = ctypes.windll.user32.GetWindowRect
            GetWindowRect(hwnd, ctypes.pointer(rect))
            
            w = rect.right - rect.left
            h = rect.bottom - rect.top

            WindowInfo['x1'] = rect.left
            WindowInfo['y1'] = rect.top
            
            WindowInfo['x2'] = rect.right
            WindowInfo['y2'] = rect.bottom

            WindowInfo['width'] = w
            WindowInfo['height'] = h

            WindowInfo['centrX'] = int(h/2) - 40
            WindowInfo['centrY'] = int(w/2) + 50

            ctypes.windll.user32.SetForegroundWindow(hwnd)
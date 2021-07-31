import cv2
from PIL import ImageGrab
import numpy as np
import webbrowser
import psutil
import win32gui
import pyautogui
import pyperclip
from time import sleep


class sussy_scraper():
    def __init__(self, browser="Firefox"):
        self.location = None
        self.shape = None
        self.browser = browser

    def find_browser(self, hwnd, extra):
        if self.browser in win32gui.GetWindowText(hwnd):
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            self.location = (x, y)
            self.shape = (w, h)

    def get_browser_window(self):
        win32gui.EnumWindows(self.find_browser, None)
        if not self.location:
            return
        return self.location, self.shape

    def checkIfProcessRunning(self, processName):
        '''
        Check if there is any running process that contains the given name processName.
        '''
        #Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if processName.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def grab_browser_frame(self):
        # Take screenshot using PyAutoGUI
        img = ImageGrab.grab(bbox=(self.location[0], self.location[1],
                                   self.shape[0], self.shape[1]))  # bbox specifies specific region (bbox= x,y,width,height *starts top-left)

        # Convert the screenshot to a numpy array
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def scrape_proto(self):
        webbrowser.open('http://google.co.kr', new=2)
        if self.checkIfProcessRunning(self.browser):
            sleep(2)
            self.get_browser_window()
            pyautogui.getWindowsWithTitle(self.browser)[0].activate()
            pyautogui.press("f12")
            sleep(2)
            frame = self.grab_browser_frame()
            cv2.imshow("scrape", frame)
            pyautogui.hotkey('ctrl', 'c')
            body = pyperclip.paste()
            print(body)
        else:
            sleep(1)

        while True:
            if cv2.waitKey(1) == ord('q'):
                break
        cv2.destroyAllWindows()

scraper = sussy_scraper()
scraper.scrape_proto()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
from PIL import ImageGrab, Image
import sys
import pyocr
import pyocr.builders
import re
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chromedriver_binary

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, -1, '', (0, 0), wx.DefaultSize, wx.STAY_ON_TOP)
        self.SetSize(wx.Display().GetGeometry().GetSize())
        self.SetBackgroundColour('#FFFFe0')
        self.SetTransparent(30)
        self.regHotkey()
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour('Blue')
        self.panel.Hide()
        
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            exit(1)
        self.tool = tools[0]

        options = webdriver.ChromeOptions()
        options.add_argument('--app=https://www.deepl.com/translator')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(20)
        self.src_textarea = driver.find_element_by_css_selector('.lmt__textarea.lmt__source_textarea.lmt__textarea_base_style')

    def regHotkey(self):
        new_id = wx.NewIdRef(count=1)
        self.RegisterHotKey(new_id, wx.MOD_ALT, wx.WXK_SPACE)
        self.Bind(wx.EVT_HOTKEY, lambda event:self.Show(True), id=new_id)

    def OnMouseLeftDown(self, event):
        # print('MouseDown')
        x1, y1 = x0, y0 = wx.GetMousePosition()
        self.panel.SetSize(x0, y0, 0, 0)
        self.panel.Show()
        while wx.GetMouseState().leftIsDown:
            x1, y1 = wx.GetMousePosition()
            xl, xg = sorted((x0, x1))
            yl, yg = sorted((y0, y1))
            self.panel.SetSize(xl, yl, xg - xl, yg - yl)
            # print(xl, yl, xg - xl, yg - yl)
        self.panel.Hide()
        # print('MouseUp')
        self.Hide()

        im = ImageGrab.grab(bbox=(xl, yl, xg, yg))

        en_text = self.tool.image_to_string(
            im,
            lang="eng",
            builder=pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        en_text = re.sub(r'\s+', ' ', en_text).replace('|', 'I')
        print(en_text)
        self.src_textarea.clear()
        self.src_textarea.send_keys(en_text)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        self.SetTopWindow(frame)
        self.SetExitOnFrameDelete(False)
        return True

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

#!/usr/local/bin/python
# DO NOT use this she-bang line unless you've managed to magically make
# wxPython run on the Mac-native Python

# ----------------------------------------------------

# Bounce in Python
# use with Arduino Uno program BounceArduino.ino

# Author: Thy Doan Mai Le
# Originally created: 7/18/2019
# Last Update : 7/18/2019
#               7/23/2019

# -----------------------------------------------------

# IMPORTANT NOTE: Program will only return the difference between bounce times
#                 The student will be required to take the logarithmic of these
#                   time differences in order to extract the coefficient of restitution

# Thy - 07/23/2019

# ------------------------------------------------------


import wx

if wx.__version__[0] == '4':
    import wx.adv

import os
import matplotlib as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np
import serial
import serial.tools.list_ports
import sys
import numpy as np

# -------------------------------------------------------
# GLOBAL VARIABLES
xxx = np.linspace(2, 30, num=29)
yyy = np.zeros(29, np.int)

ser = serial.Serial()
ychan = 0
tempchan = 0
first = True
count = 0
temp = np.zeros(len(yyy))

# -------------------------------------------------------
# MAIN WINDOW


class MainWindow(wx.Frame):
    def __init__(self, parent, title, position, size):
        # Connect to Uno routine
        self.unoPort = 'None'
        self.unoMsg = 'No Uno Connected.'
        self.ConnectToUno()

        # Create main window
        wx.Frame.__init__(self, parent, title=title, pos=position, size=size)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.CreateMenu()
        self.CreateGraphPanel()
        self.CreateButtonPanel()

        frame_box = wx.BoxSizer(wx.VERTICAL)
        frame_box.Add(self.panel, flag=wx.EXPAND, proportion=1, border=10)
        frame_box.Add(self.buttonpanel, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)

        self.SetSizer(frame_box)
        self.Show()
        self.Layout()
    # --------------------------------------------------------

    def CreateMenu(self):
        menubar = wx.MenuBar()
        filemenu = wx.Menu()

        self.aboutItem = filemenu.Append(wx.ID_ABOUT, '&About xBOU')
        filemenu.AppendSeparator()

        self.startItem = filemenu.Append(-1, "Start...\tCtrl+1")
        self.stopItem = filemenu.Append(-1, "Stop...\tCtrl+2")
        self.saveItem = filemenu.Append(-1, "Save...\tCtrl+3")
        self.quitItem = filemenu.Append(-1, "Quit...\tCtrl+4")

        menubar.Append(filemenu, "&File")

        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnStart, self.startItem)
        self.Bind(wx.EVT_MENU, self.OnStop, self.stopItem)
        self.Bind(wx.EVT_MENU, self.OnQuit, self.quitItem)
        self.Bind(wx.EVT_MENU, self.OnSave, self.saveItem)

        self.stopItem.Enable(False)
        self.saveItem.Enable(False)

    # --------------------------------------------------------

    def CreateGraphPanel(self):
        panel = wx.Panel(self)
        self.panel = panel
        # matplotlib 3.1 demands plt.figure.Figure
        self.figure = plt.figure.Figure()

        self.axis = self.figure.add_subplot(1,1,1)
        self.figure.subplots_adjust(left=0.1, right=0.975, top=0.98, bottom=0.075)

        self.axis.set_yscale('linear')
        self.figurepanel = FigureCanvas(self.panel, -1, self.figure)
        self.draw()
        self.graph_box = wx.BoxSizer(wx.HORIZONTAL)

        self.graph_box.Add(self.figurepanel, flag=wx.EXPAND, proportion=1)
        self.panel.SetSizer(self.graph_box)
    # --------------------------------------------------------

    def CreateButtonPanel(self):
        self.buttonpanel = wx.Panel(self)
        buttonpanel = self.buttonpanel

        self.startbutton = wx.Button(buttonpanel, label='Start', size=(90,30))
        self.stopbutton = wx.Button(buttonpanel, label='Stop', size=(90, 30))
        self.savebutton = wx.Button(buttonpanel, label='Save', size=(90, 30))
        self.quitbutton = wx.Button(buttonpanel, label='Quit', size=(110, 30))
        self.startbutton.Bind(wx.EVT_BUTTON, self.OnStart)
        self.stopbutton.Bind(wx.EVT_BUTTON, self.OnStop)
        self.savebutton.Bind(wx.EVT_BUTTON, self.OnSave)
        self.quitbutton.Bind(wx.EVT_BUTTON, self.OnQuit)
        self.ts = wx.StaticText(buttonpanel, -1, "Connected to UNO on port: " + self.unoPort, size=(-1, 30),
                                style=wx.ALIGN_CENTER)
        self.buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        # What is buttonbox?
        self.buttonbox.Add(self.ts, flag=wx.EXPAND | wx.ALL, proportion=4)
        self.buttonbox.AddStretchSpacer(prop=100)
        self.buttonbox.Add(self.startbutton)
        self.buttonbox.Add(self.stopbutton)
        self.buttonbox.Add(self.savebutton)
        self.buttonbox.Add(self.quitbutton)

        self.buttonpanel.SetSizer(self.buttonbox)
        self.Layout()
        self.startbutton.Enable()
        self.stopbutton.Disable()
        self.savebutton.Disable()
        self.quitbutton.Enable()
    # -----------------------------------------------------------

    def OnStart(self, event):
        global xxx, yyy, remains

        self.Bind(wx.EVT_IDLE, self.OnIdle)
        print('Data collection started...')
        self.draw()
        self.startbutton.Disable()
        self.stopbutton.Enable()
        self.savebutton.Disable()
        self.quitbutton.Disable()
        self.startItem.Enable(False)
        self.stopItem.Enable(True)
        self.saveItem.Enable(False)
        self.quitItem.Enable(False)
        self.ser.write('g')
        self.remains = ''

    # -----------------------------------------------------------
    def OnStop(self, event):
        self.ser.write('s')
        print('Data Collection stopped.')
        self.Unbind(wx.EVT_IDLE)
        self.startbutton.Enable()
        self.stopbutton.Disable()
        self.savebutton.Enable()
        self.quitbutton.Enable()
        self.startItem.Enable(True)
        self.stopItem.Enable(False)
        self.saveItem.Enable(True)
        self.quitItem.Enable(True)
        self.ClearBuffer()
        self.draw()

    # -----------------------------------------------------------
    def OnSave(self, event):
        self.Unbind(wx.EVT_IDLE)
        self.startbutton.Enable()
        self.stopbutton.Disable()
        self.savebutton.Enable()
        self.quitbutton.Enable()
        self.startItem.Enable(True)
        self.stopItem.Enable(False)
        self.saveItem.Enable(True)
        self.quitItem.Enable(True)
        dlg = wx.FileDialog(self, "Save data as...", \
                            os.getcwd(), "", "*.txt", \
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dlg.ShowModal()
        inFile = dlg.GetPath()
        dlg.Destroy()
        if result == wx.ID_OK:  # Save button was pressed
            print "Saving data to", inFile
            np.savetxt(inFile, yyy, fmt='%d')
            self.savebutton.Disable()
            self.saveItem.Enable(False)
        # self.Close(True)
        # self.Destroy()
        elif result == wx.ID_CANCEL:  # Cancel button was pressed
            print "Save data cancelled."

    # -------------------------------------------------------------

    def OnIdle(self, event):
        global xxx, yyy, ychan, tempchan, first, count, temp

        if self.ser.inWaiting() > 0:
            ins = self.ser.read(self.ser.inWaiting())
            data = (self.remains + ins).split()

            if ins[-1] <> "\n":
                self.remains = data.pop()
            else:
                self.remains = ""
            for d in data:

                if first:
                    temp[tempchan] = int(d)
                    first = False
                    tempchan += 1
                else:
                    temp[tempchan] = int(d)
                    yyy[ychan] = temp[tempchan] - temp[tempchan-1]
                    print str(temp[tempchan]) + " - " + str(temp[tempchan-1]) + " = " + str(yyy[ychan])
                    ychan += 1
                    tempchan += 1

            self.draw()
        event.RequestMore(True)

    # -------------------------------------------------------------

    def draw(self):
        global xxx
        self.axis.clear()
        self.axis.set_xlabel('Bounce Number')
        self.axis.set_ylabel('Delta time (s)')
        self.axis.set_xlim(2, 30)
        self.axis.set_xticks(xxx)
        self.axis.grid(color='lightgrey')

        self.axis.set_yticks(np.linspace(0, 1000, 29))
        self.axis.set_ylim(bottom=0, top=1000)

        self.theline = self.axis.plot(xxx, yyy,'bo', color='blue')
        self.figurepanel.draw()
    # ------------------------------------------------------------

    def OnAboutBox(self, event):
        if wx.__version__[0] == '4':
            info = wx.adv.AboutDialogInfo()
        else:
            info = wx.AboutDialogInfo()
        info.SetName('xSpex')
        info.SetVersion('0.9.8', longVersion='0.9 Alpha')
        info.SetDescription('Spex')
        info.AddDeveloper('Thy Doan Mai Le\nMarch, 2019')
        if wx.__version__[0] == '4':
            wx.adv.AboutBox(info)
        else:
            wx.AboutBox(info)
    # --------------------------------------------------------------

    def OnQuit(self, event):
        self.Unbind(wx.EVT_IDLE)
        self.ser.write('s')  # stop Uno data stream
        # print "Quit Event"
        print "Quitting..."
        self.ser.close()
        self.Destroy()

    # -------------------------------------------------------------

    def ConnectToUno(self):
        UnoPID = 0x0043
        noUno = True
        self.unoPort = 'None'
        for pinfo in serial.tools.list_ports.comports():
            if pinfo.pid == UnoPID:
                Device = 'Uno'
                self.unoPort = pinfo.device
                noUno = False
                break
        if noUno:
            wx.MessageBox( \
                'Unable to find an Arduino Uno. Is it connected?', \
                'Error:', wx.OK | wx.ICON_EXCLAMATION)  # ICON_ERROR)
            sys.exit('Error: No Arduino Uno found!')
        while True:
            # try catch block
            try:
                self.ser = serial.Serial(port=self.unoPort, baudrate=250000, \
                                         timeout=2)
                break
            except serial.SerialException:
                print("Waiting for USB port...");
                wx.MessageBox( \
                    'Waiting for USB port...\n' + \
                    'Is the Serial Monitor open on the Arduino app?', \
                    'WARNING:', wx.OK | wx.ICON_NONE)
        self.unoMsg = "Connected to UNO on port: " + self.unoPort
        # self.unoPort = unoPort
        print self.unoMsg

        self.ser.dtr = False
        self.ser.reset_input_buffer()
        self.ClearBuffer()
        self.ser.dtr = True
        ch = self.ser.read(10)[0:3]

        if str(ch) == "BOU":
            print "Uno Bounce program ready..."
        else:
            print
            'Uno Bounce program not found'
            wx.MessageBox('Uno Bounce program not found\n' + \
                          'Reload the program and try ', \
                          'WARNING:', wx.CANCEL | wx.ICON_ERROR)
            sys.exit('Uno Bounce program not found!')

        self.ser.write('s')
    # --------------------------------------------------------------------

    def ClearBuffer(self):
        self.ser.reset_input_buffer()
        # clear the data buffer:
        buf = self.ser.inWaiting()
        ##print buf
        while (buf > 0):
            ch = self.ser.read(buf)
            buf = self.ser.inWaiting()
    # -------------------------------------------------------------------

app = wx.App(False)
w, h = wx.GetDisplaySize()
frame = MainWindow(None, "BOUNCE", (10,25), (0.95*w, 0.85*h))
app.MainLoop()
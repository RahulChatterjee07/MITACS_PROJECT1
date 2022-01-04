# -*- coding: utf-8 -*-
"""
Created on May 29, 2019

@author: Rahul Chatterjee
 
"""
import sys, os, math, serial
from Tkinter import  *
import biopacndt, time, numpy
# import egi.simple as egi


# Parameters

nTrials=50    # 50    With ISI=5s it needs 810s=13.5m
F1=15     # Force at level 1
trialTime=9    # in seconds
dx1=0.5     # distance (normalised to segment1 distance) from segment1
jitterLow=8
jitterHigh=10
restingStatePeriod=6.5 #15.5   # in minutes
gripperDC=0
gripperMedianFWind=0
send2Triggerbox=1

gainX=0.6
period=10   # how often to update the plot

rampWidth=60    # 40
cross=25    # 25
screen_x=16*60
screen_y=9*60
deadtime = 5
fontsize=40


if send2Triggerbox==1:
    ser = serial.Serial('COM5', 19200)
    ser.close()
    ser.open()  # ser.close()
    ser.write('0')
    ser.write('1')

'''
import egi.simple as egi
ms_localtime = egi.ms_localtime
ns = egi.Netstation()
ns.connect('10.10.10.51',55513)
print "Connect to EGI\n"
ns.initialize('10.10.10.51',port?)
ns.BeginSession()
ns.sync()

ns.StartRecording()
print "EGI start recording"
    IN LOOP, ns.sync()
    ns.send_event('evt_',label = "event",timestamp = egi.ms_localtime())
ns.StopRecording()
ns.EndSession()
'''


#-------------- design parameters --------------#
def designPar(self,screen_X,screen_Y,MVC):
    dx=0.1*screen_X*self.screen_x
    dy=0.1*screen_Y*self.screen_y

    DX=(screen_X-2*dx)/5
    x0=dx
    x1=x0+DX
    x2=x1+DX
    x3=x2+DX
    x4=x3+DX
       
    y0=screen_Y-dy    
    y3=(screen_Y-2*dy)/3+dy
    y4=y3  
    y1=y0-(F1/float(F1))*(y0-y3)      
    y2=y1  
    gainY=(5*dy)/(float(F1)*MVC/100)    
   
    maxSamples = (screen_X-2*dx)/gainX
     
    return maxSamples,dx,x0,x1,x2,x3,x4,dy,y0,y1,y2,y3,y4,gainY



#--------------initialize communication with Biopac-------------#
def main():

        acqServer = biopacndt.AcqNdtQuickConnect()
        if not acqServer:
            print "No AcqKnowledge servers found!"
            sys.exit()

        if acqServer.getDataConnectionMethod() != "single":
            acqServer.changeDataConnectionMethod("single")

        calcChannels = acqServer.GetChannels('calc')
        acqServer.Deliver(calcChannels[0], True)
        enabledChannels = [ calcChannels[0] ]
        singleConnectPort = acqServer.getSingleConnectionModePort()
        dataServer = biopacndt.AcqNdtDataServer(singleConnectPort, enabledChannels)
        print " %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
        print
        print "Communication established"
        print
       
        # create the PlotData object for showing our incoming data and
        # add its callback to the AcqNdtDataServer to update the plot

        root = Tk()
        plotData = PlotData(root,acqServer,screen_x,screen_y)
        dataServer.RegisterCallback("UpdatePlot", plotData.handleAcquiredData)

        # The AcqNdtDataServer must be started prior to initiating our data acquisition.
        dataServer.Start()

        # enter the man GUI loop to display our window and wait for it to be closed
        print "The window for the presentation is now open"
        print
        print "Start data acquisition from acqKnowledge and when the subject is ready press the button 'Start task' on the window"
        print
        plotData.runMainWindowLoop()
        root.mainloop

        # stop the AcqNdtDataServer after all of our incoming data has been processed.
#        if send2Triggerbox==1:
#            ser.close()   # terminate communication with COM19 triggerbox
#        dataServer.Stop()
#        print "Communication terminated"
       

               
#----------------plot data and update the screen-------------#        
class PlotData:
    """Class that creates a canvas object with tkinter and plots incoming network data.
    """
   
    def __init__(self,master,server,screen_x,screen_y):

        # store server instance in our attribute
        self.__server = server

        # get our Tk instance.
        self.master = master
        self.master.title("Main window")
        self.frame = Frame(self.master)

        self.secMonit = Toplevel(self.master)
        self.secMonit.title("Secondary window")
        self.secMonitFrame=Frame(self.secMonit)
        self.secMonitFrame.pack(fill=BOTH, expand=Y)
       
        # GUI
        self.__b2 = Button(self.master, text='Start task!')
        self.__b2.grid(row=6)
        self.__b2.config(command=self.startAcquisition)

        self.__b3 = Button(self.master, text='Fullscreen')
        self.__b3.grid(row=0)
        self.__b3.config(command=self.adjustScreen)  
        self.__b4 = Button(self.master, text='Show cross', command=self.showCross).grid(row=1)    
        self.__b41 = Button(self.master, text='Show/hide inner screen', command=self.showHideInnerScreen).grid(row=2)
       
        self.InnerScreenOn = -1
        self.MVC = 1
        self.MVCtxt=StringVar()
        self.zoomOn=-1
        self.gripperDC=gripperDC
        self.gripperMedianFWind=gripperMedianFWind
       
        self.crosstxt=StringVar()
        self.screen_xtxt=StringVar()
        self.screen_ytxt=StringVar()
        self.fontsizetxt=StringVar()
               
#        self.MVCtxt="1"
        self.__e = Entry(self.master, textvariable=self.MVCtxt, justify='center').grid(row=3,column=0)
        self.__b1 = Button(self.master, text='Load MVC (kg)', command=self.loadMVC).grid(row=3,column=1)
        self.__b5 = Button(self.master, text='Get MVC', command=self.getMVC).grid(row=4)    
        self.__b6 = Button(self.master, text='Resting state (6 min)', command=self.restingState).grid(row=5)  
       
       
        self.__e11 = Entry(self.master, textvariable=self.crosstxt, justify='center').grid(row=10,column=0)
        self.__b11 = Button(self.master, text='Cross (25)', command=self.changeCross).grid(row=10,column=1)
        self.__e14 = Entry(self.master, textvariable=self.screen_xtxt, justify='center').grid(row=11,column=0)
        self.__b14 = Button(self.master, text='Screen X (1)', command=self.changescreen_x).grid(row=11,column=1)
        self.__e15 = Entry(self.master, textvariable=self.screen_ytxt, justify='center').grid(row=12,column=0)
        self.__b15 = Button(self.master, text='Screen Y (1)', command=self.changescreen_y).grid(row=12,column=1)
        self.__e17 = Entry(self.master, textvariable=self.fontsizetxt, justify='center').grid(row=13,column=0)
        self.__b17 = Button(self.master, text='Font size (40)', command=self.changefontsize).grid(row=13,column=1)
       
        self.cross=cross
        self.screen_x=1
        self.screen_y=1
        self.deadtime=deadtime
        self.fontsize=fontsize
       
       
        # create the canvas to use for drawing the data that has been received
#        self.__cMain = Canvas(self.master, width=300, height=200, bg='black')
#        self.__cMain.grid(row=50)
        self.__cSec = ResizingCanvas(self.secMonitFrame, width=screen_x, height=screen_y, bg='black',highlightthickness=0)
        self.__cSec.pack(fill=BOTH, expand=Y)
       
       
        # trigger the canvas to update the plot every x milliseconds
        # to show any incoming data that has been received
       
       
        self.__newTrial=0
        self.__trial = 0
        self.__cSec.after(0, self.updatePlot)
        self.__chanData = []
        self.__taskOn = 0        
        self.time0 = 0  
        self.text1=StringVar()
        self.text2=StringVar()
        self.text3=StringVar()
        self.text4=StringVar()
        self.text5=StringVar()

       
        self.w1 = Label(self.master, textvariable=self.text1).grid(row=15)
        self.w2 = Label(self.master, textvariable=self.text2).grid(row=16)
        self.w3 = Label(self.master, textvariable=self.text3).grid(row=17)
        self.w4 = Label(self.master, textvariable=self.text4).grid(row=18)
        self.w5 = Label(self.master, textvariable=self.text4).grid(row=19)
       
       
    def showCross(self):
        self.__taskOn = 0
        self.__server.insertGlobalEvent('Show cross_b', 'def12', '')
        if send2Triggerbox==1:    
            ser.write('0')
            ser.write('1')
       
    def showHideInnerScreen(self):
        self.InnerScreenOn = self.InnerScreenOn*(-1)
         
    def changeCross(self):
        self.cross=float(self.crosstxt.get())
       
    def changescreen_x(self):
        self.screen_x=float(self.screen_xtxt.get())
       
    def changescreen_y(self):
        self.screen_y=float(self.screen_ytxt.get())
       
    def changefontsize(self):
        self.fontsize=int(self.fontsizetxt.get())
       
    def loadMVC(self):
        self.MVC=float(self.MVCtxt.get())
       
    def getMVC(self):
        self.__taskOn = 11
        self.getMVCfirst = 1
        self.__server.insertGlobalEvent('Get MVC', 'def8', '')  
        if send2Triggerbox==0:    
            ser = serial.Serial('COM5', 19200)
            ser.write('0')
            ser.write('a')
           
    def restingState(self):
        self.__taskOn = 12
        self.restingStatefirst = 1        

    def adjustScreen(self):
        if self.zoomOn==-1:
            self.zoomOn=1
            self.secMonit.state('zoomed')
            self.secMonit.overrideredirect(1)
            screenW=self.secMonit.winfo_screenwidth()
            screenH=self.secMonit.winfo_screenheight()
            self.secMonit.config(width=screenW, height=screenH, bg='black')
            self.__cSec.delete(ALL)
        else:
            self.zoomOn=-1
            self.secMonit.state('normal')
            self.secMonit.overrideredirect(0)            
            self.__cSec.delete(ALL)    
            screenW=0.5*self.secMonit.winfo_screenwidth()
            screenH=0.5*self.secMonit.winfo_screenheight()
            # self.secMonit.config(width=screenW, height=screenH, bg='black')
       
       
    def handleAcquiredData(self, index, frame, channelsInSlice):
        # append the channel data to the end of our list of received data.
        self.__chanData.append(frame[0])  
       
    def runMainWindowLoop(self):
        """ Enters the main window loop to display data.
        """
        self.master.mainloop()

    def startAcquisition(self):

        self.__chanData = []
#        self.__b2.config(state=DISABLED)
        self.__taskOn = 1
        self.__trial = 0
        self.__flagX2=0
        self.__flagX3=0
        self.__newTrial=1        
       
        self.__time1=0
        self.timeJit=0      
        self.time0=time.time()
        #self.__server.insertGlobalEvent('Beginning of Session', 'def1', '')
        if send2Triggerbox==1:
            ser.write('0')
            ser.write('b')

           
                       
#---------------- update plots -------------#                                                
    def updatePlot(self):
        """Redraw the canvas area of the window to reflect the latest data
        received from AcqKnowledge.
        """

        # erase the existing plot in the canvas
     
        self.text1.set("MVC: %.1f kg " % ((self.MVC)))          
        self.text2.set("15%% of MVC: %.1f kg" % ((self.MVC*0.15)))
        if len(self.__chanData) > 1:

            x1 = max(0,len(self.__chanData)-1-int(self.gripperMedianFWind))
            x2 = len(self.__chanData)              
            gripperValue = numpy.median(self.__chanData[x1:x2]) - self.gripperDC
                                         
        else:
            gripperValue=0
        self.text3.set("Gripper: %.1f kg " % (gripperValue))      
        self.text4.set("Trial: %i/%i" % (self.__trial,nTrials))
       
        self.__cSec.delete(ALL)

        screenW = self.secMonitFrame.winfo_reqwidth()
        screenH = self.secMonitFrame.winfo_reqheight()
       
        if screenW*9/16 > screenH:
            screenW=screenH*16/9
        else:
            screenH=screenW*9/16    
               
        screen_x = round(screenW)
        screen_y = round(screenH)    
       
           
       
        # -------------- draw paradigm --------------- #
        maxSamples,dx,x0,x1,x2,x3,x4,dy,y0,y1,y2,y3,y4,gainY=designPar(self,screen_x,screen_y,self.MVC)  
       
        if self.InnerScreenOn > 0:
            self.__cSec.create_rectangle(dx,dy,screen_x-dx,screen_y-dy,outline='yellow')

        cross = self.cross
        fontsize = self.fontsize            
       
        if len(self.__chanData) > 1 and self.__taskOn == 0:                        
            self.__cSec.delete(ALL)
            self.__cSec.create_line((screen_x/2),(screen_y/2)+cross,(screen_x/2),(screen_y/2)-cross, fill='white',width=cross/2)  
            self.__cSec.create_line((screen_x/2)+cross,(screen_y/2),(screen_x/2)-cross,(screen_y/2), fill='white',width=cross/2)
           
            if self.InnerScreenOn > 0:
                self.__cSec.create_rectangle(dx,dy,screen_x-dx,screen_y-dy,outline='yellow')
               
               
               
               
        if len(self.__chanData) > 1 and self.__taskOn == 1:        
            if  time.time() - self.time0 <self.deadtime:
                self.__cSec.create_text(screen_x/2, screen_y/2, fill="white", text="Squeeze to reach the red targe bar.\nBe ready to start in seconds.", font=("Helvetica", fontsize))
            else:  
                if self.__newTrial==1:
                    self.__newTrial = 2
                    self.__trial = self.__trial + 1
                   
                    self.__time1=time.time()
                    self.timeJit=numpy.random.uniform(jitterLow, jitterHigh)
               
                if self.__trial <= nTrials:
                    if self.__newTrial == 2:
                        self.__server.insertGlobalEvent('Begin task', 'def3', '')                        
                        if send2Triggerbox==1:
                             ser.write('0')
                             ser.write('c')
                        grip=self.__chanData[len(self.__chanData)-1]    
                        k = 6                    
                        y = y0 - grip * gainY
                        self.__cSec.create_rectangle(screen_x/2-dx,y0-k*dy,screen_x/2+dx,y0,outline='white',fill='white') # largest box                        
                        self.__cSec.create_rectangle(screen_x/2-dx,y,screen_x/2+dx,y0,outline='yellow',fill='yellow') # the moving box
                        self.__cSec.create_line(screen_x/2-dx,y0-5*dy,screen_x/2+dx,y0-5*dy, fill='red',width=5) # leave some space for over-squeeze
                        # how long to squeeze
                        if (time.time()-self.__time1) >= 5:
                            self.__newTrial = 3
                            self.__time1=time.time()
                           
                    if self.__newTrial == 3:
                        self.__cSec.delete(ALL)
                        #self.__server.insertGlobalEvent('Show cross_b', 'def12', '')
                        self.__cSec.create_line((screen_x/2),(screen_y/2)+cross,(screen_x/2),(screen_y/2)-cross, fill='white',width=cross/2)  
                        self.__cSec.create_line((screen_x/2)+cross,(screen_y/2),(screen_x/2)-cross,(screen_y/2), fill='white',width=cross/2)
                        if   (time.time()-self.__time1)>=self.timeJit:  
                            self.__newTrial=1
                           
                else:
                    print
                    print "End of task"
                    print "You can now close the window"
                    self.__cSec.create_text(screen_x/2, screen_y/2, fill="white", text="Thank you!", font=("Helvetica", fontsize))
                    self.__taskOn = 2
                    self.__server.insertGlobalEvent('End of session', 'def7', '')  
                    if send2Triggerbox==0:
                        ser.write('0')
                        ser.write('h')
                   
                             
        if self.__taskOn == 2:
            self.__cSec.create_text(screen_x/2, screen_y/2, fill="white", text="Thank you!", font=("Helvetica", fontsize))
           
        if self.__taskOn == 11:
            if  self.getMVCfirst == 1:
                self.getMVCfirst = 0
                self.time1=time.time()
                self.maxValue=1    
               
       
            if  (time.time()-self.time1)<4:                
                self.__cSec.create_text(screen_x/2, screen_y/7, fill="white", text="Be ready to squeeze as hard as possible", font=("Helvetica", fontsize))                
                grip=self.__chanData[len(self.__chanData)-1]
               
            elif  (time.time()-self.time1)<12:                
                self.__cSec.create_text(screen_x/2, screen_y/7, fill="white", text="Squeeze!", font=("Helvetica", fontsize))                
                grip=self.__chanData[len(self.__chanData)-1]
                                     
                k=6                    
                y = y0 - (grip/60)*(k*dy)
                self.__cSec.create_rectangle(screen_x/2-dx,y0-k*dy,screen_x/2+dx,y0,outline='blue',fill='blue')
                self.__cSec.create_rectangle(screen_x/2-dx,y,screen_x/2+dx,y0,outline='green',fill='green')                    
                self.__cSec.create_rectangle(screen_x/2-dx,y0-(self.MVC/60)*(k*dy),screen_x/2+dx,y0,outline='red',width='3')  

                self.maxValue=max(self.maxValue,grip)
                self.MVC=self.maxValue
               
            else:                
                self.__cSec.create_text(screen_x/2, screen_y/2, fill="white", text="Thank you!", font=("Helvetica", fontsize))  
           
           
        if self.__taskOn == 12:
            if  self.restingStatefirst == 1:
                self.restingStatefirst = 0
                self.time1=time.time()
                self.__server.insertGlobalEvent('Resting-State On', 'def9', '')  
                if send2Triggerbox==1:
                    ser.write('0')
                    ser.write('12')
                             
            if  (time.time()-self.time1)<restingStatePeriod*60:
               
                self.__cSec.delete(ALL)
                self.__cSec.create_line((screen_x/2),(screen_y/2)+cross,(screen_x/2),(screen_y/2)-cross, fill='white',width=cross/2)  
                self.__cSec.create_line((screen_x/2)+cross,(screen_y/2),(screen_x/2)-cross,(screen_y/2), fill='white',width=cross/2)
                timeR=restingStatePeriod*60-(time.time()-self.time1)
                timeRmin=math.floor(timeR/60)
                timeRsec=timeR-timeRmin*60
               
                self.text5.set("Time remaining: %i:%i" % (timeRmin,timeRsec))                  
               
               
            else:                
                self.__cSec.create_text(screen_x/2, screen_y/2, fill="white", text="Thank you!", font=("Helvetica", fontsize))
                self.__server.insertGlobalEvent('Resting-State Off', 'def10', '')
                if send2Triggerbox==1:
                    ser.write('0')
                    ser.write('13')            


        self.__cSec.addtag_all("all")
        self.__cSec.after(period, self.updatePlot)  
       

  # a subclass of Canvas for dealing with resizing of windows
class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)
       


if __name__ == '__main__':
    main()
           
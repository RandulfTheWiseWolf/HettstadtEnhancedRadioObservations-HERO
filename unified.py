import control
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import Frame
from tkinter import filedialog as fd 

from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import time
import guiHelp as gh
import coord_helper
import spec


###Connect to the ACU
control.connect('/dev/ttyUSB0')

###Connect to the spectrograph
osci = spec.DSA815()
osci.conn()
print(osci.inst.ask(":SYST:ERR?"))

class TelescopeDrive(tk.Tk):

    def __init__(self):
        
        #Tracking parameters
        self.tracking = {"start_pos": (0, 0),
                        "start_time": 0,
                        "delay": 0,
                        "deltaT": 0,
                        "last_updated": 0,
                        "running": False}
        
        #Flag to check if telescope is tracking
        self.tracking_flag = False
        #Flag to check if track option is on
        self.flag_dummy = False
        #Flag to check if telescope is measuring
        self.measure_abort_flag = True
        #Last position for measurement file
        self.last_position=[0,0]
        #Current file for the schedule items
        self.current_file=''
        #Start with preamp on
        osci.preamp_on()
        #Pandas DataFrame for plots
        self.dataFrame = []
        
        #Default Measurement Settings (centerFreq, span, videobandwidth, resolutionbandwidth, sweeptime)
        self.settings=[["1420000000",1420000000],["100000000",100000000],["1000000",1000000],["1000000",1000000],["1",1]]
        #Spectrograph ranges (centerFreq, span, videobandwidth, resolutionbandwidth, sweeptime)
        self.specLimits=[[0,7500000000],[0,7500000000],[1,3000000],[10,1000000],[0.3,1500]]

        ###Window
        super().__init__()
        self.geometry("{}x{}".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        self.title("HERO")
        
        ###Lines
        #Vertical
        tk.ttk.Separator(self, orient="vertical").place(x=self.winfo_screenwidth()*0.32, y=0, relheight=1)
        
        #Horizontal
        tk.ttk.Separator(self).place(relx=0.339, rely=0.23, relwidth=1)
        tk.ttk.Separator(self).place(relx=0.339, rely=0.48, relwidth=1)
        tk.ttk.Separator(self).place(relx=0, rely=0.6, relwidth=0.339)
        tk.ttk.Separator(self).place(relx=0, rely=0.88, relwidth=0.339)
        
        ###Coordinate Section
        tk.Label(self, text="Coordinates", font=("Verdana", 20)).place(relx=0.1, rely=0.035)
        tk.Label(self, text="Choose Coordinates", font=("", 12)).place(relx=0.017, rely=0.1)
        
        #Dropdown menu for equatorial and azimuthal system
        self.var = tk.StringVar(self)
        self.var.set("Azimuthal System")
        menu = tk.OptionMenu(self, self.var, "Equatorial System", "Azimuthal System", command=self.coordSystemAnimation)
        menu.place(relx=0.18, rely=0.095)
        
        #Infoicon for input help
        photo = tk.PhotoImage(master = self, file = r"/home/natlab2/Schreibtisch/HERO/Raoul/info_icon.png")
        tk.Button(self, image=photo, borderwidth=0, command=self.popCoordinateMessage).place(relx=0.12, rely=0.193)
        
        #Az, El inputs
        self.coord1 = tk.Label(self, text="Azimuth [°]", font=("", 12))
        self.coord1.place(relx=0.02, rely=0.15)
        
        self.enterCoord1 = tk.Entry(self)
        self.enterCoord1.place(relx=0.18, rely=0.15)
        
        self.coord2 = tk.Label(self, text="Elevation [°]", font=("", 12))
        self.coord2.place(relx=0.02, rely=0.19)
        
        self.enterCoord2 = tk.Entry(self)
        self.enterCoord2.place(relx=0.18, rely=0.19)
        
        #Buttons for driving
        tk.Button(self, text='Go', command=self.go).place(relx=0.1, rely=0.24)
        tk.Button(self, text='Stop Driving', command=self.stopdriving).place(relx=0.15, rely=0.24)
        tk.Button(self, text='Park', command=control.park).place(relx=0.02, rely=0.24)
        
        #Tracking checkbox
        self.trackBox = tk.Checkbutton(self, text="Track", font=("", 12), command=self.__change_tracking)
        self.trackBox.place(relx=0.26, rely=0.2425)
        
        #Crossscan
        tk.Label(self, text="Range [°]", font=("", 12)).place(relx=0.02, rely=0.31)
        self.enterRange = tk.Entry(self)
        self.enterRange.place(relx=0.15, rely=0.31)
    
        tk.Button(self, text='Cross Scan', command=self.crossScan).place(relx=0.02, rely=0.35)
        
        #Display current status of the Cross-Scan
        crossFrame = Frame(self, highlightthickness=2, width=2, height=1, bd= 0)
        crossFrame.place(relx=0.15, rely=0.352)
        
        self.crossLabel = tk.Label(crossFrame, text="", font=("", 11))
        self.crossLabel.pack()
        
        
        #N-Point-Scan
        tk.Label(self, text="Gridsize", font=("", 12)).place(relx=0.02, rely=0.41)
        self.enterGrid = tk.Entry(self)
        self.enterGrid.place(relx=0.15, rely=0.41)
        
        tk.Label(self, text="Cellsize [°]", font=("", 12)).place(relx=0.02, rely=0.45)
        self.enterDistance = tk.Entry(self)
        self.enterDistance.place(relx=0.15, rely=0.45)
        
        tk.Label(self, text="Duration [s]", font=("", 12)).place(relx=0.02, rely=0.49)
        self.enterDuration = tk.Entry(self)
        self.enterDuration.place(relx=0.15, rely=0.49)
        
        tk.Button(self, text='N-Point-Scan', command=self.nPointScan).place(relx=0.02, rely=0.53)
        
        #Display current status of the N-Point-Scan
        npointFrame = Frame(self, highlightthickness=2, width=2, height=1, bd= 0)
        npointFrame.place(relx=0.15, rely=0.535)
        
        self.npointLabel = tk.Label(npointFrame, text="", font=("", 11))
        self.npointLabel.pack()
        
        ###Spectrograph section
        tk.Label(self, text="Spectrograph", font=("Verdana", 20)).place(relx=0.58, rely=0.035)
        
        #Setting inputs
        tk.Label(self, text="Center Frequency", font=("", 12)).place(relx=0.35, rely=0.085)
        self.enterCenter = gh.tEntry(self, std_text = "1420000000")
        self.enterCenter.place(relx=0.35, rely=0.115)
        
        tk.Label(self, text="Span", font=("", 12)).place(relx=0.35, rely=0.145)
        self.enterSpan = gh.tEntry(self, std_text = "100000000")
        self.enterSpan.place(relx=0.35, rely=0.175)
        
        tk.Label(self, text="RBW", font=("", 12)).place(relx=0.52, rely=0.085)
        self.enterRBW = gh.tEntry(self, std_text = "1000000")
        self.enterRBW.place(relx=0.52, rely=0.115)
        
        tk.Label(self, text="VBW", font=("", 12)).place(relx=0.52, rely=0.145)
        self.enterVBW = gh.tEntry(self, std_text = "1000000")
        self.enterVBW.place(relx=0.52, rely=0.175)
        
        tk.Label(self, text="Sweeptime", font=("", 12)).place(relx=0.69, rely=0.085)
        self.enterSweep = gh.tEntry(self, std_text = "1")
        self.enterSweep.place(relx=0.69, rely=0.115)
        
        self.preamp = tk.Button(self, text='Preamp On', bg="#99ff33",command=self.preampAnimation)
        self.preamp.place(relx=0.69, rely=0.17)
        
        #Buttons 
        tk.Button(self, text='Apply', command=self.apply).place(relx=0.9, rely=0.11)
        tk.Button(self, text='Measure', command=self.measure).place(relx=0.85, rely=0.17)
        tk.Button(self, text='Stop', bg="#ff5555", command=self.abrt).place(relx=0.93, rely=0.17)
        
        ###Current position frame
        posFrame = Frame(self, highlightthickness=2, width=150, height=50, bd= 0)
        posFrame.place(relx=0.075, rely=0.63)
        
        tk.Label(posFrame, text="Current position", font=("", 20)).pack()
        
        #Dynamic Az label for current position inside the frame
        self.dynamicAz = tk.Label(posFrame, text="", font=("", 15))
        self.dynamicAz.pack()
        
        
        #Dynamic El label for current position inside the frame
        self.dynamicEl = tk.Label(posFrame, text="", font=("", 15))
        self.dynamicEl.pack()
        
        ###Status frame
        labelFrame = Frame(self, highlightthickness=2, width=150, height=50, bd= 0)
        labelFrame.place(relx=0.1, rely=0.75)
        
        tk.Label(labelFrame, text="Status", font=("", 20)).pack()
        
        #Dynamic driving label for current position inside the frame
        self.dynamicDriving = tk.Label(labelFrame, text="", font=("", 15))
        self.dynamicDriving.pack()
        
        
        #Dynamic measuring label for current position inside the frame
        self.dynamicMeasuring = tk.Label(labelFrame, text="", font=("", 15))
        self.dynamicMeasuring.pack()
        
        ####Spectrum frame
        #Plot buttons
        tk.Button(self, text='Plot', command=lambda: self.chooseFile(False)).place(relx=0.94, rely=0.5)
        tk.Button(self, text='Plot Mean', command=lambda: self.chooseFile(True)).place(relx=0.853, rely=0.5)
        
        #Set up plot and plot window
        self.figure = plt.Figure(figsize=(7.5,4), dpi=100)        
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel('Frequency [Hz]')
        self.axes.set_ylabel('Amplitude [dBm]')
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().configure(highlightthickness=2)
        self.canvas.get_tk_widget().place(relx=0.36, rely=0.55)
        
        ###Plotting
        #Frame for the sweep index (plot the n-th data row)
        indexFrame = Frame(self, highlightthickness=2, width=150, height=50, bd= 0)
        indexFrame.place(relx=0.45, rely=0.502)
        
        self.indexLabel = tk.Label(indexFrame, text="0", font=("", 12))
        self.indexLabel.pack()
        
        tk.Label(self, text="Sweep index", font=("", 12)).place(relx=0.35, rely=0.504)
        
        #Buttons to change the sweep index
        tk.Button(self, text='+1', command = lambda: self.changeIndexAndPlot(1)).place(relx=0.65, rely=0.5)
        tk.Button(self, text='-1', command = lambda: self.changeIndexAndPlot(-1)).place(relx=0.53, rely=0.5)
        tk.Button(self, text='+10', command = lambda: self.changeIndexAndPlot(10)).place(relx=0.7, rely=0.5)
        tk.Button(self, text='-10', command = lambda: self.changeIndexAndPlot(-10)).place(relx=0.48, rely=0.5)
        tk.Button(self, text='Reset', command = self.resetIndex).place(relx=0.58, rely=0.5)
        
        
        ###Schedule 
        tk.Label(self, text="Observation Schedule", font=("Verdana", 20)).place(relx=0.53, rely=0.245)
        
        #Create Schedule input fields
        tk.Label(self, text="Right Ascension", font=("", 12)).place(relx=0.35, rely=0.29)
        self.enterrasched = gh.tEntry(self, std_text = "")
        self.enterrasched.place(relx=0.35, rely=0.32)
        
        tk.Label(self, text="Declination", font=("", 12)).place(relx=0.35, rely=0.35)
        self.enterdecsched = gh.tEntry(self, std_text = "")
        self.enterdecsched.place(relx=0.35, rely=0.38)
        
        tk.Label(self, text="Duration (s)", font=("", 12)).place(relx=0.52, rely=0.29)
        self.enterdursched = gh.tEntry(self, std_text = "")
        self.enterdursched.place(relx=0.52, rely=0.32)
        
        tk.Label(self, text="Name (optional)", font=("", 12)).place(relx=0.52, rely=0.35)
        self.enternamesched = gh.tEntry(self, std_text = "")
        self.enternamesched.place(relx=0.52, rely=0.38)
        
        #Tracking checkbox
        self.track_entry=tk.IntVar()
        self.trackBoxsched = tk.Checkbutton(self, text="Tracking", font=("", 12), variable=self.track_entry)
        self.trackBoxsched.place(relx=0.68, rely=0.32)
        
        #Measure while tracking checkbox
        self.mwtrack_entry=tk.IntVar()
        self.mwtrackBoxsched = tk.Checkbutton(self, text="Measure while tracking", font=("", 12), variable=self.mwtrack_entry)
        self.mwtrackBoxsched.place(relx=0.78, rely=0.32)
        
        
        #Buttons the carry out/create or add an object to a schedule 
        tk.Button(self, text='Load Schedule', command = self.schedule).place(relx=0.86, rely=0.43)
        tk.Button(self, text='Create Schedule', command = self.createschedule).place(relx=0.69, rely=0.43)
        tk.Button(self, text='Add object', command = self.add_item).place(relx=0.69, rely=0.375)
        
        #How fast should be tracked during a schedule measurement
        self.trackperiod = tk.Label(self, text="Trackperiod [s]", font=("", 12))
        self.trackperiod.place(relx=0.35, rely=0.435)
        
        self.entertrackperiod = gh.tEntry(self, std_text = "5")
        self.entertrackperiod.place(relx=0.485, rely=0.435)
        
        #Display current status of the schedule measurement
        scheduleFrame = Frame(self, highlightthickness=2, width=2, height=1, bd= 0)
        scheduleFrame.place(relx=0.815, rely=0.375)
        
        self.scheduleLabel = tk.Label(scheduleFrame, text="", font=("", 11))
        self.scheduleLabel.pack()
        
        ###Other stuff
        #Data cleaning button, to remove oversampled measurements
        tk.Button(self, text='Clean Data', command=self.cleanse).place(relx=0.76, rely=0.5)
        #Wuit button
        tk.Button(self, text='Quit', command=self.__close).place(relx=0.15, rely=0.94)
        
        
        self.alternative_positioning()
        self.mainloop()


        
#####ANIMATION AND INFORMATION SECTION

    
    ###Change the colour of the preamp button
    def preampAnimation(self):
        if self.preamp.config('text')[-1] == 'Preamp On':
            self.preamp.config(text='Preamp Off')
            self.preamp.config(bg="#ff5555")
            
        else:
            self.preamp.config(text='Preamp On')
            self.preamp.config(bg = "#99ff33")
    
    
    ###Change the coordinate labels coord1 and coord2 depending on the choice
    ###in the dropdown menu           
    def coordSystemAnimation(self, coordSystem):
        if self.var.get() == "Equatorial System":
            self.coord1["text"] = "Right Ascencion"
            self.coord2["text"] = "Declination"
            
        else: 
            self.coord1["text"] = "Azimuth [°]"
            self.coord2["text"] = "Elevation [°]"
    
    
    ###Connected to the infoicon: specifies coordinate inputs
    def popCoordinateMessage(self):
        message = """1. Azimuthal System: Altitude and Azimuth in [°] \n\n2. Equatorial System: Several options are possible. The most common formats are [° m s] and [h m s]. \n\nExamples: 140d4m2s or 50h5m3s, respectively. \n\nIf no unit is specified, degrees will be assumed.\n\nRefer to the AstroPy documentation for further information:\nhttps://docs.astropy.org/en/stable/api/astropy.coordinates.Angle.html"""
        tk.messagebox.showinfo("Expected coordinate inputs", message)
    
    
    
#####SPECTROGRAPH SECTION

      
    ###Send the settings of the spectrograph
    def apply(self):
        centerFreq = self.enterCenter.get()
        span = self.enterSpan.get()
        vbw = self.enterVBW.get()
        rbw = self.enterRBW.get()
        sweeptime = self.enterSweep.get()
        
        if self.preamp.config('text')[-1] == 'Preamp On':
            osci.preamp_on()
        else:
            osci.preamp_off()
        
        #Check if inputs are valid floats
        Entries=[centerFreq,span,rbw,vbw,sweeptime]
        counter=0
        
        for setting in self.settings:
            if Entries[counter] == setting[0]:
                Entries[counter] = setting[1]
            else:
                try:
                     Entries[counter] = float(Entries[counter])
                except ValueError:
                     tk.messagebox.showinfo("Warning", "Please enter valid parameters.")
                     return
            counter+=1
        
        #Check if inputs are in the allowed domain of the spectrograph
        for i in range(len(self.specLimits)):
            if self.specLimits[i][0] <= Entries[i] <= self.specLimits[i][1]:
                pass
            else:
                tk.messagebox.showinfo("Warning", "Input parameters not in allowed domain of the spectrograph.")

                
        
        #The actual setting of the values
        osci.set_centerfreq(Entries[0])
        osci.set_span(Entries[1])
        osci.set_rbw(Entries[2])
        osci.set_vbw(Entries[3])
        osci.set_sweeptime(Entries[4])
        
        #Display the settings of the spectrograph
        #centerfreq, span, rbw, vbw, sweep, preamp = osci.getsettings()
        
        #tk.messagebox.showinfo("Info", str(centerfreq) + " " + str(span) + " " + str(rbw) + " " + str(vbw) + " " + str(sweep) + " " + str(preamp))

    
    

#####DRIVING AND TRACKING SECTION


    ###Drive to input coordinates
    def go(self):
        coord1 = self.enterCoord1.get()
        coord2 = self.enterCoord2.get()
        
        #Check the system and if the inputs are valid, if yes: get Az, El
        try:
            az, el = self.checkSystem(coord1, coord2)
        
        except:
            return
        
        #Check if limits fit
        try: 
            control.checkLimits(az, el)
        
        except ValueError:
            tk.messagebox.showinfo("Warning", "Coordinates out of bounds. \n 42 < Az < 322 \n 22 < El < 90")
                
            return
        
        #Check if tracking is selected
        else: 
            #Set up start parameters
            if self.flag_dummy:
                self.tracking["start_pos"] = (az, el)
                self.tracking["delay"] = 20
                self.tracking["running"] = False
                self.tracking["last_updated"] = time.time()
                self.tracking_flag = True
                
            else:
                self.tracking["running"] = False
                self.tracking_flag = False
            
            #small time.sleep() needed that the ACU can receive command
            control.drive(az, el)
            time.sleep(0.1)
            
            
    ###Stop driving and set the tracking flag to false        
    def stopdriving(self):
        self.trackBox.deselect()
        control.stop()
    
    
    ###Change the tracking dummy if tracking checkbox is activated
    def __change_tracking(self):
        self.flag_dummy = not self.flag_dummy
    
         
    ###Calculate the new coordinates and drive there
    def track(self, az, el):
        az, el = coord_helper.calculate_new_coordinates(self.tracking["start_pos"], 
                                                   self.tracking["start_time"])
        control.drive(az, el)
        
        
         
#####INPUT CHECK SECTION
    
    
    ###Check if an arbitrary number of inputs can be made to floats
    @staticmethod
    def checkNumericalInput(*args):
        output=[]
        
        for i in range(len(args)):
            try:   
                output.append(float(args[i]))
                
            except ValueError:
                tk.messagebox.showinfo("Warning", f"Invalid Input: {args[i]}")
        
        return output
        
    
    ###Check if Ra, Dec inputs can be converted to an astropy Angle object
    def isAngle(self, ra, dec):
        #Make strings for astropy.Angle
        ra = str(ra)
        dec = str(dec)

        try:
            ra = coord_helper.Angle(ra)
            dec = coord_helper.Angle(dec)
            
        except ValueError:
            tk.messagebox.showinfo("Warning", "Invalid Angle Format")
            
            return
        
        #Handle inputs without units for each coordinate
        except coord_helper.u.core.UnitsError:
            #Default input is degree
            try:
                ra=coord_helper.Angle(ra + "d")
            
            #Weird try except for debugging errors, but should work
            except:
                try:
                    ra = coord_helper.Angle(ra)
                    
                except ValueError:    
                    tk.messagebox.showinfo("Warning", "Invalid RA Format")
                    return
            
            #Default input is degree
            try:
                dec=coord_helper.Angle(dec + "d")
            
            #Weird try except for debugging errors, but should work
            except:
                try:
                    dec = coord_helper.Angle(dec)
                    
                except ValueError:    
                    tk.messagebox.showinfo("Warning", "Invalid DEC Format")
                    return
        
        #Convert Ra, Dec to Az, El to work with it
        az, el = coord_helper.convertEqToAz(ra, dec)
          
        return az, el 
    
    
    ###Check if equatoral or azimuthal system was chosen
    def checkSystem(self, coord1, coord2):
        if self.var.get() == "Equatorial System":
            ra = coord1
            dec = coord2
            
            #Check if input is valid and transform to Az, El
            try:
                az, el = self.isAngle(ra, dec)
            
            #Just return since isAngle makes the messagebox
            except:
                return
            
            return az, el
            
        else:
            az = coord1
            el = coord2
            
            #Check if input is valid
            try:
                az, el = self.checkNumericalInput(az, el)
                
            #Just return since checkNumericalInput makes the messagebox
            except:
                return
            
            return az, el
    
    

#####QUERY STATUS SECTION

            
    ###Overall ACU status query for labels, flags, etc    
    def alternative_positioning(self):
        #Get status
        az, el, status = control.readdata()
        #Overwrite last_position
        self.last_position=[az,el]
        
        #Check status variable where driving details are hidden (see bottom 
        #for details) and change driving labels
        if status == "@P@" or status == "@@@":
            control.driving_flag = False
            self.dynamicDriving["text"] = "Standing" 
            
        else:
            control.driving_flag = True
            self.dynamicDriving["text"] = "Driving"
        
        #Check if measuring and change labels
        if self.measure_abort_flag == False:
            self.dynamicMeasuring["text"] = "Measuring"
            
        if self.measure_abort_flag == True:
            self.dynamicMeasuring["text"] = "Not measuring"
        
        #Check if correction of actual position is needed (only in tracking)
        #Needed if current position differs from old one by a certain range
        if self.tracking_flag and not self.tracking["running"] and\
        self.tracking["start_pos"][0] - 0.5 <= az <= self.tracking["start_pos"][0] + 0.5 and \
        self.tracking["start_pos"][1] - 0.5 <= el <= self.tracking["start_pos"][1] + 0.5 \
        and self.flag_dummy:
            self.tracking["start_time"] = coord_helper.Time.now()
            self.tracking["running"] = True
        
        #If running is True (see above) then correct the position (with short delay) 
        elif self.tracking["running"] and self.flag_dummy and\
        self.tracking["last_updated"] + self.tracking["delay"] <= time.time():
            self.tracking["last_updated"] += self.tracking["delay"]
            self.track(az, el)
        
        #Update the current position labels
        self.dynamicAz["text"] = "Az: " + str(az)
        self.dynamicEl["text"] = "El: " + str(el)
        
        #Always execute this function
        self.after(500, self.alternative_positioning)
    
    
    ###Smaller alternativ_positioning
    #new function needed because if cross/npoint: alternative_positioning blocked
    #and it gives more information than needed
    def checkDriving(self):
            #Az, El are not needed here but control.readdata() returns az, el, status
            az, el, status = control.readdata()
            
            self.last_position=[az,el]
            
            #Update the current position labels
            self.dynamicAz["text"] = "Az: " + str(az)
            self.dynamicEl["text"] = "El: " + str(el)
            
            #Same as altpos
            if status == "@P@" or status == "@@@":
                control.driving_flag = False
                self.dynamicDriving["text"] = "Stopped"
                
            else:
                control.driving_flag = True
                self.dynamicDriving["text"] = "Driving"
            
            if self.measure_abort_flag == False:
                self.dynamicMeasuring["text"] = "Measuring"
                
            if self.measure_abort_flag == True:
                self.dynamicMeasuring["text"] = "Not Measuring"
            
            #self.update() makes GUI interaction possible
            self.update()
            
            
            
#####SCAN SECTION
       

    ###CrossScan
    def crossScan(self):
        coord1 = self.enterCoord1.get()
        coord2 = self.enterCoord2.get()
        #Range of the scan
        size = self.enterRange.get() 
        
        #Check if inputs are valid
        try:
            az, el = self.checkSystem(coord1, coord2)
            #[0] since checkNumericalInput returns a list
            size = self.checkNumericalInput(size)[0] 
        
        except:
            return
        
        #Check if limits fit
        try: 
            control.checkLimits(az, el, size)
        
        except ValueError:
            tk.messagebox.showinfo("Warning", "Coordinates out of bounds. \n 42 < Az < 322 \n 22 < El < 90")
            
            return
        
        #Choose file to write data
        filename = self.fileDialog()
        
        #Set up starting parameters for tracking
        startTime = coord_helper.Time.now()
        startPos = (az, el)
        
        #Calculate equatorial coordinates for file
        ra, dec = coord_helper.convertAzToEq(az, el, startTime)
        
        newTime = startTime
        newPos = startPos
        
        #Go to the top of the cross
        #    o
        #    .
        #. . . . .
        #    .
        #    .
        control.drive(az, el + size)
        time.sleep(0.1)
        
        #Keep the program busy until it has reached the top position
        while control.driving_flag == True:
            self.after(500,self.checkDriving())
            
            self.crossLabel["text"] = "Going to top position"
        
        #Check if tracking was selected and calculate new position 
        if self.flag_dummy:
            az, el = coord_helper.calculate_new_coordinates(startPos, startTime)
            az = float(az)
            el = float(el)
        
            #If the position differs overwrite newPos and newTime and 
            #drive to corrected position; repeat until no difference
            while not newPos[0] - 0.1 < az < newPos[0] + 0.1 or not newPos[1] - 0.1 < el < newPos[1] + 0.1:
                    
                newPos = (az, el)
                newTime = coord_helper.Time.now()
                
                control.drive(az, el + size)
                time.sleep(0.1)
            
                #Keep the program busy until it has reached the top position
                while control.driving_flag == True:
                    self.after(500,self.checkDriving())
                
                    self.crossLabel["text"] = "Going to top position"
                
                az, el = coord_helper.calculate_new_coordinates(newPos, newTime)
                az = float(az)
                el = float(el)
            
        #Go down to the bottom of the cross
        control.drive("", el - size)
        time.sleep(0.1)
        
        #Start the measurement
        #Downward scanning motion
        self.crossMeasure(filename, "down", startTime, startPos[0], startPos[1], ra, dec, size)
        
        #Go to the outer left 
        #    .
        #    .
        #o . . . .
        #    .
        #    .
        
        newPos = (az, el)
        
        control.drive(az - size, el)
        time.sleep(0.1)
        
        #Keep the program busy until it has reached the left position
        while control.driving_flag == True:
            self.after(500,self.checkDriving())
            
            self.crossLabel["text"] = "Going to left position"
            
        #Check if tracking was selected and calculate new position 
        if self.flag_dummy:
            az, el = coord_helper.calculate_new_coordinates(startPos, startTime)
            az = float(az)
            el = float(el)
            
            #If the position differs overwrite newPos and newTime and 
            #drive to corrected position; repeat until no difference
            while not newPos[0] - 0.1 < az < newPos[0] + 0.1 or not newPos[1] - 0.1 < el < newPos[1] + 0.1:
                    
                newPos = (az, el)
                newTime = coord_helper.Time.now()
                
                control.drive(az - size, el)
                time.sleep(0.1)
            
                #Keep the program busy until it has reached the left position
                while control.driving_flag == True:
                    self.after(500,self.checkDriving())
                
                    self.crossLabel["text"] = "Going to left position"
                
                az, el = coord_helper.calculate_new_coordinates(newPos, newTime)
                az = float(az)
                el = float(el)

        #Go to the right side of the cross
        control.drive(az + size, "")
        time.sleep(0.1)
        
        #Start the measurement
        #Scanning motion to the right
        self.crossMeasure(filename, "right", startTime, startPos[0], startPos[1], ra, dec, size)

        self.crossLabel["text"] = ""
        tk.messagebox.showinfo("Success", "Cross Scan Done!")
  
    
    ###N-Point-Scan function
    def nPointScan(self):
        coord1 = self.enterCoord1.get()
        coord2 = self.enterCoord2.get()
        #n x n
        gridSize = self.enterGrid.get()
        #How far are the points apart
        pointDist = self.enterDistance.get()
        #How long to measure each point
        duration = self.enterDuration.get()
        
        #Help variable to make sure that the frequencies are written one time in the file
        filehelp = True
        
        #Check if inputs are valid
        try:
            az, el = self.checkSystem(coord1, coord2)
            gridSize, pointDist, duration = self.checkNumericalInput(gridSize, pointDist, duration)
        
        except:
            return
        
        #Define gridsize by steps between each point
        step = (float(gridSize) - 1)/2
        
        #Check if limits fit
        try: 
            control.checkLimits(az, el, step*pointDist)
        
        except ValueError:
            tk.messagebox.showinfo("Warning", "Coordinates out of bounds. \n 42 < Az < 322 \n 22 < El < 90")
            
            return
                
        #Choose file to write data
        filename = self.fileDialog()        
        
        #Set up starting parameters for tracking
        startTime = coord_helper.Time.now()
        startPos = (az, el)
        
        #Calculate equatorial coordinates for file
        ra, dec = coord_helper.convertAzToEq(az, el, startTime)
        
        newTime = startTime
        newPos = startPos
        
        #Go to the top left corner of the grid
        #o . .
        #. . .
        #. . .
        control.drive(az - step*pointDist, el + step*pointDist)
        time.sleep(0.1)
        
        #Keep the program busy until it has reached the first position
        while control.driving_flag == True:
            self.after(500,self.checkDriving())
            
            self.npointLabel["text"] = "Going to position (0,0)"
        
        #Check if tracking was selected and calculate new position az_m, el_m
        if self.flag_dummy:
            az, el = coord_helper.calculate_new_coordinates(startPos, startTime)
            
        az_m = float(az)
        el_m = float(el)
        
        #If the position differs overwrite newPos and newTime and 
        #drive to corrected position; repeat until no difference
        if self.flag_dummy:
            while not newPos[0] - 0.1 < az_m < newPos[0] + 0.1 or not newPos[1] - 0.1 < el_m < newPos[1] + 0.1:
                    
                newPos = (az_m, el_m)
                newTime = coord_helper.Time.now()
                
                control.drive(az_m - step*pointDist, el_m + step*pointDist)
                time.sleep(0.1)
            
                #Keep the program busy until it has reached the top position
                while control.driving_flag == True:
                    self.after(500,self.checkDriving())
                    
                    self.npointLabel["text"] = "Going to position (0,0)"
                
                az, el = coord_helper.calculate_new_coordinates(newPos, newTime)
                az_m = float(az)
                el_m = float(el)
        
        az = az_m - step*pointDist
        el = el_m + step*pointDist
        
        #Define n x n grid and measure each point from top left to top right
        #then go one down and to the left, then one down and so on
        for i in range(int(gridSize)):
            if i % 2 == 0:
                for k in range(int(gridSize)):
                    
                    #Track if selected
                    if self.flag_dummy:
                        az_m, el_m = coord_helper.calculate_new_coordinates(startPos, startTime)
                        az_m = float(az_m)
                        el_m = float(el_m)
                        az = az_m - step*pointDist
                        el = el_m + step*pointDist
                    
                    control.drive(az + k*pointDist, el - i*pointDist)
                    time.sleep(0.1)
                    
                    #Keep program busy until position is reached
                    while control.driving_flag == True:
                        self.after(500,self.checkDriving())
            
                        self.npointLabel["text"] = "Going to position (" + str(i) + "," + str(k) + ")"
                    
                    #The actual measurement
                    self.nPointMeasure(duration, filename, filehelp, i, k, startTime, startPos[0], startPos[1], ra, dec, gridSize, pointDist)
                    
                    #Help variable to make sure that the frequencies are written one time in the file
                    filehelp = False
                    
    
            else:
                for k in range(int(gridSize)):
                    
                    #Track if selected
                    if self.flag_dummy:
                        az_m, el_m = coord_helper.calculate_new_coordinates(startPos, startTime)
                        az_m = float(az_m)
                        el_m = float(el_m)
                        az = az_m - step*pointDist
                        el = el_m + step*pointDist
                    
                    control.drive(az + (gridSize - 1 - k)*pointDist, el - i*pointDist)
                    time.sleep(0.1)
                    
                    #Keep program busy until position is reached
                    while control.driving_flag == True:
                        self.after(500,self.checkDriving())
                        
                        self.npointLabel["text"] = "Going to position (" + str(i) + "," + str(int(gridSize) - 1 - k) + ")"
                    
                    #The actual measurement
                    self.nPointMeasure(duration, filename, filehelp, i, int(gridSize) - 1 - k, startTime, startPos[0], startPos[1], ra, dec, gridSize, pointDist)
        
        self.npointLabel["text"] = ""
        tk.messagebox.showinfo("Success", "NPoint Scan Done!")
    
    
    
#####MEASURING SECTION
    

    ###Choose a file to write the data
    def fileDialog(self):
        dialog = fd.asksaveasfile(initialdir="/home/natlab2/Schreibtisch/Praktikum", filetypes=(("CSV File", "*.csv"),("All Files", "*.*"))).name
        
        return dialog
        
    
    ###Prepare the chosen file with the specific settings (npoint, cross, file)
    def prepareFile(self, filename, filehelp, mode, *args):
        self.measure_abort_flag = False
        
        #Open the selected file
        f = open(filename, "a+")
        
        #Get the current frequencies
        frequencies = osci.get_frequencies()
        
        #Now write a headline with all the necessary information:
        #Az, El, Ra, Dec, settings of the osci and specific details for each mode
        #and a line with the freqencies and the column headers
        
        #N-Point-Scan
        if mode == "npoint":
            #filehelp to write these things just one time
            if filehelp:
                centerfreq, span, rbw, vbw, sweep, preamp = osci.getsettings()
                f.write("Start Time: "  + str(args[3]) + "," + "Az: " + str(args[4]) + "," + "Alt: " + str(args[5]) + "," + "Ra: " + str(args[6]) + ",Dec: " + str(args[7]) + ",Gridsize: " + str(args[8]) + ",Cellsize: " + str(args[9]) + ",Duration: " + str(args[2]) + ",Tracking: " + str(self.flag_dummy) + ",Center frequency: " + str(centerfreq) + ",Span: " + str(span) + ",RBW: " + str(rbw) + ",VBW: " + str(vbw) + ",Sweeptime: " + str(sweep) + ",Preamp: " + preamp + "\n")
                f.write("Time(s),Az,El,Measurement,")
            
                for j in range(len(frequencies)-1):
                    f.write(str(frequencies[j]) + ",")
                f.write(str(frequencies[-1]))
                f.write("\n")
                  
        #Crossscan
        elif mode == "cross":
            #args[0] == "down" to write these things just one time
            if args[0]=="down":
                centerfreq, span, rbw, vbw, sweep, preamp = osci.getsettings()
                f.write("Start Time: "  + str(args[1]) + "," + "Az: " + str(args[2]) + "," + "Alt: " + str(args[3]) + "," + "Ra: " + str(args[4]) + ",Dec: " + str(args[5]) + ",Range: " + str(args[6]) + ",Tracking: " + str(self.flag_dummy) + ",Center frequency: " + str(centerfreq) + ",Span: " + str(span) + ",RBW: " + str(rbw) + ",VBW: " + str(vbw) + ",Sweeptime: " + str(sweep) + ",Preamp: " + preamp + "\n")
                f.write("Time(s),Az,El,Measurement,")
            
                for j in range(len(frequencies)-1):
                    f.write(str(frequencies[j]) + ",")
                f.write(str(frequencies[-1]))
                f.write("\n")
                
        #Regular measurement
        elif mode == "regular":
            centerfreq, span, rbw, vbw, sweep, preamp = osci.getsettings()
            f.write("Start Time: "  + str(args[0]) + "," + "Az: " + str(args[1]) + "," + "Alt: " + str(args[2]) + "," + "Ra: " + str(args[3]) + ",Dec: " + str(args[4]) + ",Tracking: " + str(self.flag_dummy) + ",Center frequency: " + str(centerfreq) + ",Span: " + str(span) + ",RBW: " + str(rbw) + ",VBW: " + str(vbw) + ",Sweeptime: " + str(sweep) + ",Preamp: " + preamp + "\n")
            f.write("Time(s),Az,El,Measurement,")
            
            for j in range(len(frequencies)-1):
                f.write(str(frequencies[j]) + ",")
            f.write(str(frequencies[-1]))
            f.write("\n")
            
        #Schedule measurement    
        elif mode == "file":
            #filehelp to write these things just one time
            if filehelp:
                centerfreq, span, rbw, vbw, sweep, preamp = osci.getsettings()
                f.write("Schedule" + ",Start Time: "  + str(args[0]) + "," + "Az: " + str(args[1]) + "," + "Alt: " + str(args[2]) + "," + "Ra: " + str(args[3]) + ",Dec: " + str(args[4]) + ",Duration: " + str(args[5]) + ",Tracking: " + str(self.flag_dummy) + ",Track while measure: " + str(args[6]) + ",Center frequency: " + str(centerfreq) + ",Span: " + str(span) + ",RBW: " + str(rbw) + ",VBW: " + str(vbw) + ",Sweeptime: " + str(sweep) + ",Preamp: " + preamp + "\n")
                f.write("Time(s),Az,El,Measurement "+str(args[7])+',')
                
                for j in range(len(frequencies)-1):
                    f.write(str(frequencies[j]) + ",")
                f.write(str(frequencies[-1]))
                f.write("\n")
                     
        return f

    
    ###Function called by the 'Measure'-button
    def measure(self):
        #Choose a fitting file
        filename = self.fileDialog()
        
        startTime = coord_helper.Time.now()
        #Parse out the current coordinates from the dynamic labels
        az = float(self.dynamicAz["text"].split(" ")[1])
        el = float(self.dynamicEl["text"].split(" ")[1])
        
        #Calculate equatorial coordinates for the file
        ra, dec = coord_helper.convertAzToEq(az, el, startTime)
   
        #Set up a fitting file
        f = self.prepareFile(filename, False, "regular", startTime, az, el, ra, dec) #False as the filehelp input
        
        startTime = time.time()
        
        #Measure as long as the button 'Stop' is not clicked
        idx = 0
        
        while True:
            if idx % 5 == 0:
                #self.update() to interact with GUI during measurement
                self.update()
            
            if self.measure_abort_flag == False:
                #Ask the spectrograph for the amplitudes and
                #write them with details into the file
                amplitudes = osci.inst.ask(":TRAC? TRACE1")
                f.write(str(time.time()-startTime) + "," + str(self.last_position[0]) + ","+ str(self.last_position[1]) + "," + "regular" + "," + amplitudes[12:]+"\n")
                
                idx += 1
        
        f.close()
        
        
    ###Function only to measure during cross scan 
    #args: startTime, startPos[0], startPos[1], ra, dec, size
    def crossMeasure(self, filename, direction, *args):
        #Set up a fitting file
        f = self.prepareFile(filename, False, "cross", direction, args[0], args[1], args[2], args[3], args[4], args[5]) 
        
        startTime = time.time() 
        
        #Measure while the telescope is in the scanning motion
        idx = 0
        
        while control.driving_flag == True:
            #self.update() to interact with GUI during measurement
            if idx % 5 == 0:
                self.update()
            
            if self.measure_abort_flag == False:
                #checkDriving updates labels and positions
                self.after(500,self.checkDriving())
                
                #Ask the spectrograph for the amplitudes and
                #write them with details into the file
                amplitudes = osci.inst.ask(":TRAC? TRACE1")
                f.write(str(time.time() - startTime) + "," + str(self.last_position[0])+ ","+ str(self.last_position[1])+ "," + direction + "," + amplitudes[12:] + "\n")
                
                self.crossLabel["text"] = "Going " + direction 
                    
                idx += 1
        
        f.close()
        #Set the measure_abort_flag to True
        self.abrt()
    
    
    ###Function only to measure during npoint scan 
    #args: startTime, startPos[0], startPos[1], ra, dec, gridSize, pointDist
    def nPointMeasure(self, duration, filename, filehelp, i, k, *args):
        #Set up a fitting file
        f = self.prepareFile(filename, filehelp, "npoint", i, k, duration, args[0], args[1], args[2], args[3], args[4], args[5], args[6])
        
        startTime = time.time()
        
        #Measure for the requested time
        #for the rest see crossMeasure()
        idx = 0
        
        while (time.time() - startTime) < duration:
            if idx % 5 == 0:
                self.update()
            
            if self.measure_abort_flag == False:
                amplitudes = osci.inst.ask(":TRAC? TRACE1")
                f.write(str(time.time()-startTime) + "," + str(self.last_position[0]) + "," + str(self.last_position[1]) + "," + "(" + str(i) + str(k) + ")" + "," + amplitudes[12:] + "\n")
                
                self.npointLabel["text"] = "Measuring position (" + str(i) + ", " + str(k) + ")"
                
                idx += 1
        
        f.close()
        self.abrt()
    
    
    ###Function only to measure during a schedule     
    #args: az, el, ra, dec, duration, trackMeasure, startTime, startPos
    def filemeasure(self, savefile, filehelp, nmbr, *args): 
        startTime = coord_helper.Time.now()
        
        #Set up a fitting file
        f = self.prepareFile(savefile, filehelp, "file", startTime, args[0], args[1], args[2], args[3], args[4], args[5], nmbr) 
        
        startTime = time.time()
        
        self.scheduleLabel["text"] = "Observing object " + str(nmbr)
        
        #How often should be tracked (in seconds)
        trackPeriod = float(self.entertrackperiod.get())  
        
        #Measure as long as requested
        #trackCounter to calculate the time when the position should be tracked
        idx = 0
        trackCounter=0
        
        while (time.time() - startTime) < float(args[4]):
            
            #Check if tracking is selected
            if self.flag_dummy == True:
                
                #Correct the old position every trackCounter period
                if (time.time() - startTime) // trackPeriod > trackCounter:
                    az, el = coord_helper.calculate_new_coordinates(args[7], args[6])
                    control.drive(az, el)
                    time.sleep(0.1)
                    
                    #Check if measuring while tracking is selected and
                    #switch flags for the displayed label
                    if args[5] == "n" or args[5] == "0" or args[5] == "False":
                        self.abrt()
                        #Keep the program busy
                        while control.driving_flag == True:
                            self.after(500,self.checkDriving())
                        self.measure_abort_flag = False
                        self.update()
                        
                    trackCounter+=1 
            
            #for the rest see crossMeasure()
            if idx % 5 == 0:
                self.update()
            
            if self.measure_abort_flag == False:
                amplitudes = osci.inst.ask(":TRAC? TRACE1")
                f.write(str(time.time()-startTime) + "," + str(self.last_position[0]) + ","+ str(self.last_position[1]) + "," + str(nmbr) + "," + amplitudes[12:]+"\n")
                idx += 1

        f.close()
        self.abrt()
        self.scheduleLabel["text"] = ""
    
    
    ###Set the measure_abort_flag to True
    def abrt(self):
        self.measure_abort_flag=True
    
    
    
#####SCHEDULE SECTION   
 
    
    ###Create an observation schedule    
    def createschedule(self):
        #Possible input 
        header = ["Ra", "Dec", "Duration (s)", "Track (y/n)", "Measure while Tracking (y/n)", "Name (optional)"]
        df = pd.DataFrame(columns = header)
        #Choose a file 
        dialog = fd.asksaveasfile(initialdir="/home/natlab2/Schreibtisch/Schedules", filetypes=(("CSV File", "*.csv"),("All Files", "*.*"))).name
        #Set the chosen file to current_file
        self.current_file=dialog
        #Write the header into the file without row indices
        df.to_csv(dialog, index= False)
        
        
    ###Add objects to a schedule
    def add_item(self):    
        ra=self.enterrasched.get()
        dec=self.enterdecsched.get()
        duration=self.enterdursched.get()
        track=self.track_entry.get()
        mwt=self.mwtrack_entry.get()
        name=self.enternamesched.get()
        
        #Check if inputs are valid
        try:
            self.isAngle(ra, dec)
            duration = self.checkNumericalInput(duration)[0]
            
        except:
            return
        
        #Write them into a DataFrame
        row=[ra, dec, duration, track, mwt, name]
        df = pd.DataFrame(columns = row)
        
        #If a file is selected, append them
        #otherwise create a new one and append then
        try:
            df.to_csv(self.current_file, index= False, mode='a')
            tk.messagebox.showinfo("Done", "Object successfully added to " + self.current_file + " !")
            
        except:
            tk.messagebox.showinfo("Info", "Please create a schedule first in the next step.")
            self.current_file = fd.asksaveasfile(initialdir="/home/natlab2/Schreibtisch/Schedules", filetypes=(("CSV File", "*.csv"),("All Files", "*.*"))).name
            header = ["Ra", "Dec", "Duration (s)", "Track (y/n)", "Measure while Tracking (y/n)", "Name (optional)"]
            headdf = pd.DataFrame(columns = header)
            headdf.to_csv(self.current_file, index= False)
            df.to_csv(self.current_file, index= False, mode='a')
            tk.messagebox.showinfo("Done", "Object successfully added to " + self.current_file + " !")
            
            
    ###Load and execute a schedule measurement
    def schedule(self): 
        #Choose a schedule
        filepath = fd.askopenfile(initialdir="/home/natlab2/Schreibtisch/Schedules", filetypes=(("CSV File", "*.csv"),("All Files", "*.*")))
        
        #Save the header as names to skip it
        header = ["Ra", "Dec", "Duration (s)", "Track", "Measure while Tracking", "Name (optional)"] ###evtl Oscidaten
        schedule = pd.read_csv(filepath, skiprows=1, names=header)
        
        #Choose a file to save the data
        savefile = self.fileDialog()
        
        #Get the trackperiod and check if it is a valid input
        trackPeriod = self.entertrackperiod.get()
        try:
            trackPeriod = self.checkNumericalInput(trackPeriod)[0]
            
            if float(trackPeriod) < 3:
                tk.messagebox.showinfo("Warning", "Trackingspeed > 2s")
                return 
        
        except:
            return
        
        
        startTime = coord_helper.Time.now()
        
        #For loop to iterate over all objects in the file 
        for i in range(len(schedule)):
            #Extract the values
            checkra = str(schedule.iloc[i][0])
            checkdec = str(schedule.iloc[i][1])
            checkduration = str(schedule.iloc[i][2])
            checktrack = str(schedule.iloc[i][3])
            checktrackMeasure = str(schedule.iloc[i][4])
            
            #Check if input is valid 
            try:
                az, el = self.isAngle(checkra, checkdec) 
            
            except:
                return
            
            #Estimate the end time after the measurement for each object
            #to calculate its end position and check if the limits fit
            startPos = (az, el)
            #numbers from estimation (see bottom)
            aztime=abs((az-self.last_position[0])*112/40)
            eltime=abs((az-self.last_position[0])*61/40)
            
            #Check if remaining input is valid
            try:
                checkduration = self.checkNumericalInput(checkduration)[0]
                
            except:
                return
            
            if checktrack != "y" and checktrack != "n" and checktrack != "True" and checktrack != "False" and checktrack != "1" and checktrack != "0":
                tk.messagebox.showinfo("Warning", "Invalid input: " + checktrack)
                return
            
            if checktrackMeasure != "y" and checktrackMeasure != "n" and checktrackMeasure != "True" and checktrackMeasure != "False" and checktrackMeasure != "1" and checktrackMeasure != "0":
                tk.messagebox.showinfo("Warning", "Invalid input: " + checktrackMeasure)
                return
            
            #Calculate the measurement time 
            az, el = coord_helper.calculate_new_coordinates(startPos, startTime + (float(checkduration) + max(aztime, eltime) + 5)*coord_helper.u.second)   #5 secconds tolerance 
            
            #Check if limits fit
            try:
                control.checkLimits(float(az), float(el))
                
            except ValueError:
                tk.messagebox.showinfo("Warning", "Coordinates of object "+str(i)+"\n out of bounds. \n 42 < Az < 322 \n 22 < El < 90")
            
                return
             
            #Add the time to startTime for the other objects
            startTime=startTime + (float(checkduration) + max(aztime, eltime) + 5)*coord_helper.u.second

        #If the checks do not fail, measure each object in the schedule with
        #the requested details
        for i in range(len(schedule)):
            ra = str(schedule.iloc[i][0])
            dec = str(schedule.iloc[i][1])
            duration = str(schedule.iloc[i][2])
            track = str(schedule.iloc[i][3])
            trackMeasure = str(schedule.iloc[i][4])
            
            #Check if input is valid and transform to Az, El
            try:
                az, el = self.isAngle(ra, dec)  
            
            except:
                return
            
            #Check if tracking
            if track == "y" or track == "1" or track == "True":
                self.trackBox.select()
                self.flag_dummy = True
            
            if track == "n" or track == "0" or track == "False":
                self.trackBox.deselect()
                self.flag_dummy = False
                
            
            #Set up starting parameters for tracking
            startTime = coord_helper.Time.now()
            startPos = (az, el)
        
            newTime = startTime
            newPos = startPos
            
            #Go to object
            control.drive(az, el)
            time.sleep(0.1)
            
            self.scheduleLabel["text"] = "Going to object " + str(i)
            
            #Keep the program busy until it has reached the object
            while control.driving_flag == True:
                self.after(500,self.checkDriving())
            
            #Check if tracking is selected and calculate new position
            if self.flag_dummy:
                az, el = coord_helper.calculate_new_coordinates(startPos, startTime)
                az = float(az)
                el = float(el)
            
                #If the position differs overwrite newPos and newTime and 
                #drive to corrected position; repeat until no difference
                while not newPos[0] - 0.1 < az < newPos[0] + 0.1 or not newPos[1] - 0.1 < el < newPos[1] + 0.1:
                        
                    newPos = (az, el)
                    newTime = coord_helper.Time.now()
                    
                    control.drive(az, el)
                    time.sleep(0.1)
                
                    #Keep the program busy until it has reached the object
                    while control.driving_flag == True:
                        self.after(500,self.checkDriving())
                    
                    az, el = coord_helper.calculate_new_coordinates(newPos, newTime)
                    az = float(az)
                    el = float(el)
            
            #The actual measurement
            self.filemeasure(savefile, True, i, az, el, ra, dec, duration, trackMeasure, startTime, startPos) 
        
        self.scheduleLabel["text"] = ""
        tk.messagebox.showinfo("Success", "Schedule Done!")    
        


#####PLOTTING SECTION
    
    
    ###Choose a file to plot
    def chooseFile(self, ismean):   
        self.indexLabel["text"] = 0
        filepath = fd.askopenfilename(initialdir="/home/natlab2/Schreibtisch/Praktikum", filetypes=(("CSV File", "*.csv"),("All Files", "*.*")))
        
        #Specify if schedule or not
        mode=pd.read_csv(filepath, nrows=1).columns[0]
        
        self.dataFrame = pd.read_csv(filepath, skiprows=1)
        
        #If schedule file: delete redundant string rows
        if mode=='Schedule':
            self.dataFrame=self.dataFrame[(self.dataFrame['Time(s)']!='Schedule')&(self.dataFrame['Time(s)']!='Time(s)')]
            
        #If plotmean: calculate it first
        if ismean:
           self.calcmean()
        
        #If not plotmean: plot normally with meanIndex = 4
        else:
            plotIndex = self.getIndex()
            self.plot(plotIndex, 4)
        
        
    ###Calculate the mean value(s) of a chosen file
    def calcmean(self):   
        #Pandas calculates the mean of the single groups (NPoint,
        #Cross and Schedule do have several)
        self.dataFrame = self.dataFrame.groupby(self.dataFrame.columns[3]).mean()
        
        #meanIndex = 3 since the mean is plotted and a string column is ignored
        plotIndex = self.getIndex()
        self.plot(plotIndex, 3)
        
        
    ###Get the index to plot the n-th data row 
    def getIndex(self): 
        #Check if index is valid (number and not out of range)
        try:
            plotIndex = int(self.indexLabel["text"]) 
            #Next line for index error check
            self.dataFrame.iloc[plotIndex,4:]
            
        except ValueError:
            tk.messagebox.showinfo("Warning", "Invalid input.")
            return
        
        except IndexError:
            tk.messagebox.showinfo("Warning", "Index out of range.")
            return
    
        return plotIndex
    
    
    ###Called by the -10/-1/reset/+1/+10 buttons to change data row index    
    def changeIndexAndPlot(self, arg):
        #Check if a file is chosen
        try:    
            idx=self.getIndex()
            
        except AttributeError:
            tk.messagebox.showinfo("Warning", "Choose a file.")
            return
        
        #Check if index idx+arg out of range
        try:
            self.dataFrame.iloc[idx + arg, 4:]
            
        except IndexError:
            tk.messagebox.showinfo("Warning", "Index out of range.")
            return

        self.indexLabel["text"] = idx + arg
        
        #Distinguish a mean plot and a normal plot: mean has one column less
        if len(self.dataFrame.columns) == 604:
            #mean plot (meanIndex = 3)
            self.plot(idx + arg, 3)
            
        else:
            #regular plot (meanIndex = 4)
            self.plot(idx + arg, 4)
            
            
    ###Set the plotindex to 0 and plot (see changeIndexAndPlot)
    def resetIndex(self):
        self.indexLabel["text"] = 0
        
        try:
            if len(self.dataFrame.columns) == 604:
                self.plot(0, 3)
            
            else:
                self.plot(0, 4)
           
        except AttributeError:
            tk.messagebox.showinfo("Warning", "Choose a file.")
        
        
    ###Plot a data file
    #plotIndex referres to the n-th data row
    #meanIndex is 3 or 4; it specifies if the mean should be plotted since 
    #one string column is ignored by the .mean() function so 3 instead of 4
    def plot(self, plotIndex, meanIndex):
        x = []
        y = []
        
        #Set up two lists of values to be plotted
        for i in self.dataFrame.columns.values[meanIndex:]:
            x.append(float(i))
        for i in self.dataFrame.iloc[plotIndex, meanIndex:]:
            y.append(float(i))
        
        #Plot x, y
        self.axes.cla()        
        self.canvas.draw()
            
        self.axes.plot(x,y) 
        self.axes.set_xlabel('Frequency [Hz]')
        #Plot only the relevant area if the spectrograph doesn´t work
        #self.axes.set_ylim(-80,-70)
        self.axes.set_ylabel('Amplitude [dBm]')
        self.canvas.draw()    
        
        
        
#####OTHER STUFF SECTION

    
    ###Remove the duplicates of oversampling from a data file 
    def cleanse(self):
        #Choose the file
        filepath = fd.askopenfilename(initialdir="/home/natlab2/Schreibtisch/Praktikum", filetypes=(("CSV File", "*.csv"),("All Files", "*.*")))
        
        #Extract the chosen filename from filepath and strip the .csv
        filename = filepath.split("/")[-1][:-4]
        #Extract the header
        headerFrame=pd.read_csv(filepath)[0:0]
        #Delete the header from the file
        self.dataFrame = pd.read_csv(filepath, skiprows=1)
    
        #Drop the duplicates and write the extracted header with the 
        #remaining rows into a new file filenameClean.csv
        self.dataFrame = self.dataFrame.drop_duplicates(self.dataFrame.columns.values[3:])
        headerFrame.to_csv('/home/natlab2/Schreibtisch/Praktikum/' + filename + 'Clean.csv', index= False)
        self.dataFrame.to_csv('/home/natlab2/Schreibtisch/Praktikum/' + filename + 'Clean.csv', index= False, mode='a')
            
    
    ###Quit the program
    def __close(self):
        self.quit()
        osci.destroy()
        self.destroy()
        
        
        
#####COMMENT SECTION
      

#CCW=Az lower=BP@
#CW=Az higher = AP@
#Down=El lower = HP@
# Up=El higher =DP@
# Down + CCW=JP@
# Down + CW=IP@
# Up+ CCW =  FP@
# Up + CW =  EP@
#nothing=@P@
        
#driving speed telescope
#El:40°=61s
#Az: 40°=112s
#together: same as both on their own

###El in Alt ändern?
###was ist mit den Oscieinstellungen??? eher mal nicht, kann man am Anfang einmal einstellen
        
    
if __name__ == "__main__":
    TelescopeDrive()

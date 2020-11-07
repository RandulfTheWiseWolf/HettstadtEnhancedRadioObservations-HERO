import usbtmc


class DSA815(object):
    
    
    def __init__(self):
        pass
        
    ###Attempt to connect to the spectrograph
    def conn(self, constr="USB0::0x1AB1::0x0960::DSA8B180500029::INSTR"):
       
        
        self.inst = usbtmc.Instrument(constr)
        
        #Set basic spectrograph settings
        self.inst.write(":SENS:FREQ:CENT 1420000000\n")
        self.inst.write(":SENS:FREQ:SPAN 100000000\n")
        self.inst.write(":SENS:BAND:VID 1000000\n")
        self.inst.write(":SENS:BAND:RES 1000000\n")
        self.inst.write(":SENS:SWE:TIME 1\n")
        
    ###Return identify string which has serial number
    def identify(self):
        return self.inst.ask("*IDN?")

    def TG_enable(self, state):
        if state:
            tstate = "1"
        else:
            tstate = "0"

        self.inst.write(":OUTput:STATe %s\n"%tstate)

    def TG_amp(self, amp):
        """Set the TG output amplitude power in dBm"""

        if amp > 0 or amp < -20:
            raise ValueError("Amplitude outside of allowed range -20dBm to 0dBm")
        
        self.inst.write(":SOUR:POW:LEV:IMM:AMPL {}\n".format(amp))

    def set_span(self, span):
        self.inst.write(":SENS:FREQ:SPAN {}\n".format(span))

    def set_centerfreq(self, freq):        
        self.inst.write(":SENS:FREQ:CENT {}\n".format(freq))
        
    def set_vbw(self, vbw):
        self.inst.write(":SENS:BAND:VID {}\n".format(vbw))
        
    def set_rbw(self, rbw):
        self.inst.write(":SENS:BAND:RES {}\n".format(rbw))
        
    def set_sweeptime(self, sweeptime):
        self.inst.write(":SENS:SWE:TIME {}\n".format(sweeptime))
        
    def preamp_on(self):
        self.inst.write(":SENSe:POWer:RF:GAIN:STATe ON")
        
    def preamp_off(self):
        self.inst.write(":SENSe:POWer:RF:GAIN:STATe OFF")
    
    
    ###Calculate the current frequencies
    #101 < sweeppoints < 3001!!!
    def get_frequencies(self, sweeppoints = 601):
        minfreq = float(self.inst.ask(":SENS:FREQ:STAR?")) 
        maxfreq = float(self.inst.ask(":SENS:FREQ:STOP?"))
        step = (maxfreq - minfreq)/(sweeppoints - 1)
        
        freqs = []
        for i in range(sweeppoints):
            freqs.append(minfreq + i*step)
            
        return freqs
    
    
    ###Get current spectrograph settings
    def getsettings(self):
        centerfreq = float(self.inst.ask(":SENS:FREQ:CENT?"))
        span = float(self.inst.ask(":SENS:FREQ:SPAN?"))
        rbw = float(self.inst.ask(":SENS:BAND:RES?"))
        vbw = float(self.inst.ask(":SENS:BAND:VID?"))
        sweep = float(self.inst.ask(":SENS:SWE:TIME?"))
        preamp = self.inst.ask(":SENS:POW:RF:GAIN:STAT?")
        if preamp == "1":
            preamp = "ON"
        elif preamp == "0":
            preamp = "OFF"
        
        return centerfreq, span, rbw, vbw, sweep, preamp
    

    def destroy(self):
        del self.inst
        
    def configure(self):
        return self.inst.ask(":CONF?")
'''

if __name__ == '__main__':
    test = DSA815()
    
    

    #Insert your serial number here / confirm via Ultra Sigma GUI
    test.conn("USB0::0x1AB1::0x0960::DSA8B180500029::INSTR")

    #test.preamp_on()
    time.sleep(1)
    #print(test.inst.ask(":SENSe:POWer:RF:GAIN:STATe?"))

    print("Identity string:\n  %s\n"%test.identify())
    
    test.inst.write("*RST")
    test.inst.write("*ESE 60")
    test.inst.write("*SRE 48")
    test.inst.write("*CLS")
    
    print(test.inst.ask(":SYST:ERR:NEXT?"))
    
    print(test.inst.ask(":STAT:OPER:COND?"))
    
    #test.inst.write(":CALC:MARK:AOFF")
    
    #test.inst.write(":INIT")
    
    #test.inst.write("*CLS")

    #test.inst.ask("*OPC?")
    #test.set_centerfreq(1420000000)
    #print(test.inst.ask(":SENS:FREQ:CENT?"))
    #test.inst.write(":FREQ:CENT:STEP:AUTO ON")
    
    test.inst.write(":SENS:FREQ:CENT 1420000000")
    test.inst.write(":SENS:FREQ:SPAN 100000000")

    print(test.inst.ask(":SENS:FREQ:CENT?"))
    print(test.inst.ask(":SENS:FREQ:SPAN?"))
    
    #test.inst.write("TRAC:CLE:ALL")
    
    #print(test.inst.ask(":TRAC? TRACE1"))
    
    test.inst.write(":FREQ:STAR 1.37E+9")
    test.inst.write(":FREQ:STOP 1.47E+9")
    
    test.inst.write(":SWE:TIME 1.")
    test.inst.write(":SWE:TIME:AUTO:RUL NORM")
    test.inst.write(":SWE:COUN 1.")
    test.inst.write(":BAND:RES 1000.")
    test.inst.write(":BAND:VID:AUTO ON")
    
    test.inst.write(":POW:ATT 0.")
    test.inst.write(":UNIT:POW DBM")
    test.inst.write(":DISP:WIN:TRAC:Y:SCAL:RLEV 0.")
    test.inst.write(":INP:IMP 50.")
    test.inst.write(":POW:GAIN ON")
    
    print(test.inst.ask(":SYST:ERR?"))
    time.sleep(20)
    test.inst.write(":FORM:ASC")

    print(test.inst.ask(":TRAC? TRACE1"))
    #print(test.inst.ask(":TRAC? TRACE2"))
    #print(test.inst.ask(":TRAC? TRACE3"))
    #print(test.inst.ask(":TRAC? TRACE4"))
    
    #test.set_centerfreq(1.47E+9)
    #test.set_span(8E+8)
    
    #test.inst.write(":MMEM:STOR:TRAC TRACE1 Schreibtisch\esgeht.csv")
    
    #test.inst.write(":SENSe:POWer:RF:GAIN:STATe ON")
    
    #test.inst.write(":FREQ:SPAN:FULL")
    
    #test.inst.write(':TRAC:CLE:ALL')

    #print(test.inst.ask(":FREQuency:CENTer:STEP:AUTO?"))
    
    f = open("/home/natlab2/Schreibtisch/HERO/trace1.csv", "a+")
    frequencies = test.get_frequencies()
    f.write("\t")
    for j in range(len(frequencies)):
        f.write(str(frequencies[j]) + "\t")
    
    f.write("\n\n")
    
    startTime = time.time()
    i = 1
    while i < 20:
        amplitudes = test.inst.ask(":TRAC? TRACE1")
        #amplitudes = amplitudes.split(", ")
        #amplitudes[0] = amplitudes[0][12:]
        f.write(str(time.time()-startTime) + "\t" + amplitudes[12:] + "\n\n\n\n\n")
        print(i)
        i += 1
        
    f.close()
    
    
    #test.inst.write("MMEM:STOR:TRAC TRACE1,E\schmall.csv")

   
    test.destroy()
''' 


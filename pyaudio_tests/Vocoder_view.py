from tkinter import filedialog
import tkinter as tk
import tkinter.ttk as ttk

from Controller import Controller, MODE
import threading

class VocoderGUI:
    def __init__(self,master):
        topFrame = ttk.Frame(master)
        topFrame.pack()
        bottomFrame = ttk.Frame(master)
        bottomFrame.pack(side=tk.BOTTOM)

        self.processing = False
        self.controller = Controller()
        self.devices = self.controller.get_devices()


        self.startButton = ttk.Button(topFrame, text = "START", command=self.runVocoder)
        self.startButton.grid(column =4, row=1)


        self.stopButton = ttk.Button(topFrame, text= "STOP", command = self.stopVocoder)
        self.stopButton.grid(column=4, row=2)

        #MIC INPUT menu
        ttk.Label(topFrame, text="MIC INPUT").grid(column=1, row=0)
        self.micString = tk.StringVar()
        self.micChosen = ttk.Combobox(topFrame, width=12, textvariable=self.micString)
        self.micChosen['values'] = list(self.devices.keys())
        self.micChosen.grid(column=1, row=1)
        self.micChosen.current(0)

        # SIGNAL INPUT menu
        ttk.Label(topFrame, text="SIGNAL INPUT").grid(column=1, row=2)
        self.signalString = tk.StringVar()
        self.signalChosen = ttk.Combobox(topFrame, width=12, textvariable=self.signalString)
        self.signalChosen['values'] = ("LINE1", "LINE2","PIŁA", "PROSTOKAT")
        self.signalChosen.grid(column=1, row=3)
        self.signalChosen.current(1)

        #  BUTTON TO CHOOSE CARR FILE
        self.chooseCarrButton = ttk.Button(topFrame, text="CHOOSE CARR FILE", command=self.chooseCarrFilename)
        self.chooseCarrButton.grid(column=3, row=1)

        #  BUTTON TO CHOOSE MOD FILE
        self.chooseModButton = ttk.Button(topFrame, text="CHOOSE MOD FILE", command=self.chooseModFilename)
        self.chooseModButton.grid(column=3, row=2)

        """
        #BUTTON TO CHECK HOW CHECK DEVICE'S INDEX
        self.choose_fileButton = Button(topFrame, text=" DEVICE'S INDEX", command=self.controller.get_devices)
        self.choose_fileButton.grid(column=1, row=4)
        """

        # LPC/FFT BUTTON
        tk.Label(topFrame, text="LPC/FFT").grid(column=1, row=5)
        self.t_btn = ttk.Button(topFrame, text="FFT", command=self.toggle)
        self.t_btn.grid(column =1, row =6)

    def runVocoder(self):
        if not self.processing:
            self.controller.set_vocoder_mode(mode=MODE.file,
                                             mod_path=self.carrFile,
                                             carr_path=self.modFile)

            self.t1 = threading.Thread(target=self.process)
            self.t1.start()
            #print("Chosen input mic : " + str(self.micString))
            #print("Choosen input signal: " + str(self.signalString))
            self.returnMicInput()


    def stopVocoder(self):
        self.processing = False

    def chooseInput1(self):
        print("wybieram input1")

    def process(self):
        self.processing = True
        while self.processing:
            self.controller.runVocoder()

    def chooseCarrFilename(self):
        self.carrFile = filedialog.askopenfilename(initialdir="./wavs", title="Select Carr file")
        print("choosen carr: " + str(self.carrFile))
        #return self.carrFile


    def chooseModFilename(self):
        self.modFile = filedialog.askopenfilename(initialdir="./wavs", title="Select Mod file")
        print("choosen mod: " + str(self.modFile))
        #return self.modFile

    def returnMicInput(self):
        print("chosen mic input: " + str(self.devices[self.micString.get()]))


    def toggle(self):
        '''
        use
        t_btn.config('text')[-1]
        to get the present state of the toggle button
        '''
        if self.t_btn.config('text')[-1] == 'FFT':
            self.t_btn.config(text='LPC')
            self.controller.setFFT()

        else:
            self.t_btn.config(text='FFT')
            self.controller.setLPC()



# ---------JAK ODPALAC VOCODER GUI-----------
root = tk.Tk()
vocoder = VocoderGUI(root)
root.mainloop()

from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *

from Controller import Controller, MODE
import threading

class VocoderGUI:
    def __init__(self,master):
        topFrame = Frame(master)
        topFrame.pack()
        bottomFrame = Frame(master)
        bottomFrame.pack(side=BOTTOM)

        self.processing = False
        self.controller = Controller()


        self.startButton = Button(topFrame, text = "START", command=self.runVocoder)
        self.startButton.grid(column =4, row=1)


        self.stopButton = Button(topFrame, text= "STOP", command = self.stopVocoder)
        self.stopButton.grid(column=5, row=1)

        #  BUTTON TO CHOOSE FILE
        #  then -> self.filename = filedialog.askopenfilename(initialdir = "/",title = "Select file")

        #MIC INPUT menu
        Label(topFrame, text="MIC INPUT").grid(column=1, row=0)
        self.string = StringVar()
        self.stringChosen = Combobox(topFrame, width=12, textvariable=self.string)
        self.stringChosen['values'] = ("LINE1", "LINE2")  
        self.stringChosen.grid(column=1, row=1)
        self.stringChosen.current(0)

        # SIGNAL INPUT menu
        Label(topFrame, text="SIGNAL INPUT").grid(column=1, row=2)
        self.string = StringVar()
        self.stringChosen = Combobox(topFrame, width=12, textvariable=self.string)
        self.stringChosen['values'] = ("LINE1", "LINE2","PIŁA", "PROSTOKAT")
        self.stringChosen.grid(column=1, row=3)
        self.stringChosen.current(1)

    def runVocoder(self):
        if not self.processing:
            self.controller.set_vocoder_mode(mode=MODE.file,
                                             mod_path='wavs/modulator_2.wav',
                                             carr_path='wavs/carrier_2.wav')

            self.t1 = threading.Thread(target=self.process)
            self.t1.start()

    def stopVocoder(self):
        self.processing = False

    def chooseInput1(self):
        print("wybieram input1")

    def process(self):
        self.processing = True
        while self.processing:
            self.controller.runVocoder()



# ---------JAK ODPALAC VOCODER GUI-----------
root = Tk()
vocoder = VocoderGUI(root)
root.mainloop()

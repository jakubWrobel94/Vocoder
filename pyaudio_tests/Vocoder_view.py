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
        self.stopButton.grid(column=4, row=2)

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

        #  BUTTON TO CHOOSE FILE
        self.choose_fileButton = Button(topFrame, text="CHOOSE FILE", command=self.chooseFilename)
        self.choose_fileButton.grid(column=3, row=1)

        #BUTTON TO CHECK HOW CHECK DEVICE'S INDEX
        self.choose_fileButton = Button(topFrame, text=" DEVICE'S INDEX", command=self.controller.get_devices)
        self.choose_fileButton.grid(column=1, row=4)

        # LPC/FFT BUTTON
        Label(topFrame, text="LPC/FFT").grid(column=1, row=5)
        self.t_btn = Button(topFrame, text="FFT", command=self.toggle)
        self.t_btn.grid(column =1, row =6)

    def runVocoder(self):
        if not self.processing:
            self.controller.set_vocoder_mode(mode=MODE.file,
                                             mod_path='wavs/modulator_2.wav',
                                             carr_path='wavs/carrier_2.wav')   # trzeba stworzyć metodę do automatycznego dodawania tych ścieżek do plików

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

    def chooseFilename(self):
        filedialog.askopenfilename(initialdir="/", title="Select file")


    def toggle(self):
        '''
        use
        t_btn.config('text')[-1]
        to get the present state of the toggle button
        '''
        if self.t_btn.config('text')[-1] == 'FFT':
            self.t_btn.config(text='LPC')
            print("pressed FFT")
        else:
            self.t_btn.config(text='FFT')
            print("pressed LPC")



# ---------JAK ODPALAC VOCODER GUI-----------
root = Tk()
vocoder = VocoderGUI(root)
root.mainloop()

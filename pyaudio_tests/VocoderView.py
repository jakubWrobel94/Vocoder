import kivy
import Controller
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.base import runTouchApp
from Controller import MODE
from functools import partial
from kivy.properties import ObjectProperty
import os

class VocoderView(GridLayout):

    # kivy objects references
    input_devices_button = ObjectProperty(None)
    output_devices_button = ObjectProperty(None)
    carrier_source_button = ObjectProperty(None)
    modulator_source_button = ObjectProperty(None)
    mode = MODE.file

    input_devices = None
    output_devices = None
    input_device_index = None
    output_device_index = None
    carrier_file_path = None
    modulator_file_path = None

    def __init__(self, **kwargs):
        super(VocoderView, self).__init__(**kwargs)
        self.controller = Controller.Controller()
        self.fill_input_devices_list()
        self.fill_output_devices_list()

    def fill_input_devices_list(self):

        ''' Fill input devices droplist(kivy.uix.dropdown.DropDopwn) with names of current input audio devices'''

        self.input_devices = self.controller.get_input_devices()
        self.dropdown_input = DropDown()
        for key in self.input_devices.keys():
            device = self.input_devices[key]
            btn = Button(text=device['name'], size_hint_y=None, height=35, font_size=11)
            btn.bind(on_release=lambda btn: self.dropdown_input.select(btn.text))
            self.dropdown_input.add_widget(btn)
        self.input_devices_button.bind(on_release=self.dropdown_input.open)
        self.dropdown_input.bind(on_select=lambda instance, x: setattr(self.input_devices_button, 'text', x))
        self.dropdown_input.bind(on_select=lambda instance, x: self.set_input_device_index(name=x))

    def fill_output_devices_list(self):

        ''' Fill output devices droplist(kivy.uix.dropdown.DropDopwn) with names of current output audio devices'''

        self.output_devices = self.controller.get_output_devices()
        self.dropdown_output = DropDown()
        for key in self.output_devices.keys():
            device = self.output_devices[key]
            btn = Button(text=device['name'], size_hint_y=None, height=35, font_size=11)
            btn.bind(on_release=lambda btn: self.dropdown_output.select(btn.text))
            self.dropdown_output.add_widget(btn)
        self.output_devices_button.bind(on_release=self.dropdown_output.open)
        self.dropdown_output.bind(on_select=lambda instance, x: setattr(self.output_devices_button, 'text', x))
        self.dropdown_output.bind(on_select=lambda instance, x: self.set_output_device_index(name=x))

    def set_input_device_index(self, **kwargs):

        ''' Set choosen input device index. Method searches index of chosen audio device name inside droplist'''

        name = kwargs['name']
        for idx, val in self.input_devices.items():
            if val['name'] == name:
                self.input_device_index = idx
                self.fill_sources_droplists(val['max'])

    def set_output_device_index(self, **kwargs):

        ''' Set choosen output device index. Method searches index of chosen audio device name inside droplist'''

        name = kwargs['name']
        for idx, val in self.output_devices.items():
            if val['name'] == name:
                self.output_device_index = idx

    def fill_sources_droplists(self, max):

        ''' This method fills droplists of carrier and modulator sources with
        available inputs in currently chosen audio input device'''

        self.dropdown_carr = DropDown()
        self.dropdown_mod = DropDown()
        for i in range(0, max):
            text_inp = 'Input %d' % i
            btn_carr = Button(text=text_inp, size_hint_y=None, height=30, font_size=11)
            btn_mod = Button(text=text_inp, size_hint_y=None, height=30, font_size=11)
            btn_carr.bind(on_release=lambda btn: self.dropdown_carr.select(btn.text))
            btn_mod.bind(on_release=lambda btn: self.dropdown_mod.select(btn.text))
            self.dropdown_carr.add_widget(btn_carr)
            self.dropdown_mod.add_widget(btn_mod)

        carr_but_callback = partial(self.on_carrier_source_click, dropdown=self.dropdown_carr)
        mod_but_callback = partial(self.on_modulator_source_click, dropdown=self.dropdown_mod)
        self.carrier_source_button.bind(on_release=carr_but_callback)
        self.modulator_source_button.bind(on_release=mod_but_callback)
        self.dropdown_carr.bind(on_select=lambda instance, x: setattr(self.carrier_source_button, 'text', x))
        self.dropdown_mod.bind(on_select=lambda instance, y: setattr(self.modulator_source_button, 'text', y))

    def on_carrier_source_click(self, *args, **kwargs):

        ''' Called when carrier source button is clicked. 2 cases are handled:
        1. Within live mode droplists of available inputs (created in fill_sources_droplists function) is opened
        2. Within live mode pop up window with filedialog is opened '''

        if self.mode == MODE.file:
            content = LoadDialog(load=self.save_carrier_file_path, cancel=self.dismiss_popup)
            self._load_file_popup = Popup(title="Load file", content=content,
                                size_hint=(0.9, 0.9))
            self._load_file_popup.open()
        elif self.mode == MODE.live:
            kwargs['dropdown'].open(args[0])

    def on_modulator_source_click(self, *args, **kwargs):
        ''' Called when modulator source button is clicked. 2 cases are handled:
        1. Within live mode droplists of available inputs (created in fill_sources_droplists function) is opened
        2. Within live mode pop up window with filedialog is opened '''

        if self.mode == MODE.file:
            content = LoadDialog(load=self.save_modulator_file_path, cancel=self.dismiss_popup)
            self._load_file_popup = Popup(title="Load file", content=content,
                                size_hint=(0.9, 0.9))
            self._load_file_popup.open()
        elif self.mode == MODE.live:
            kwargs['dropdown'].open(args[0])

    def save_carrier_file_path(self, path, filename):

        '''Called when carrier file in pop up file dialog is selected. Saves file path to object field '''

        self.carrier_file_path = filename[0]
        self.dismiss_popup()

    def save_modulator_file_path(self, path, filename):

        '''Called when modulator file in pop up file dialog is selected. Saves file path to object field '''

        self.modulator_file_path = filename[0]
        self.dismiss_popup()

    def dismiss_popup(self):

        '''Called when file dialog needs to be closed'''

        self._load_file_popup.dismiss()

    def change_mode(self, *args):

        ''' Called when file/live button is clicked '''
        if self.mode == MODE.live:
            self.mode = MODE.file
            args[0].text = 'File'
            self.carrier_source_button.text = 'choose file'
            self.modulator_source_button.text = 'choose file'
        else:
            self.mode = MODE.live
            args[0].text = 'Live'
            self.carrier_source_button.text = 'choose input'
            self.modulator_source_button.text = 'choose input'

    def on_play(self):
        pass

    def on_stop(self):
        pass

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class VocoderApp(App):

    def build(self):
        return VocoderView()

vocoderApp = VocoderApp()
vocoderApp.run()
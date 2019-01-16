import kivy
import Controller
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.base import runTouchApp

class VocoderView(GridLayout):

    # kivy objects references
    input_devices_button = kivy.properties.ObjectProperty(None)
    output_devices_button = kivy.properties.ObjectProperty(None)
    carrier_source_button = kivy.properties.ObjectProperty(None)
    modulator_source_button = kivy.properties.ObjectProperty(None)

    input_devices = None
    output_devices = None
    input_device_index = None
    output_device_index = None

    def __init__(self, **kwargs):
        super(VocoderView, self).__init__(**kwargs)
        self.controller = Controller.Controller()
        self.fill_input_devices_list()
        self.fill_output_devices_list()

    def fill_input_devices_list(self):
        self.input_devices = self.controller.get_input_devices()
        dropdown = DropDown()
        for key in self.input_devices.keys():
            device = self.input_devices[key]
            btn = Button(text=device['name'], size_hint_y=None, height=35, font_size=11)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        self.input_devices_button.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(self.input_devices_button, 'text', x))
        dropdown.bind(on_select=lambda instance, x: self.set_input_device_index(x))

    def fill_output_devices_list(self):
        self.output_devices = self.controller.get_output_devices()
        dropdown = DropDown()
        for key in self.output_devices:
            device = self.output_devices[key]
            btn = Button(text=device['name'], size_hint_y=None, height=35, font_size=11)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        self.output_devices_button.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(self.output_devices_button, 'text', x))
        dropdown.bind(on_select=lambda instance, x: self.set_output_device_index(x))

    def set_input_device_index(self, name):
        for idx, val in self.input_devices.items():
            if val['name'] == name:
                self.input_device_index = idx
                self.fill_sources_droplists(val['max'])

    def set_output_device_index(self, name):
        for idx, val in self.output_devices.items():
            if val['name'] == name:
                self.output_device_index = idx

    def fill_sources_droplists(self, max):
        dropdown_carr = DropDown()
        dropdown_mod = DropDown()
        for i in range(0, max):
            text_inp = 'Input %d' % i
            btn_carr = Button(text=text_inp, size_hint_y=None, height=35, font_size=11)
            btn_mod = Button(text=text_inp, size_hint_y=None, height=35, font_size=11)
            btn_carr.bind(on_release=lambda btn: dropdown_carr.select(btn_carr.text))
            btn_mod.bind(on_release=lambda btn: dropdown_mod.select(btn_mod.text))
            dropdown_carr.add_widget(btn_carr)
            dropdown_mod.add_widget(btn_mod)
        self.carrier_source_button.bind(on_release=dropdown_carr.open)
        self.modulator_source_button.bind(on_release=dropdown_mod.open)
        dropdown_carr.bind(on_select=lambda instance, x: setattr(self.carrier_source_button, 'text', x))
        dropdown_mod.bind(on_select=lambda instance, x: setattr(self.modulator_source_button, 'text', x))

class VocoderApp(App):

    def build(self):
        return VocoderView()

vocoderApp = VocoderApp()
vocoderApp.run()
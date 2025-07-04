import os
from gpiozero import Device
from gpiozero import DigitalOutputDevice
from gpiozero.pins.rpigpio import RPiGPIOFactory
import time

Device.pin_factory = RPiGPIOFactory()
class GpiosManager():
    def __init__(self):
        super().__init__()
        self.relay_1 = DigitalOutputDevice(20)
        self.relay_2 = DigitalOutputDevice(21)
        self.relay_3 = DigitalOutputDevice(16)
        self.relay_4 = DigitalOutputDevice(12)
        # declaracion de salidas
        self.relay_1.on()
        self.relay_2.on()
        self.relay_3.on()
        self.relay_4.on()


    def turnstileOpen(self):
        self.relay_1.off()
        self.relay_2.off()
        time.sleep(0.5)
        self.relay_1.on()
        self.relay_2.on()
        return "puerta general abierta"

    def armDown(self):
        self.relay_3.off()
        self.relay_4.off()
        time.sleep(0.5)
        self.relay_3.on()
        self.relay_4.on()
        return "puerta especial abierta"

# class GpiosManager():
#     def __init__(self):
#         super().__init__()
#         self.relay_1 = 1
#         self.relay_2 = 2
#         self.relay_3 = 3
#         self.relay_4 = 4
   

#     def turnstileOpen(self):

#         return "puerta general abierta"

#     def armDown(self):
#         return "puerta especial abierta"




from microbit import *
import radio

def print(*args, **kwargs):
    pass # disable print, now UART is in use
    
class MIDI():
    NOTE_ON  = 0x90
    NOTE_OFF = 0x80
    CHAN_MSG = 0xB0
    CHAN_BANK = 0x00
    CHAN_VOLUME = 0x07
    CHAN_PROGRAM = 0xC0

    uart.init(baudrate=31250, bits=8, parity=None, stop=1, tx=pin0)

    @staticmethod
    def send(b0, b1, b2=None):
        if b2 is None: m = bytes([b0,b1])
        else: m = bytes([b0,b1,b2])
        uart.write(m)

    def __init__(self, channel=0, velocity=0x7F):
        self.channel = channel
        self.velocity = velocity

    def set_instrument(self, instrument):
        instrument -= 1
        if instrument<0 or instrument>0x7F: return
        self.send(self.CHAN_PROGRAM|self.channel, instrument)

    def note_on(self, note, velocity=None):
        if note<0 or note>0x7F:return
        if velocity is None: velocity=self.velocity
        if velocity<0 or velocity>0x7F: velocity=0x7F
        self.send(self.NOTE_ON|self.channel, note, velocity)

    def note_off(self, note, velocity=0x7F):
        if note<0 or note>0x7F:return
        if velocity is None: velocity=self.velocity
        if velocity<0 or velocity>0x7F: velocity=0x7F
        self.send(self.NOTE_OFF|self.channel, note, velocity)

def get_message():
    while True:
        try:
            msg = radio.receive_bytes()
            if msg is not None:
                if len(msg) >= 13 and msg[3] == 2:
                    lstr = msg[12] # length byte
                    text = str(msg[13:13+lstr], 'ascii')
                    return text

        except Exception as e: # reset radio on error
            radio.off()
            radio.on()

midi = MIDI()

radio.config(channel=7, address=0x75626974, group=0, data_rate=radio.RATE_1MBIT)
radio.on()
display.show(Image.DIAMOND_SMALL)

while True:
    msg = get_message()

    # any message, just trigger a midi on/off
    display.show(Image.DIAMOND)
    midi.note_on(40)
    sleep(50)
    midi.note_off(40)
    display.show(Image.DIAMOND_SMALL)

from serial import Serial


class GpsReceiver:

    DEFAULT_BAUD = 9600
    DEFAULT_DEVICE = '/dev/ttyACM0'
    DEFAULT_RECORDED_SENTENCES = ['$GPGGA',]

    def __init__(self, ser: Serial = None):
        if ser is None:
            ser = Serial(self.DEFAULT_DEVICE, self.DEFAULT_BAUD,
                         timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
        self.ser = ser

    def next_message(self):
        bytes = self.ser.readline()

        return bytes

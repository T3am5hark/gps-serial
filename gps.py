from serial import Serial


def parse_msg(bytes):
    # Convert to string, strip carriage return chars
    msg = bytes.decode('utf-8').replace('/r/n', '')
    fields = msg.split(',', 1000)
    return msg, fields

def latlong_to_decimal_degrees(str):
    major = float(str[0:2])
    minutes = float(str[2:])

    decimal_degrees = major + minutes/60.0
    return decimal_degrees


class Message_GPGGA:

    def __init__(self, fields):
        if fields[0] != '$GPGGA':
            raise ValueError('Not a $GPGGA message')

    @classmethod
    def from_bytes(cls, bytes):
        msg, fields = parse_msg(bytes)
        return Message_GPGGA(fields)


class GpsReceiver:

    DEFAULT_BAUD = 2000000
    DEFAULT_DEVICE = '/dev/ttyACM0'
    DEFAULT_RECORDED_SENTENCES = ['$GPGGA',]

    def __init__(self, ser: Serial=None):
        if ser is None:
            ser = Serial(self.DEFAULT_DEVICE, self.DEFAULT_BAUD,
                         timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
        self.ser = ser

    def next_message(self):
        bytes = self.ser.readline()
        msg, fields = parse_msg(bytes)

        return msg, fields



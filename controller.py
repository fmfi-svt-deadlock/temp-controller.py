#!/usr/bin/env python

import sys
import logging
from binascii import hexlify
import serial
from gatereader.reader import Reader, PacketId
from mfrc522.mfrc522 import MFRC522, NoTagError, TransmissionError
from mfrc522.iso14443com import *
from textaccess import access_init, is_cleared

logger = logging.getLogger('controller')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
ch.setFormatter(formatter)

logger.addHandler(ch)

class SPIWrapper:
    def __init__(self, reader):
        self.reader = reader

    def transfer(self, data):
        return self.reader.RFID_send(data)

    def hard_powerdown(self):
        # TODO
        pass

    def reset(self):
        # TODO
        pass

def main(device='/dev/ttyUSB0'):
    reader = Reader(device)
    module = MFRC522(SPIWrapper(reader))

    last_uid = None

    while True:
        if are_cards_in_field(module):
            reader.set_leds(1 << Reader.Leds.BLUE_LED.value)

            try:
                uid = get_id(module)
                if uid is not None and last_uid != uid:
                    number = int.from_bytes(uid, byteorder='little')
                    logger.info(
                        'Card detected: '
                        + ' '.join('{:02x}'.format(x) for x in uid)
                        + ' -- '
                        + str(number)
                    )
                    if is_cleared(number):
                        logger.info('Access granted for ' + str(number))
                        reader.beep([(900, 600)])
                    else:
                        logger.warn('Access denied for ' + str(number))
                        reader.beep([(220, 80), (0, 80)]*3)
                    last_uid = uid
            except NoTagError:
                reader.set_leds(0)
                last_uid = None
        else:
            reader.set_leds(0)

if __name__ == '__main__':
    access_init()
    logger.info('Access controller initialized')
    while True:
        try:
            logger.info('Controller launch!')
            main(*sys.argv[1:])
        except KeyboardInterrupt:
            logger.info('Controller shutdown.')
            break
        except serial.SerialException:
            logger.exception('Unable to open serial port!')
            break
        except:
            logger.exception('Unexpected exception!')
            pass

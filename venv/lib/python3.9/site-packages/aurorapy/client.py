# -*- coding: utf-8 -*-
from __future__ import absolute_import
from past.builtins import map
from serial.serialutil import SerialException
import socket
import select
import struct
import binascii
import logging
import sys
import serial
import math

from .mapping import Mapping
from .defaults import Defaults

logger = logging.getLogger('aurorapy')
logger.setLevel(logging.WARNING)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARNING)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False

class AuroraError(Exception):
    pass

class AuroraBaseClient(object):
    """
    Implements the command functions of Aurora Protocol without
    specifies the communication channel.

    The Aurora inverters protocol uses a fixed length request message with 8 Bytes
    of data and 2 Bytes for CRC (calculated with CRC CCITT X.25),
    and a fixed length response message with 6 Bytes of data and 2 Bytes for CRC.

    Structure and example of request message:
         -------------------------------------------------------------
        | address | Command | 6 various purpose bytes | CRC_L | CRC_H |
        |---------|---------|-------------------------|-------|-------|
        |   0x0F  |  0x32   |    unused(all 0)        |  0xaC |  0xE0 |
         -------------------------------------------------------------

    Structure and example or response message:
         -------------------------------------------------------------
        | Tr. State | Glob.State |    4 Data Bytes    | CRC_L | CRC_H |
        |-----------|------------|--------------------|-------|-------|
        |    0x00   |    0x08    |     0x03020210     |  0xC2 |  0x83 |
         -------------------------------------------------------------

    Tr.state = Transmission state
    Glob.state = Global state

    In some command Tr.state and Glob.state bytes are replaced by 2 other data bytes.
    """
    def __init__(self, address):
        self.address = address

    def send_and_recv(self, request):
        raise NotImplemented

    def crc(self, buf):
        """
        Calcs the crc with CRC polynomial algorithm standardized by CCITT

        Arguments:
            _bytes: The bytearray on which calc the crc. [bytearray]
        Returns:
            The crc. [bytearray]
        """
        POLY = 0x8408
        MASK = 0xffff
        BIT = 0x0001

        crc = 0xffff

        if len(buf) == 0:
            return ~crc & MASK

        for data in buf:
            for i in range(8):
                if ((crc & BIT) ^ (data & BIT)):
                    crc = ((crc >> 1) ^ POLY) & MASK
                else:
                    crc >>= 1
                data >>= 1

        crc = ~crc & MASK
        crc = struct.pack('<H', crc)
        return bytearray(crc)

    def check_crc(self, response):
        """
        Checks if the crc of a response is correct otherwise raise
        an AuroraError.

        Arguments:
            - response: The response to check. [bytearray]
        """
        if response[6:8] != self.crc(response[0:6]):
            raise AuroraError('Response has a wrong CRC')

    def check_transmission_state(self, response):
        """
        Checks if the transmission state byte is 0 (OK) otherwise
        raise an AuroraError.

        Arguments:
            - response: The response to check. [bytearray]
        """
        ts = response[0]
        if ts == 0:
            return
        elif ts in Mapping.TRANSMISSION_STATES:
            raise AuroraError(Mapping.TRANSMISSION_STATES[ts])
        else:
            raise AuroraError('Unknown transmission state')

    def reset_auto_exclusion(self):
        """
        Sends a reset auto-exclusion command. (command: 53).
        """
        request = bytearray([self.address, 53, 10, 201, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

    def state(self, state_type, mapped=True):
        """
        Sends a state request (command: 50).

        Arguments:
            - state_type: The type of state that the function must return.
                          See Mapping.STATE_TYPES const. [int]
        Returns:
            The state description [string]
        """
        # [ address, command_num, *unused_bytes ]
        request = bytearray([self.address, 50, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        if not mapped:
            return response[state_type]

        states = []
        states.append(Mapping.GLOBAL_STATES.get(response[1], 'N/A'))
        states.append(Mapping.INVERTER_STATES.get(response[2], 'N/A'))
        states.append(Mapping.DCDC_STATES.get(response[3], 'N/A'))
        states.append(Mapping.DCDC_STATES.get(response[4], 'N/A'))
        states.append(Mapping.ALARM_STATES.get(response[5], 'N/A'))

        return states[state_type - 1]

    def pn(self):
        """
        Sends a P/N reading request (command: 52).

        Returns:
            P/N [string]
        """
        # [ address, command_num, *unused_bytes ]
        request = bytearray([self.address, 52, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)

        return response[0:6].decode('ascii')

    def version(self):
        """
        Sends a Version reading request (command: 58).
        available only for FW version 1.0.9 and following.

        Returns:
            Version of the inverter. [string]
        """
        # [ address, command_num, *unused_bytes ]
        request = bytearray([self.address, 58, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        res = response[2:6].decode('ascii')
        return (' - '.join(map(lambda i, x: Mapping.VERSION_PARAMETERS[i].get(x, 'N/A'), [0, 1, 2, 3], res)))

    def measure(self, index, global_measure=False):
        """
        Sends a Measure request to the DSP. (command: 59)

        Arguments:
            - index: Index of the measure. (see the manual) [int]
            - global_measure: if True the function returns the global measurement (Only for master)
                              otherwise returns the module measurement (Master and Slave) [bool]
        Returns:
            - The measurement with the stadard unit of measure (V/W/a/C°). [float]
        """
        global_measure = 1 if global_measure else 0

        # [ address, command_num, index, global_measure, *unused_bytes ]
        request = bytearray([self.address, 59, index, global_measure, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)
        self.check_crc(response)
        self.check_transmission_state(response)

        return struct.unpack('>f', response[2:6])[0]

    def joules_in_last_10s(self):
        """
        Sends a request to get latest 10 seconds produced Joules [Ws]. (command: 76)

        Returns:
            - The measurement in Joules [Ws] , updated every 10 seconds. [float]
        """
        request = bytearray([self.address, 76, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        return struct.unpack('>f', response[2:3])[0]

    def serial_number(self):
        """
        Sends a Serial Number reading request. (command: 63)

        Returns:
            The serial number. [string]
        """
        request = bytearray([self.address, 63, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)

        return response[0:6].decode('ascii')

    def manufacturing_date(self):
        """
        Sends a Manufacturing Week and Year reading. (command: 65)

        Returns:
            Manufacturing date in format "%Y-W%W". [string]
        """
        request = bytearray([self.address, 65, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        week = response[2:4].decode('ascii')
        year = response[4:6].decode('ascii')

        date_str = "%s-W%s" % (year, week)

        return date_str

    def flags_and_switches(self):
        """
        Sends a Flags or Switch reading request. (command: 67)
        Only for Aurora Central.

        Returns:
            4 bytes those represent the state of the flag1, flag2, switch1 and
            switch2 respectively. [bytearray]
        """
        request = bytearray([self.address, 67, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        return response[2:6]

    def cumulated_float_energy(self, period, ndays=None, global_measure=False):
        """
        Sends a Cumulated Float Energy Reading request. (command: 68)
        Only for Aurora Central

        Arguments:
            - period: Period of cumulated energy. (see the manual for the available periods)
                      For ex. 2 => 'Current week energy'. [int]
            - ndays: To specify only if period is 5 => 'Last Ndays day Energy' represents the
                     number of days of period. (Max 366) [int]
            - global_measure: if True the function returns the global measurement (Only for master)
                               otherwise returns the module measurement (Master and Slave) [bool]
        Returns:
            The cumulated energy. [float]
        """
        request = bytearray([self.address, 68, period])

        if ndays:
            request += bytearray(struct.pack('>H', ndays))
        else:
            request += bytearray([0, 0])

        global_measure = 1 if global_measure else 0
        request.append(global_measure)

        # Unused bytes
        request += bytearray([0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        return struct.unpack('>f', response[2:6])[0]

    def time_date(self):
        """
        Sends a Time/Date reading request. (command: 70)

        Returns:
            the number of past seconds since midnight of January 1, 2000. [int]
        """
        request = bytearray([self.address, 70, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        seconds = (response[2] * 2**24 + response[3] * 2**16 +
                   response[4] * 2**8 + response[5])

        return seconds

    def firmware(self, mrelease):
        """
        Sends a Firmware release reading request. (command: 72)

        Arguments:
            - mrelease: microcontroller release number. (1=a,2=B,...) [int]

        Returns:
            Firmware release [string]
        """
        request = bytearray([self.address, 72, mrelease, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        return '.'.join(response[2:6].decode('ascii'))

    def cumulated_energy(self, period):
        """
        Sends a Cumulated Energy Reading request. (command: 78)
        Only for Grid-Tied Inverter

        Arguments:
            - period: Period of cumulated energy. (see the manual for the available periods)
                      For ex. 1 => 'Current week energy'. [int]
        Returns:
            The cumulated energy. [int]
        """
        request = bytearray([self.address, 78, period, 0, 0, 0, 0, 0])

        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        a = response[2:6]

        value = a[0] * math.pow(2, 24) + a[1] * math.pow(2, 16) + a[2] * math.pow(2, 8) + a[3]
        return value

    def alarms(self):
        """
        Sends an alarm reading request. (command: 86)

        Returns:
            - list of the last 4 alarms [list of strings]
        """
        request = bytearray([self.address, 86, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        return list(map(lambda x: Mapping.ALARM_STATES.get(x, None), response[2:6]))

    def sysinfo(self, index):
        """
        Sends a System info reading request. (command: 101)
        Only for Aurora Central.

        Arguments:
            - index: index of system info (1 -> transformer_type, 2-> 50kW modules number) [int]

        Returns:
            - value of system info requested [int]
        """
        if index not in [1, 2]:
            raise AuroraError("Index not supported")

        request = bytearray([self.address, 101, index, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        if index == 1:
            return Mapping.TRANSFORMER_TYPES.get(response[2], 'N/A')
        else:
            return response[2]

    def junction_box_monitoring_status(self):
        """
        Sends a Junction Box monitoring status request (command: 103)
        Returns:
            - None if the module is not managing junction boxes, otherwise
              returns 2 bytes that represents the active junction box.

              Example:
                &0x0124 -> 0000000100100100
                junction boxes 8, 11, 14 are active.
        """
        request = bytearray([self.address, 103, 0, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)
        if response[1] == 0:
            return None
        else:
            return response[4:6]
        return response

    def junction_box_param(self, junction_box, parameter):
        """
        Sends a Junction Box Val Request. (command: 201)

        Arguments:
            - junction_box: Number of Junction Box to read. [int]
            - parameter: Number of parameter to read. [int]

        Returns:
            - value of requested junction parameter [float]
        """
        request = bytearray([self.address, 201, junction_box, parameter, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        return struct.unpack('>f', response[2:6])[0]

    def junction_box_state(self, junction_box, mapped=True):
        """
        Sends a Junction Box State Request. (command: 200)

        Arguments:
            - junction_box: Number of Junction Box to read. [int]

        Returns:
            - A string that describes the current state. [string]
        """
        request = bytearray([self.address, 200, junction_box, 0, 0, 0, 0, 0])
        request += self.crc(request)

        response = self.send_and_recv(request)

        self.check_crc(response)
        self.check_transmission_state(response)

        state = response[1]
        if not mapped:
            return state

        n_bits = 8

        # Splits the state byte in 8 bits.
        bits = [(state >> bit) & 1 for bit in range(n_bits - 1, -1, -1)]
        state = ""
        for pos, bit in enumerate(bits):
            if bit:
                if state:
                    state += "\n"
                state += Mapping.JBOX_STATE[pos]

        if not state:
            state = "OK"

        return state

class AuroraSerialClient(AuroraBaseClient):
    """
    Implementation of Aurora Power-One inverters protocol over serial line.

    Arguments:
        - address: Serial line address of the inverter. [int]
        - port: Serial port. [string]
        - baudrate: Baudrate of the serial line. [int]
        - parity: Parity of the serial line. ('E'/'O'/'N') [char]
        - stop_bits: Stop bits of the serial line. [int]
        - data_bits: Data bits of the serial line. [int]
        (for parity, stop_bits and data_bits, serial module has some constants.)
    """

    def __init__(self, address, port, baudrate=Defaults.BAUDRATE,
                 parity=Defaults.PARITY, stop_bits=Defaults.STOP_BITS,
                 data_bits=Defaults.DATA_BITS, timeout=Defaults.TIMEOUT, tries=Defaults.TRIES):

        self.serline = serial.Serial(timeout=timeout)
        self.serline.port = port
        self.serline.baudrate = baudrate
        self.serline.parity = parity
        self.serline.stop_bits = stop_bits
        self.serline.data_bits = data_bits
        self.timeout = timeout
        self.tries = tries
        self.address = address

    def connect(self):
        try:
            self.serline.open()
        except SerialException as e:
            raise AuroraError(str(e))

    def close(self):
        try:
            self.serline.close()
        except SerialException as e:
            raise AuroraError(str(e))

    def send_and_recv(self, request):
        """
        Sends a request message and waits for the response.

        Arguments:
            request: Request message. [bytearray]

        Returns:
            Response message [bytearray]
        """
        if not self.serline.isOpen():
            raise AuroraError("Serial line closed")

        self.serline.flushInput()
        self.serline.flushOutput()

        response = b''
        tries = self.tries
        self.serline.write(request)

        while(len(response) < 8 and tries >= 0):
            tries = tries - 1
            try:
                response += self.serline.readline(8 - len(response))
            except SerialException as e:
                self.serline.close()
                raise AuroraError(str(e))

        if tries == -1 and len(response) < 8:
            raise AuroraError('No response after %d tries' % self.tries)

        return bytearray(response)

class AuroraTCPClient(AuroraBaseClient):
    """
    Implementation of Aurora Power-One inverters protocol over TCP
    with the serial line converted to Ethernet.

    Arguments:
        - ip: IP address of the inverter/ethernet-converter.
        - port: TCP Port of the inverter/ethernet-converter.
        - address: Serial line address of the inverter.
    """

    def __init__(self, ip, port, address, timeout=Defaults.TIMEOUT):
        self.ip = ip
        self.port = port
        self.address = address
        self.timeout = timeout
        self.s = None

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.ip, self.port))
        except socket.error as e:
            self.s = None
            raise AuroraError(str(e))

    def close(self):
        self.s.close()

    def send_and_recv(self, request):
        """
        Sends a request message and waits for the response.

        Arguments:
            request: Request message. [bytearray]

        Returns:
            Response message [bytearray]
        """
        if not self.s:
            raise AuroraError("You must connect client before launch a command")

        try:
            # Empty the socket buffer before send request and receive response
            # this is made to prevent receipt of noise in the response packet.
            ready = select.select([self.s], [], [], 0.1)
            if ready[0]:
                noise = self.s.recv(4096)
                logger.warning('Found noises on the socket buffer: %s' % (binascii.hexlify(noise)))

            self.s.send(request)
            self.s.setblocking(0)
            response = b''
            while(len(response) < 8):
                ready = select.select([self.s], [], [], self.timeout)
                if ready[0]:
                    response += self.s.recv(1024)
                else:
                    raise AuroraError("Reading Timeout")
        except socket.error as e:
            raise AuroraError("Socket Error: " + str(e))

        return bytearray(response)

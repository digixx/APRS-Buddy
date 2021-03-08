# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

'''
Class for generating array containing APRS data to be send
'''
import array
# import aprs_crc

class APRS():

    ccitt_table = (
       0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
       0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
       0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
       0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
       0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
       0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
       0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
       0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
       0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
       0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
       0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
       0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
       0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
       0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
       0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
       0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
       0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
       0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
       0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
       0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
       0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
       0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
       0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
       0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
       0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
       0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
       0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
       0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
       0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
       0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
       0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
       0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78)

    INITIAL_CRC16_VALUE = 0xffff    # The initial value of the crc register
    CRC16CCITT_POLYNOMIAL = 0x8408  # CRC Polynomial used for AX.25 FCS

    AX25_APRS_UI_FRAME = 0x03       # Frame Type
    AX25_PROTO_NO_LAYER3 = 0xf0     # Layer 3 protocol

    def __init__(self, source = 'NOCALL-0', destination = 'APZDIY-12', digipeaters = 'WIDE1-1', information = '>NoText'):
        self.source = source
        self.destination = destination
        self.digipeaters = digipeaters
        self.information = information
        self._debugging = False

        '''
        AX25 - Control field
        This field indicates that the packet is an unnumbered information (UI)
        frame, the default for APRS.
        '''
        self._ax25_control_field = [self.AX25_APRS_UI_FRAME]

        '''
        AX25 - Protocol ID
        This field indicates that there is no layer 3 (network layer) implementation,
        as is standard for APRS.
        '''
        self._ax25_protocol_id = [self.AX25_PROTO_NO_LAYER3]

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, destination):
        self._destination = destination
        self._ax25_destination = self._set_ax25_destination(self._destination)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source
        self._ax25_source = self._set_ax25_source(self._source)

    @property
    def digipeaters(self):
        return self._digipeaters

    @digipeaters.setter
    def digipeaters(self, digipeaters):
        self._digipeaters = digipeaters[:56]
        self._ax25_digipeaters = self._set_ax25_digipeaters(self._digipeaters)

    @property
    def information(self):
        return self._information

    @information.setter
    def information(self, information):
        self._information = information
        self._ax25_information_field = self._set_ax25_information(self._information)

    def debugging(self, mode):
        self._debugging = mode

    def create_ax25_frame(self):
        ax25_frame = []
        ax25_frame += self._ax25_destination
        ax25_frame += self._ax25_source
        ax25_frame += self._ax25_digipeaters
        ax25_frame += self._ax25_control_field
        ax25_frame += self._ax25_protocol_id
        ax25_frame += self._ax25_information_field
        self._ax25_fcs = self._calc_crc(ax25_frame)
        ax25_frame.append(self._get_crc_low_byte(self._ax25_fcs))
        ax25_frame.append(self._get_crc_high_byte(self._ax25_fcs))

        if self._debugging == True:
            print("\n\nAPRS: AX25 packet data")
            print("APRS: Dest:", self.destination)
            print("APRS: Src :", self.source)
            print("APRS: Digi:", self.digipeaters)
            print("APRS: CTRL:", self._ax25_control_field)
            print("APRS: PrID:", self._ax25_protocol_id)
            print("APRS: Info:", self.information)
            print("APRS: Len :", len(self._ax25_information_field))
            print("APRS: CRC :", self._ax25_fcs)

        return ax25_frame

    '''
    *AX25 - Source address
    Byte 1-6:   source address, left shifted one bit
    Byte 7:     SSID byte format, 0bCRRSSID0
                where C is the command/response bit (1 for APRS), RR is 11, SSID is the SSID value,
                from 0-15, and the LSB is 0. For this example, this gives 0b11100000 = 0xE0
    '''
    def _set_ax25_source(self, source):
        name, ssid = self._split_address_ssid(source)
        n = bytearray(name + '      ')[:6]
        s = int(ssid) & 0x0F
        ax25_source = self._shift_1bit_left(n)
        ax25_source += [0xe0 | (s << 1)]
        return ax25_source

    '''
    *AX25 - Destination
    Byte 1-6:   destination address, left shifted one bit
    Byte 7:     SSID byte format, 0bCRRSSID0
                where C is the command/response bit (1 for APRS), RR is 11, SSID is the SSID value,
                from 0-15, and the LSB is 0. For this example, this gives 0b11100000 = 0xE0
    '''
    def _set_ax25_destination(self, destination):
        name, ssid = self._split_address_ssid(destination)
        n = bytearray(name + '      ')[:6]
        s = int(ssid) & 0x0F
        ax25_dest = self._shift_1bit_left(n)
        ax25_dest += [0xf0 | (s << 1)]
        return ax25_dest


    '''
    *AX25 - Digipeater addresses
    This field is a list of the digipeater addresses (call signs) or indicates a generic path for
    the packet to follow. In this example, the generic path WIDE1-1 is used, meaning it will be
    repeated in one “hop”, with each digipeater decrementing the SSID until it reaches -0.
    The first digipeater(s) to hear this packet will retransmit it once more for other stations
    or IGates to receive. The last address in this field must end with an LSB of 1 to indicate
    the end of the address fields.
    '''
    def _set_ax25_digipeaters(self, digipeaters):
        ax25_digi = []
        digilist = digipeaters.split(',')
        if digilist != ['']:
            for address in digilist:
                name, ssid = self._split_address_ssid(address)
                n = bytearray(name + '      ')[:6]
                s = int(ssid) & 0x0F
                ax25_digi += self._shift_1bit_left(n)
                ax25_digi += [0xe0 | (s << 1)]
        # set last address bit
        ax25_digi[-1] = ax25_digi[-1] | 1
        return ax25_digi

    '''
    This field contains the information the user
    wants to send, following one of the ten main types of data as defined in the APRS specification.
    '''
    def _set_ax25_information(self, information):
        info = bytearray(information)
        ax25_info = []
        for j in info:
            ax25_info.append(j)
        return ax25_info

    def _shift_1bit_left(self, s):
        r = []
        for i in s:
            r.append(i << 1)
        return r

    def _split_address_ssid(self, fulladdr):
        addrparts = fulladdr.split('-')
        if len(addrparts) > 1:
            return addrparts[0], addrparts[1]
        else:
            return addrparts[0], 0

    '''
    AX25 - Frame Check Sequence
    This field contains a Cyclic Redundancy Check (CRC) of
    all bytes in the packet except the flags and the FCS itself. The CRC follows the 16-bit CRC-CCITT
    format, with a polynomial of 0x8408. The FCS is sent low-byte first.
    The FCS is a sequence of 16 bits used for checking the integrity of a received frame.
    '''

    def _calc_crc(self, frame):
       crc = self.INITIAL_CRC16_VALUE
       for j in frame:
          crc = (crc >> 8) ^ self.ccitt_table[(crc ^ j) & 0xff]
       crc = crc ^ self.INITIAL_CRC16_VALUE
       return crc

    def _get_crc_high_byte(self, n):
       return (n >> 8) & 0x00FF

    def _get_crc_low_byte(self, n):
       return n & 0x00FF


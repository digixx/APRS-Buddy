# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

'''
Class for generating array containing APRS data to be send
'''
import array
import aprs_crc

class APRS():

    AX25_APRS_UI_FRAME = 0x03       # Frame Type
    AX25_PROTO_NO_LAYER3 = 0xf0     # Layer 3 protocol

    def __init__(self, source = 'NOCALL-0', destination = 'APNMDM', digipeaters = 'WIDE1-1', information = '>NoText'):
        self.source = source
        self.destination = destination
        self.digipeaters = digipeaters
        self.information = information
        self.debug = False

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

    @property
    def get_ax25_frame(self):
        ax25_frame = []
        ax25_frame += self._ax25_destination
        ax25_frame += self._ax25_source
        ax25_frame += self._ax25_digipeaters
        ax25_frame += self._ax25_control_field
        ax25_frame += self._ax25_protocol_id
        ax25_frame += self._ax25_information_field
        self._ax25_fcs = crc.calc_crc(ax25_frame)
        ax25_frame.append(crc.get_crc_low_byte(self._ax25_fcs))
        ax25_frame.append(crc.get_crc_high_byte(self._ax25_fcs))

        if self.debug == True:
            print("\n\n// *** AX25 Packet ***")
            print("// Dest:", self.destination)
            print("// Src :", self.source)
            print("// Digi:", self.digipeaters)
            print("// CTRL:", self._ax25_control_field)
            print("// PrID:", self._ax25_protocol_id)
            print("// Info:", self.information)
            print("// Len :", len(self._ax25_information_field))
            print("// CRC :", self._ax25_fcs)

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
        s = int(ssid) & 0x07
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
        s = int(ssid) & 0x07
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
                s = int(ssid) & 0x07
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

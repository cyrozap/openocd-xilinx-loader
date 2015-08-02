#!/usr/bin/env python3
#
# Copyright (C) 2015  Forest Crossman <cyrozap@gmail.com>
#
# This file is part of openocd-xilinx-loader.
#
# openocd-xilinx-loader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# openocd-xilinx-loader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with openocd-xilinx-loader.  If not, see <http://www.gnu.org/licenses/>.

import binascii
import struct
import sys

from openocd import OpenOcd
import xilinx.utilities

read_status_reg_commands = [
    0xFFFF,
    0xAA99,
    0x5566,
    0x2000,
    0x2901,
    0x2000,
    0x2000,
    0x2000,
    0x2000,
]

def print_status(status):
    print('SWWD_strikeout\t', 1 if (status & (1 << 15)) else 0)
    print('IN_PWRDN\t', 1 if (status & (1 << 14)) else 0)
    print('DONE\t\t', 1 if (status & (1 << 13)) else 0)
    print('INIT_B\t\t', 1 if (status & (1 << 12)) else 0)
    print('MODE\t\t', (status & ((1 << 11) | (1 << 10) | (1 << 9))) >> 9)
    print('HSWAPEN\t\t', 1 if (status & (1 << 8)) else 0)
    print('PART_SECURED\t', 1 if (status & (1 << 7)) else 0)
    print('DEC_ERROR\t', 1 if (status & (1 << 6)) else 0)
    print('GHIGH_B\t\t', 1 if (status & (1 << 5)) else 0)
    print('GWE\t\t', 1 if (status & (1 << 4)) else 0)
    print('GTS_CFG_B\t', 1 if (status & (1 << 3)) else 0)
    print('DCM_LOCK\t', 1 if (status & (1 << 2)) else 0)
    print('ID_ERROR\t', 1 if (status & (1 << 1)) else 0)
    print('CRC_ERROR\t', 1 if (status & (1 << 0)) else 0)

if __name__ == "__main__":
    tap = input("Tap name [xc6slx100.tap]: ") or 'xc6slx100.tap'
    drscan_command = 'drscan %s' % tap

    with OpenOcd(verbose=False) as ocd:
        # CFG_IN
        ocd.send('irscan %s 0x05' % tap)
        command = drscan_command
        for word in read_status_reg_commands:
            command += ' 16 0x%04X' % xilinx.utilities.flip_bits(word, 16)
        ocd.send(command)

        # CFG_OUT
        ocd.send('irscan %s 0x04' % tap)
        response = ocd.send(drscan_command + ' 16 0x0000')
        response_bytes = binascii.a2b_hex(response)
        response_int = (response_bytes[0] << 8) | response_bytes[1]
        status = xilinx.utilities.flip_bits(response_int, 16)

        print("0x%04X" % status)
        print_status(status)

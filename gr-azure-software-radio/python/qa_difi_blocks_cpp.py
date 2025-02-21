#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Microsoft Corporation.
# Licensed under the GNU General Public License v3.0 or later.
# See License.txt in the project root for license information.
#

from gnuradio import gr, gr_unittest, blocks
from multiprocessing import Process
import pytest
import socket
import struct
import math
import time
import random
import numpy as np
from azure_software_radio import (difi_source_cpp_fc32, difi_source_cpp_sc8, difi_sink_cpp_fc32, difi_sink_cpp_sc8,
                                 DATA_PACKET_METADATA_FORMAT, VITA_PKT_MOD, CONTEX_ALT_PACK_STRUCT_FORMAT, DIFI_HEADER_SIZE)



SAMPS_PER_PACKET = 1344 // 2

class qa_testcpp(gr_unittest.TestCase):

    def setUp(self):
        self.vita_data = b'\x18\xe6\x01W\x00\x00\x00\x00\x00|8l\x00\x00\x00\x00`X\xec\xac\x00\x00\x00\xe5\xd0\xda\xa1' \
                         b'\xe0\xd0\xdc\xd5\xe1\xf6\x00\n*\xff@\x01)"\xfb\x1a\xdd\xdf\xe7\xd4\x12\x12,)\x08\x00\xd3\xf8\xe5 \x19+\x12' \
                         b'\x16\xe1\x1c\xe2*\x1a\x14A\x00*\x05\xef\xfa\xd3\xd5\xee\xd8\x10\x10\x16-\x1e\x121\xf3!\xe5\xf1\xd6\xd3\xd6\xe1' \
                         b'\xfb\x02$\x1a.\x16*\xfa(\xe0\x17\xdf\xef\xf7\xcb\x0c\xc8\x0c\xe0\xfc\xf8\xe4\xf9\xc9\xf6\xc8\x0c\xf4$\x1e\x12\r\xde' \
                         b'\xe4\xc3\xe8\xd9\x0c\x04\x1a%\x171\x1d\x1e \x01!\x072\x13<\xf2\x16\xd3\xe6\xfa\xef)\x1c\x06' \
                         b'\x1f\xd1\x02\xec\xfe2\x00G\xf1#\xfd\x02*\x0b)"\xf1\x0c\xd7\xda\xf9\xdd\x17\x16\x181' \
                         b'\x1f\r/\xe3,\xe4 \x05$#\x1e(\xf9\x19\xd6\x05\xd1\xf4\xdc\xe3\xee\xcf\x15' \
                         b'\xd0/\xfe\r$\xdd\x04\xee\xde!\x05%2\xfe\n\xdf\xd6\xe5\xfa\xff:\xfb9\xd9\x08' \
                         b'\xe4\xe6\x1f\xf0\x1f\x13\xe1\x19\xe3\xf0#\xcf%\xd4\xfd\xe7\x13\xff5 \x0b\x1f' \
                         b'\xd5\xef\xdc\xd8\xeb\xf7\xd8\xfc\xd4\xd5\xf5\xda\x13\x15\x1a1\x1c!\x1e"\x1c+' \
                         b'\x1a\n!\xe1%\xdf!\xe8 \xdf,\xe6"\x11\xfe5\xfb2\x1e\x13\x17\xfc\xde\x02\xcd\x18' \
                         b'\xe4\x1b\xd8\x01\xca\xe6\xf9\xe5(\xfe\x0c\x1c\xd9(\xd1\x19\xe2\x00\xe4\xfd\xd0' \
                         b'\x12\xc7\x1f\xf5\x120\xf3\x1e\xdf\xe3\xe3\xf4\xff1\x1b\x1d\x1b\xd9\x01\xd1\xdd' \
                         b'\xef\xcb\xf4\xd6\x03\xe8)\xe2 \xd1\xea\xed\xe7\x1e\x15\x1b \xe1\x06\xc2\x08' \
                         b'\xdf#\n&\x1f\x1a\x1d \x070\xf32\x07*,#\x19\x19\xdc\x0c\xda\x00\x19\xfa<\x02(\x17' \
                         b'\x18%!\x1e-\r,\xff&\xf5+\xfa;\t)\xfc\xef\xda\xd8\xec\xfe+\x0b$\xf2\xdc\x05\xd8-\x18' \
                         b'\x0b%\xce\x02\xe7\x08)!/\x11%\xf87\xfa+\xfd\xf0\xf0\xdc\xe2\x10\xe9?\n3%\x07\x0b\xe4' \
                         b'\xe4\xdc\xf4\xe3"\xe5\x1a\xdf\xe5\xe2\xc9\xfe\xd8#\xf3,\xfa\x10\xe7\xf3\xd0\xe6\xd3\xdb' \
                         b'\xf7\xd8\x1c\xf9"\'\x08+\xe5\x02\xd6\xde\xe2\xd5\x02\xdd!\xe4$\xdd\x0e\xd1\x03\xd1\x0b\xd9' \
                         b'\xff\xe8\xdc\n\xd8&\x05\x164\xec/\xdd\xfe\xf5\xd8\x17\xe4$\x19\x15>\x02+\x00\xf3\xfc' \
                         b'\xd1\xe6\xda\xda\xe9\xe2\xe7\xdc\xe3\xd4\xe7\xf0\xe1\x19\xdb\x16\xef\xec\x1c\xcf9\xe1&\x0c' \
                         b'\xf6\x1d\xde\xff\xfc\xdf*\xe14\xe6\x18\xd6\x04\xd5\x0e\xf8$\x19*&\x0f/\xe0\'\xd4\xfd\x06' \
                         b'\xdf*\xfb\x00#\xd7"\xfb\x1e)0\x1f\x1c\x18\xe4-\xe8\x18\x1d\xe5\x11\xdf\xd5\x01\xdd\x06\x1a' \
                         b'\xe6-\xc9\x1a\xd9\x10\x13\x053\xe9\x12\xd1\x00\xd1$\xec \x03\xde\xf3\xd5\xdd' \
                         b'\x17\xf9,)\x01 \xeb\xe7\xec\xcf\xd8\xf8\xcf+\xf7"!\xe6\x1c\xd3\xff\x0e' \
                         b'\xf22\x05\x06\x1f\xcc\x1f\xc8\x0b\xe9\x06\x01 \x02=\x015\x17\x0b.\xf9\x1e' \
                         b'\x1a\x00/\x08\x06$\xd7,\xe1&\r\x1a(\xf7+\xda%\xf6"#!\x13\x13\xd9\x04\xc1\x06' \
                         b'\xd6\x06\xee\xef\xf9\xd2\xf6\xd3\xdd\xea\xc3\x00\xe1\x03 \xfc*\x02\xf8\x19' \
                         b'\xd2.\xdc\'\xfc\x0c\x18\xe7%\xcd\x1d\xdb\x0c\x0f\x05/\x12\x1a0\xf6@\xf2\x1d' \
                         b'\x04\xe2\n\xd6\xfb\x03\xe73\xdd8\xf0\x13\x18\x001\x1b\x1c1\xfa\x07\xf3\xd7' \
                         b'\xe8\xe7\xca\x06\xd7\x00\x1a\x040!\xf7\x15\xd0\xe3\xe4\xe0\xe9\x13' \
                         b'\xd62\xea,\x07\x1b\xe9\x01\xcc\xde\xf3\xd2\r\xea\xe0\x01\xd1\x02' \
                         b'\x13\x064\x16\xfd \xca\x1f\xd6\x1d\xf6\x1f\x11!-\x0e2\xe0\x19\xcd' \
                         b'\x05\xfd\x08)\x1d\x121\xfc.\x1b\x19%\x1f\x038\x04 %\xe5\n\xdf\xd2' \
                         b'\x03\xe6\x05*\xf73\x10\x03.\xe0\x1b\xe1\xe2\xef\xbb\xfd' \
                         b'\xdb\x06&\x04*\xfc\xdf\xf9\xd7\xf2\x1e\xd8!\xd0\xe1' \
                         b'\xfe\xec(%\t\r\xd9\xdb\xea\xfd\n6\xf72\xdc' \
                         b'\x1a\xe3 \xe5$\xd3\x10\xdb\xf8\x07\xe81\xd9-\xd6\xf7\xf1' \
                         b'\xd0\t\xf1\xf4!\xd9\t\xe6\xd7\xeb\xe3\xca\x07\xd5\x07\x1f\xfd-\x03\xe5' \
                         b'\xfd\xd2\xf5\x18\x15B,#\x02\x08\xd3\x08\xe9\x0b!\x19)0\xfe,\xde\t\xe3' \
                         b'\xde\xf7\xc7\xfa\xdc\xe4\x03\xcc\x00\xcf\xe0\xf6\xf0 \x1c#\x14' \
                         b'\x17\xe2(\xd84\xff\x10\x1f\xfd* ,#\x1d\xe3\x06\xd2\x04\x14\x087' \
                         b'\xf2\x10\xd3\xe6\xe2\xe2\x16\xeb3\xe7&\xd3\r\xcf\x03\xf3' \
                         b'\x15\x08/\xea2\xe0\x1a\r\xfb!\xd9\xf2\xcc\xd4\xf9\xf5/\x19\x1b' \
                         b'\x1c\xe1\x11\xeb\t)\x07:\x1c\x1c:\x07-\x00\xf5\xf3\xda\xe1\xf5' \
                         b'\xd2\xff\xd7\xe3\xe6\xdf\xe1\xfb\xcf\xf9\xe0\xd7\x03\xdc\x00' \
                         b'\x13\xdf=\xdf.\x00\xfe\x17\xe5!\xfb#\'\x1d5\x1a' \
                         b'\x17!\xfd*\x0e,($\r\x17\xd8\x08\xdd\xf9\x16\xe34\xd3' \
                         b'\x1d\xdf\x03\x05\x06-\x199\x1e\x18\x01\xe9\xd2\xe6\xc3\x02' \
                         b'\xe8\xff\x13\xdf\x1d\xea\x0b"\x01<\x18":\x043\x01\xf9\r\xde!\x0b-%\x1a' \
                         b'\xf8\xf4\xd5\xde\xef\xda\x08\xd0\xfc\xcc\xfe\xe8\x1e\x14/%)\x08\x1e\xda' \
                         b'\x03\xd2\xde\xfe\xe2&\x13\x19/\xf5\x15\xe1\xf3\xd2\xf6\xca\x06\xe3\x04' \
                         b'\x18\xfb=\xec2\xd6\xff\xd5\xdd\x01\xff$$\x14\x01\xfa\xcb\x05\xd6$\xe8+\xd3' \
                         b'\x12\xe3\xf1$\xe0\x1c\xec\xd4\x10\xdd%"\x14\x12\xfb\xce\n\xdd/\t1\xec\x17\xd7' \
                         b'\x00\r\xe1)\xc9\xf6\xea\xdd#\x0e\x16(\xda\n\xdd\xfb\x1f\x037\xf4\x07\xd7\xd5' \
                         b'\xd1\xdc\xe4\x14\xf4-\xfd\x02\x03\xcb\x05\xc5\x04\xdc\xff\xe1\xf1\xdb\xda\xdd' \
                         b'\xd7\xe5\xfa\xe5 \xdc\x18\xda\xeb\xf9\xce \xdd$\x07\x1d /\x12,\xf9\xfa\xee\xd2' \
                         b'\xe2\xdc\xd4\xe9\xf2\xef(\x18+:\x01\x0b\xf8\xce\t\xef\xfe2\xf7)\x1c\xf82\xea\t\xe3' \
                         b'\xda\xce\xd9\xe9\xec%\xf7\'\x01\xea\x07\xc2\xfd\xd3\xe9\xf8\xd8\x02\xd3\xe8\xdb\xdb' \
                         b'\xe5\x02\xe2#\xdf\x02\xe3\xd5\xe4\xda\xdf\xe5\xe7\xd4\xff\xd2\x02\xe3\xea\xdb\xe1\xcd' \
                         b'\xfb\xeb\x17\x1c\x1c.\x0c \xe8\x07\xbf\xfb\xd2\x06\x1d\x06.\xf1\xec\x01\xd0,\x07\x14*'


    def tearDown(self):
        pass
    
    def test_vita_source_sink_full_loop(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        vita_source = difi_source_cpp_fc32('127.0.0.1', source_p, 0, 2048, 8)
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, True, SAMPS_PER_PACKET, 0, 352, int(1e6), 0, 0, 100, 72, 8)
        tb.connect(vita_source, vita_sink)

        send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), self.vita_data))
        rec_proc = Process(target=socket_rec, args=(('127.0.0.1', sink_p), self.vita_data))
        tb_proc = Process(target=run_tb, args=(tb,))
        tb_proc.start()
        rec_proc.start()
        send_proc.start()
        send_proc.join()
        rec_proc.join()
        tb_proc.kill()
        if rec_proc.exitcode != 0:
            pytest.fail()
            
    def test_timing_basic(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        vita_source = difi_source_cpp_fc32('127.0.0.1', source_p, 0, 2048, 8)
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, True, SAMPS_PER_PACKET, 0, 352, int(1e6), 0, 0, 100, 108, 8)
        tb.connect(vita_source, vita_sink)
        vita_data_time_change = bytearray(self.vita_data)
        full = b'\x00\x00\x00\x00'
        frac = full + full
        vita_data_time_change[16:20] = bytearray(full)
        vita_data_time_change[20:28] = bytearray(frac)
        
        # first msg
        send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), vita_data_time_change))
        socket_rec_time= Process(target=socket_rec_confirm_time, args=(('127.0.0.1', sink_p), 0, 0))
        tb_proc = Process(target=run_tb, args=(tb,))
        tb_proc.start()
        socket_rec_time.start()
        send_proc.start()
        send_proc.join()
        socket_rec_time.join()
        if socket_rec_time.exitcode != 0:
            tb_proc.kill()
            pytest.fail()

        # second msg
        vita_data_time_change[1] = (vita_data_time_change[1] & 0xf0) | 7 # update packet count
        send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), vita_data_time_change))
        socket_rec_time= Process(target=socket_rec_confirm_time, args=(('127.0.0.1', sink_p), 1344000000 // 2, 0))
        socket_rec_time.start()
        send_proc.start()
        send_proc.join()
        socket_rec_time.join()
        tb_proc.kill()
        if socket_rec_time.exitcode != 0:
            pytest.fail()

    def test_time_full_and_frac(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        vita_source = difi_source_cpp_fc32('127.0.0.1', source_p, 0, 2048, 8)
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, True, SAMPS_PER_PACKET, 0, 352, int(1e6), 0, 0, 100, 108, 8)
        tb.connect(vita_source, vita_sink)
        tb_proc = Process(target=run_tb, args=(tb,))
        vita_data_time_change = bytearray(self.vita_data)
        full = b'\x00\x00\x00\x00'
        frac = full + full
        vita_data_time_change[16:20] = bytearray(full)
        vita_data_time_change[20:28] = bytearray(frac)
        frac_base = 1344000000 // 2
        to_one = math.ceil(1e12 / frac_base)
        tb_proc.start()
        time.sleep(1)
        base_pkt_n = 6
        rec_proc = Process(target=rec_socket_multi_packet, args=(('127.0.0.1', sink_p), to_one, frac_base))
        rec_proc.start()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i in range(to_one + 1):
            vita_data_time_change[1] = (vita_data_time_change[1] & 0xf0) | base_pkt_n
            time.sleep(.002)
            sock.sendto(vita_data_time_change, ('127.0.0.1', source_p))
            base_pkt_n = (base_pkt_n + 1) % VITA_PKT_MOD
        rec_proc.join()
        sock.close()
        tb_proc.kill()
        if rec_proc.exitcode != 0:
            pytest.fail()

    # test case were partial buffer is filled
    def test_missed_pack_partial_buffer(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        vita_source = difi_source_cpp_fc32('127.0.0.1', source_p, 0, 2048, 8)
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, False, SAMPS_PER_PACKET, 0, 352, int(1e6), 0, 0, 100, 108, 8)
        # keep one in two to test partial buffer
        keep_1_n = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, 2)
        tb.connect(vita_source, keep_1_n)
        tb.connect(keep_1_n, vita_sink)
        vita_data_time_change = bytearray(self.vita_data)
        full = b'\x00\x18\x18\x18'
        frac = full + full
        vita_data_time_change[16:20] = bytearray(full)
        vita_data_time_change[20:28] = bytearray(frac)
        # first msg
        send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), vita_data_time_change))
        tb_proc = Process(target=run_tb, args=(tb,))
        tb_proc.start()
        send_proc.start()
        send_proc.join()
        # zero out time
        full = b'\x00\x00\x00\x00'
        frac = full + full
        vita_data_time_change[16:20] = bytearray(full)
        vita_data_time_change[20:28] = bytearray(frac)
        # second msg
        vita_data_time_change[1] = (vita_data_time_change[1] & 0xf0) | 3 # send out of order packet
        send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), vita_data_time_change))
        # confirm time was zeroed out when out of order packet came in
        socket_rec_time= Process(target=socket_rec_confirm_time, args=(('127.0.0.1', sink_p), 0, 0))
        socket_rec_time.start()
        # need to send 2 to get 1 since keeping 1 in 2
        send_proc.start()
        send_proc.join()

        vita_data_time_change[1] = (vita_data_time_change[1] & 0xf0) | 4
        send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), vita_data_time_change))
        send_proc.start()
        send_proc.join()
        socket_rec_time.join()
        tb_proc.kill()
        if socket_rec_time.exitcode != 0:
            pytest.fail()
    
    
    def test_multi_packet_correct(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        vita_source = difi_source_cpp_fc32('127.0.0.1', source_p, 0, 2048, 8)
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, True, SAMPS_PER_PACKET, 0, 352, int(1e6), 0, 0, 100, 108, 8)
        tb.connect(vita_source, vita_sink)
        tb_proc = Process(target=run_tb, args=(tb,))
        vita_data = bytearray(self.vita_data)
        tb_proc.start()
        base_pkt_n = 6
        for i in range(VITA_PKT_MOD + 1):
            vita_data[1] = (vita_data[1] & 0xf0) | base_pkt_n
            send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), vita_data))
            socket_rec_test = Process(target=socket_rec, 
                                     args=(('127.0.0.1', sink_p), vita_data))

            socket_rec_test.start()
            send_proc.start()
            send_proc.join()
            socket_rec_test.join()
            if socket_rec_test.exitcode != 0:
                tb_proc.kill()
                pytest.fail()
            base_pkt_n = (base_pkt_n + 1) % VITA_PKT_MOD
            random.randint(29, 1371)
            vita_data[random.randint(29, 1371)] = random.randint(0, 255)
        tb_proc.kill()

    def test_multi_packet_correct_sc8(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        vita_source = difi_source_cpp_sc8('127.0.0.1', source_p, 0, 2048, 8)
        vita_sink = difi_sink_cpp_sc8(0, 0, '127.0.0.1', sink_p, True, SAMPS_PER_PACKET, 0, 352, int(1e6), 0, 0, 100, 108, 8)
        tb.connect(vita_source, vita_sink)
        tb_proc = Process(target=run_tb, args=(tb,))
        vita_data = bytearray(self.vita_data)
        tb_proc.start()
        base_pkt_n = 6
        for i in range(VITA_PKT_MOD + 1):
            vita_data[1] = (vita_data[1] & 0xf0) | base_pkt_n
            send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), vita_data))
            socket_rec_test = Process(target=socket_rec, 
                                     args=(('127.0.0.1', sink_p), vita_data))

            socket_rec_test.start()
            send_proc.start()
            send_proc.join()
            socket_rec_test.join()
            if socket_rec_test.exitcode != 0:
                tb_proc.kill()
                pytest.fail()
            base_pkt_n = (base_pkt_n + 1) % VITA_PKT_MOD
            random.randint(29, 1371)
            vita_data[random.randint(29, 1371)] = random.randint(0, 255)
        tb_proc.kill()

    # standalone mode tests
    def test_standalone_context(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        samp_rate = int(1e6)
        oui = 0xf
        packet_class_id = 1
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, False, SAMPS_PER_PACKET, 0, 352, 
                            int(1e6), packet_class_id, oui, 100, 72, 8)
        vector_source = blocks.vector_source_c((0, 0) * 512, False, 1, [])
        tb.connect(vector_source, vita_sink)
        tb_proc = Process(target=run_tb, args=(tb,))
        socket_rec_test = Process(target=socket_rec_confirm_context_correct_alt, 
                            args=(('127.0.0.1', sink_p), 
                            samp_rate, packet_class_id, oui, 8))
        socket_rec_test.start()
        time.sleep(1)
        tb_proc.start()
        socket_rec_test.join()
        if socket_rec_test.exitcode != 0:
            tb_proc.kill()
            pytest.fail()
    
    def test_standalone_data(self):
        _, sink_p = get_open_ports()
        tb = gr.top_block()
        samp_rate = int(1e6)
        oui = 0xf
        packet_class_id = 1
        add_const = blocks.add_const_cc(1)
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, False, 1024 // 2, 0, 352, 
                            int(1e6), packet_class_id, oui, 100, 72, 8)
        vector_source = blocks.vector_source_c((0, 0) * 512, False, 1, [])
        tb.connect(vector_source, add_const)
        tb.connect(add_const, vita_sink)
        tb_proc = Process(target=run_tb, args=(tb,))
        socket_rec_test = Process(target=socket_rec_confirm_standalone_data, 
                            args=(('127.0.0.1', sink_p), 1024 // 2))
        socket_rec_test.start()
        time.sleep(1)
        tb_proc.start()
        socket_rec_test.join()
        if socket_rec_test.exitcode != 0:
            tb_proc.kill()
            pytest.fail()
    
    def test_16_bit_depth_full_loop(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        vita_source = difi_source_cpp_fc32('127.0.0.1', source_p, 0, 2048, 16)
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, True, 1344 // 4, 0, 352, int(1e6), 0, 0, 100, 72, 16)
        tb.connect(vita_source, vita_sink)

        send_proc = Process(target=socket_send, args=(('127.0.0.1', source_p), self.vita_data))
        rec_proc = Process(target=socket_rec, args=(('127.0.0.1', sink_p), self.vita_data))
        tb_proc = Process(target=run_tb, args=(tb,))
        tb_proc.start()
        rec_proc.start()
        send_proc.start()
        send_proc.join()
        rec_proc.join()
        tb_proc.kill()
        if rec_proc.exitcode != 0:
            pytest.fail()

    def test_standalone_16_bit_data_basic(self):
        _, sink_p = get_open_ports()
        tb = gr.top_block()
        samp_rate = int(1e6)
        oui = 0xf
        packet_class_id = 1
        add_const = blocks.add_const_cc(1)
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, False, 512, 0, 352, 
                            int(1e6), packet_class_id, oui, 100, 72, 16)
        vector_source = blocks.vector_source_c((0, 0) * 512, False, 1, [])
        tb.connect(vector_source, add_const)
        tb.connect(add_const, vita_sink)
        tb_proc = Process(target=run_tb, args=(tb,))
        socket_rec_test = Process(target=socket_rec_confirm_standalone_data_16, 
                            args=(('127.0.0.1', sink_p), 512))
        socket_rec_test.start()
        time.sleep(1)
        tb_proc.start()
        socket_rec_test.join()
        if socket_rec_test.exitcode != 0:
            tb_proc.kill()
            pytest.fail()
    
    def test_standalone_16_bit_data_random_vec(self):
        _, sink_p = get_open_ports()
        tb = gr.top_block()
        oui = 0xf
        packet_class_id = 1
        ran_vec = list(np.random.choice([complex(x,x) for x in range(-32767, 32767)], size=(512)))
        expected = []
        for i in ran_vec:
            re = int(i.real)
            im = int(i.imag)
            re = re.to_bytes(2, 'little', signed=True)
            im = im.to_bytes(2, 'little', signed=True)
            expected.append(re[0])
            expected.append(re[1])
            expected.append(im[0])
            expected.append(im[1])     
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, False, 512, 0, 352, 
                            int(1e6), packet_class_id, oui, 100, 72, 16)
        vector_source = blocks.vector_source_c(ran_vec, False, 1, [])
        tb.connect(vector_source, vita_sink)
        tb_proc = Process(target=run_tb, args=(tb,))
        socket_rec_test = Process(target=socket_rec_confirm_standalone_data_16_vec, 
                            args=(('127.0.0.1', sink_p), expected))
        socket_rec_test.start()
        time.sleep(1)
        tb_proc.start()
        socket_rec_test.join()
        if socket_rec_test.exitcode != 0:
            tb_proc.kill()
            pytest.fail()

    def test_standalone_context_16(self):
        source_p, sink_p = get_open_ports()
        tb = gr.top_block()
        samp_rate = int(1e6)
        oui = 0xf
        packet_class_id = 1
        vita_sink = difi_sink_cpp_fc32(0, 0, '127.0.0.1', sink_p, False, SAMPS_PER_PACKET, 0, 352, 
                            int(1e6), packet_class_id, oui, 100, 72, 16)
        vector_source = blocks.vector_source_c((0, 0) * 512, False, 1, [])
        tb.connect(vector_source, vita_sink)
        tb_proc = Process(target=run_tb, args=(tb,))
        socket_rec_test = Process(target=socket_rec_confirm_context_correct_alt, 
                            args=(('127.0.0.1', sink_p), 
                            samp_rate, packet_class_id, oui, 16))
        socket_rec_test.start()
        time.sleep(1)
        tb_proc.start()
        socket_rec_test.join()
        if socket_rec_test.exitcode != 0:
            tb_proc.kill()
            pytest.fail()

def socket_rec_confirm_standalone_data(server, size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server)
    data = sock.recv(2048) #ignore context
    data = sock.recv(2048) 
    sock.close()
    samples = struct.unpack_from('!%sb' % (len(data) - DIFI_HEADER_SIZE), data, offset=DIFI_HEADER_SIZE)
    expected = (1, 0) * size
    assert samples == expected

def socket_rec_confirm_standalone_data_16(server, size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server)
    data = sock.recv(4096) #ignore context
    data = sock.recv(4096) 
    sock.close()
    samples = struct.unpack_from('!%sb' % (len(data) - DIFI_HEADER_SIZE), data, offset=DIFI_HEADER_SIZE)
    expected = (1, 0, 0, 0) * size
    assert samples == expected

def socket_rec_confirm_standalone_data_16_vec(server, vec):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server)
    data = sock.recv(4096) #ignore context
    data = sock.recv(4096) 
    sock.close()
    assert list(data[28::]) == vec

def socket_rec_confirm_context_correct_alt(server, sample_rate, packet_class_id, oui, expect_bit_depth):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server)
    data = sock.recv(2048)
    sock.close()
    payload = struct.unpack_from(CONTEX_ALT_PACK_STRUCT_FORMAT, data, offset=8)
    r_samp_rate = parse_vita_double(payload[6])
    r_bw = parse_vita_double(payload[2])
    class_id = payload[0]
    r_oui = class_id >> 32
    r_packet_class_id = class_id & 0x000000000000ff
    bit_depth = payload[-1] >> 32 & 0x0000001f
    assert bit_depth + 1 == expect_bit_depth # bit depth is one plus value in data format see DIFI spec.
    assert sample_rate == r_samp_rate
    assert int(sample_rate *.8) == r_bw
    assert r_oui == oui
    assert r_packet_class_id == packet_class_id

def socket_rec_pack_n(server, pkt_n, vita_source):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server)
    data = sock.recv(2048)
    sock.close()
    pack_type, r_pkt_n, stream_num, header, _, _ = vita_source.parse_header(data)
    assert r_pkt_n == pkt_n

def socket_rec(server, vita_data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server)
    data = sock.recv(2048)
    sock.close()
    assert len(data) == 1372
    assert data[28::] == vita_data[28::]

def socket_rec_confirm_time(server, frac, full):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server)
    data = sock.recv(2048)
    sock.close()
    payload = struct.unpack(DATA_PACKET_METADATA_FORMAT, data[0:28])
    r_full = payload[3]
    r_frac = payload[4]
    assert math.isclose(frac, r_frac, rel_tol = 1e-11, abs_tol=2)
    assert full == r_full


def socket_send(server, data):
    time.sleep(.05)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, server)
    sock.close()

def get_open_ports():
    sock1 = socket.socket()
    sock1.bind(('', 0))
    sock2 = socket.socket()
    sock2.bind(('', 0))    
    return sock1.getsockname()[1], sock2.getsockname()[1]

def rec_socket_multi_packet(server, num_packets, frac_base):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server)
    for i in range(num_packets + 1):
        frac, full = (i * frac_base) % 1e12, 0 if i < num_packets else 1
        data = sock.recv(2048)
        try:
            payload = struct.unpack(DATA_PACKET_METADATA_FORMAT, data[0:28])
            r_full = payload[3]
            r_frac = payload[4]
            assert math.isclose(frac, r_frac, rel_tol = 1e-11, abs_tol=2)
            assert full == r_full
        except Exception as e:
            sock.close()
            raise e
def parse_vita_double(bits):
    int_part = bits >> 20
    frac_part = bits & 0xfffff
    power = 43
    res = 0
    mask = 0x1
    while power > -21:
        tmp = (0x1 << abs(power)) * ((int_part >> power if power > -1 else frac_part >> 20 - power) & mask)
        res += tmp if power > -1 else (1/tmp if tmp else 0)
        power -= 1
    return res
def run_tb(tb):
    tb.run()

if __name__ == '__main__':
    gr_unittest.run(qa_testcpp)

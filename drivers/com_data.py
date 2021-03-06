"""
串口数据收发
"""
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

sys.path.append(
    os.path.join(
        root_dir,
        'dataGetSend'))

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),
        'utils'))
import serial
from serial.tools import list_ports
import binascii
import time
import copy
from threading import Thread

from utils import log

logger = log.LogHandler('test_com')


class ComData:
    def __init__(self, com, baud, timeout, logger=None):
        if logger is None:
            import logging
            logging.basicConfig(
                format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                level=logging.DEBUG)
            self.logger = logging
        else:
            self.logger = logger
        self.port = com
        self.baud = baud
        self.timeout = timeout
        try:
            # 打开串口，并得到串口对象
            self.uart = serial.Serial(
                self.port, self.baud, timeout=self.timeout)
            # 判断是否打开成功
            if not self.uart.is_open:
                self.logger.error('无法打开串口')
        except Exception as e:
            self.logger.error({"串口连接异常：": e})

    # 打印设备基本信息
    def print_info(self):
        info_dict = {
            'name': self.uart.name,  # 设备名字
            'port': self.uart.port,  # 读或者写端口
            'baudrate': self.uart.baudrate,  # 波特率
            'bytesize': self.uart.bytesize,  # 字节大小
            'parity': self.uart.parity,  # 校验位
            'stopbits': self.uart.stopbits,  # 停止位
            'timeout': self.uart.timeout,  # 读超时设置
            'writeTimeout': self.uart.writeTimeout,  # 写超时
            'xonxoff': self.uart.xonxoff,  # 软件流控
            'rtscts': self.uart.rtscts,  # 软件流控
            'dsrdtr': self.uart.dsrdtr,  # 硬件流控
            'interCharTimeout': self.uart.interCharTimeout,  # 字符间隔超时
        }
        self.logger.info(info_dict)
        return info_dict

    # 打开串口
    def open_serial(self):
        self.uart.open()

    # 关闭串口
    def close_Engine(self):
        self.uart.close()
        print(self.uart.is_open)  # 检验串口是否打开

    # 打印可用串口列表
    @staticmethod
    def print_ssed_com():
        port_list = list(list_ports.comports())
        print(port_list)

    # 接收指定大小的数据
    # 从串口读size个字节。如果指定超时，则可能在超时后返回较少的字节；如果没有指定超时，则会一直等到收完指定的字节数。
    def read_size(self, size):
        return self.uart.read(size=size)

    # 接收一行数据
    # 使用readline()时应该注意：打开串口时应该指定超时，否则如果串口没有收到新行，则会一直等待。
    # 如果没有超时，readline会报异常。
    def readline(self):
        data_read = self.uart.readline()
        return data_read
        # if str(data_read).count(',') > 2:
        #     return str(data_read)[2:-5]
        # else:
        #     return data_read

    # 发数据
    def send_data(self, data, b_hex=False):
        print('com send_data', data)
        if b_hex:
            self.uart.write(bytes.fromhex(data))
        else:
            self.uart.write(data.encode())

    # 读取深度传感器数据
    def read_deep_data(self, data='010300000001840A', b_hex=True):
        # print('com send_data', data)
        if b_hex:
            self.uart.write(bytes.fromhex(data))
        time.sleep(0.1)  # 等待一段时间再去读数据
        data_read = self.uart.readline()
        str_data = str(binascii.b2a_hex(data_read))[2:-1]
        print('read_sonar str_data', str_data)
        distance = 0
        if str_data.startswith('0103'):
            distance = int(str_data[6:10], 16) / 100
            print('深度:', distance)
        # print(str_data.split('ff')[0][:4])
        if distance <= 0.73:
            return -1
        else:
            return distance

    # 更多示例
    # self.main_engine.write(chr(0x06).encode("utf-8"))  # 十六制发送一个数据
    # print(self.main_engine.read().hex())  #  # 十六进制的读取读一个字节
    # print(self.main_engine.read())#读一个字节
    # print(self.main_engine.read(10).decode("gbk"))#读十个字节
    # print(self.main_engine.readline().decode("gbk"))#读一行
    # print(self.main_engine.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
    # print(self.main_engine.in_waiting)#获取输入缓冲区的剩余字节数
    # print(self.main_engine.out_waiting)#获取输出缓冲区的字节数
    # print(self.main_engine.readall())#读取全部字符。

    # 接收数据
    # 一个整型数据占两个字节
    # 一个字符占一个字节

    def recive_data(self, way):
        # 循环接收数据，此为死循环，可用线程实现
        print("开始接收数据：")
        while True:
            try:
                # 一个字节一个字节的接收
                if self.uart.in_waiting:
                    if (way == 0):
                        for i in range(self.uart.in_waiting):
                            print("接收ascii数据：" + str(self.read_size(1)))
                            data1 = self.read_size(1).hex()  # 转为十六进制
                            data2 = int(
                                data1, 16)  # 转为十进制print("收到数据十六进制："+data1+"  收到数据十进制："+str(data2))
                    if (way == 1):
                        # 整体接收
                        # data =
                        # self.main_engine.read(self.main_engine.in_waiting).decode("utf-8")#方式一
                        data = self.uart.read_all()  # 方式二print("接收ascii数据：", data)
            except Exception as e:
                print("异常报错：", e)

    def get_laser_data(self):
        data = self.read_size(30)
        # print(time.time(), type(data), data)
        str_data = str(binascii.b2a_hex(data))[2:-1]
        # print(str_data)
        for i in str_data.split('aa'):
            if len(i) == 14 and i.startswith('55'):
                # print(i)
                distance = int(i[6:12], 16) / 1000
                return distance

    @staticmethod
    def split_lora_data(data: str) -> list:
        item_data = data[1:-1]
        item_data_list = item_data.split(',')
        if len(item_data_list) >= 13:
            try:
                left_row = int(item_data_list[1])
            except Exception as e1:
                left_row = 50
            try:
                left_col = int(item_data_list[0])
            except Exception as e0:
                left_col = 50
            try:
                right_row = int(item_data_list[3])
            except Exception as e3:
                right_row = 49
            try:
                right_col = int(item_data_list[2])
            except Exception as e2:
                right_col = 49
            try:
                fine_tuning = int(item_data_list[4])
            except Exception as e4:
                fine_tuning = 50
            try:
                button_10 = int(item_data_list[9])
            except Exception as e9:
                button_10 = -1
            try:
                button_11 = int(item_data_list[10])
            except Exception as e10:
                button_11 = -1
            try:
                button_12 = int(item_data_list[11])
            except Exception as e11:
                button_12 = -1
            try:
                button_13 = int(float(item_data_list[12]))
            except Exception as e12:
                button_13 = -1
            try:
                lever_6 = int(float(item_data_list[5]))
            except Exception as e5:
                lever_6 = -1
            try:
                lever_7 = int(item_data_list[6])
            except Exception as e6:
                lever_7 = -1
            try:
                lever_8 = int(item_data_list[7])
            except Exception as e7:
                lever_8 = -1
            try:
                lever_9 = int(item_data_list[8])
            except Exception as e8:
                lever_9 = -1
            try:
                remote_dumpenergy = float(item_data_list[13])
            except Exception as e13:
                remote_dumpenergy = 0
            try:
                draw_deep = float(item_data_list[14])
            except Exception as e14:
                draw_deep = -1
            try:
                draw_capacity = int(item_data_list[15])
            except Exception as e15:
                draw_capacity = -1

            return_list = [left_col,
                           left_row,
                           right_col,
                           right_row,
                           fine_tuning,
                           lever_6,
                           lever_7,
                           lever_8,
                           lever_9,
                           button_10,
                           button_11,
                           button_12,
                           button_13,
                           remote_dumpenergy,
                           draw_deep,
                           draw_capacity
                           ]
            return return_list
        else:
            return []

    def read_remote_control(self, debug=False, send_data='z00'):
        self.send_data('G1')
        lora_data = self.readline()
        str_lora_data = str(lora_data)
        if len(str_lora_data) < 10:
            return []
        str_lora_data.strip()
        str_lora_data = str_lora_data[2:-5]
        # print(time.time(), 'data', lora_data)
        if str_lora_data[0] == 'A' and str_lora_data[-1] == 'Z':
            return_list = ComData.split_lora_data(str_lora_data)
            # print('return_list',return_list)
            return return_list

    def read_deep(self):
        data = self.readline()
        print(time.time(), 'sonar count', data)
        str_data = str(binascii.b2a_hex(data))[2:-1]
        print('read_sonar str_data', str_data)
        # print(r'str_data.split', str_data.split('aa'))
        # print(r'str_data.split', int(str_data.split('ff')[0][:4], 16))
        distance = 0
        for i in str_data.split('aa'):
            if len(i) == 8:
                distance = int(str_data[4:8], 16) / 1000
                if distance == 0.275:
                    continue
                print('深度:', distance)
        # print(str_data.split('ff')[0][:4])
        if distance <= 0.25:
            return -1
        else:
            return distance


if __name__ == '__main__':
    import config

    b_ultrasonic = 0
    b_com_data = 0
    b_gps = 0
    b_laser = 0
    b_lora = 0
    b_deep = 0
    check_type = input('check_type: 1 compass  2 ultrasonic  3 com_data  4 gps  5 laser 6 lora 7 sonar deep>>')
    if int(check_type) == 1:
        b_compass = 1
    elif int(check_type) == 2:
        b_ultrasonic = 1
    elif int(check_type) == 3:
        b_com_data = 1
    elif int(check_type) == 4:
        b_gps = 1
    elif int(check_type) == 5:
        b_laser = 1
    elif int(check_type) == 6:
        b_lora = 1
    elif int(check_type) == 7:
        b_deep = 1
    if b_com_data:
        serial_obj = ComData(config.stc_port,
                             config.stc_baud,
                             timeout=0.7,
                             logger=logger)
        while True:
            print(serial_obj.readline())
            print(serial_obj.readline())
            print(serial_obj.readline())
            print(serial_obj.readline())
            key_input = input('input:')
            try:
                i = int(key_input)
                if i == 1:
                    serial_obj.send_data('A1Z')
                else:
                    serial_obj.send_data('A0Z')
            except Exception as e:
                print({'error': e})
    elif b_deep:
        serial_obj = ComData(config.deep_port,
                             config.deep_baud,
                             timeout=1,
                             logger=logger)
        # while True:
        #     print(serial_obj.read_deep())
        print(serial_obj.read_deep_data())
        # print(serial_obj.readline())
        # print(serial_obj.readline())
    elif b_ultrasonic:
        serial_obj = ComData('com3',
                             '9600',
                             timeout=0.7,
                             logger=logger)
        while True:
            data = serial_obj.read_size(4)
            # print(time.time(),type(data),data)
            str_data = str(binascii.b2a_hex(data))[2:-1]
            # print(str_data)
            print(int(str_data[2:-2], 16) / 1000)
    elif b_lora:
        lora_serial_obj = ComData('/dev/ttyUSB0',
                                  '9600',
                                  timeout=0.2,
                                  logger=logger)
        lora_serial_obj.read_remote_control()
    elif b_gps:
        serial_obj1 = ComData('com4',
                              115200,
                              timeout=1,
                              logger=logger)
        serial_obj2 = ComData('com7',
                              9600,
                              timeout=1,
                              logger=logger)
        while True:
            data1 = serial_obj1.readline()
            str_data1 = bytes(data1).decode('ascii')
            if str_data1.startswith('$GNGGA'):
                data_list1 = str_data1.split(',')
                print(data_list1)
                lng1, lat1 = float(data_list1[4][:3]) + float(data_list1[4][3:]) / 60, float(data_list1[2][:2]) + float(
                    data_list1[2][2:]) / 60
                print('经纬度1', lng1, lat1)
                print('误差1', data_list1[8])
            time.sleep(0.2)
            data2 = serial_obj2.readline()
            str_data2 = bytes(data2).decode('ascii')
            if str_data2.startswith('$GNGGA') or str_data2.startswith('$GPGGA'):
                data_list2 = str_data2.split(',')
                print(data_list2)
                lng2, lat2 = float(data_list2[4][:3]) + float(data_list2[4][3:]) / 60, float(data_list2[2][:2]) + float(
                    data_list2[2][2:]) / 60
                print('经纬度2', lng2, lat2)
                print('误差2', data_list2[8])
            time.sleep(0.2)
    elif b_laser:
        serial_obj_laser = ComData('com9',
                                   '115200',
                                   timeout=0.3,
                                   logger=logger)
        while True:
            # 控制到位置1 2 3 4 5获取距离
            distance1 = serial_obj_laser.get_laser_data()
            distance2 = serial_obj_laser.get_laser_data()
            distance3 = serial_obj_laser.get_laser_data()
            distance4 = serial_obj_laser.get_laser_data()
            distance5 = serial_obj_laser.get_laser_data()
            print('距离矩阵', distance1, distance2, distance3, distance4, distance5)
    # str_data = data.decode('ascii')[:-3]
    # # print('str_data',str_data,type(str_data))
    # if len(str_data)<2:
    #     continue
    # # str_data = str_data.encode('utf8')
    # # print(str_data.split('.'))
    # float_data = float(str_data)
    # print(time.time(),'float_data', float_data,type(float_data))
    # time.sleep(0.1)
    # t1 = Thread(target=get_com_data)
    # t2 = Thread(target=send_com_data)
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()
    # print(str(obj.Read_Line())[2:-5])

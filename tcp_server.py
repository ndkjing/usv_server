import re
import socket
import server_config
import json
import time
import requests
import threading


def singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@singleton
class TcpServer:
    def __init__(self):
        self.bind_ip = server_config.tcp_server_ip  # 监听所有可用的接口
        self.bind_port = server_config.tcp_server_port  # 非特权端口号都可以使用
        # AF_INET：使用标准的IPv4地址或主机名，SOCK_STREAM：说明这是一个TCP服务器
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 服务器监听的ip和端口号
        self.tcp_server_socket.bind((self.bind_ip, self.bind_port))
        print("[*] Listening on %s:%d" % (self.bind_ip, self.bind_port))
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # 最大连接数
        self.tcp_server_socket.listen(128)
        # 是否有链接上
        self.b_connect = 0
        self.client = None
        self.client_dict = {}  # {船号:client}
        self.ship_status_data_dict = {}  # 船状态数据
        self.ship_draw_dict = {}  # 船抽水状态数据
        self.ship_detect_data_dict = {}  # 船检测数据
        self.ship_obstacle_data_dict = {}  # 船检测数据
        self.receive_confirm_data = ""
        self.disconnect_client_list = []  # 断线了的船号

    def wait_connect(self):
        # 等待客户连接，连接成功后，将socket对象保存到client，将细节数据等保存到addr
        client, addr = self.tcp_server_socket.accept()
        print("客户端的ip地址和端口号为:", addr)
        self.b_connect = 1
        self.client = client

    def start_server(self):
        while True:
            # 等待客户连接，连接成功后，将socket对象保存到client，将细节数据等保存到addr
            client, addr = self.tcp_server_socket.accept()
            print(time.time(), "客户端的ip地址和端口号为:", addr)
            # 代码执行到此，说明客户端和服务端套接字建立连接成功
            client_handler = threading.Thread(target=self.handle_client, args=(client, addr))
            # 子线程守护主线程
            client_handler.setDaemon(True)
            client_handler.start()
            time.sleep(0.5)

    # 客户处理线程
    def handle_client(self, client, addr):
        addr_dict = {}
        while True:
            try:
                recv_data = client.recv(1024)
                if recv_data:
                    recv_content = recv_data.decode("gbk")
                    ship_id_list = re.findall('[ABCD](\d+)', recv_content)
                    if len(ship_id_list) > 0:
                        ship_id = int(ship_id_list[0])
                        if recv_content.startswith('A'):
                            rec_list = recv_content.split(',')
                            if len(rec_list) >= 6:
                                if ship_id not in self.client_dict:
                                    self.client_dict.update({ship_id: client})
                                if ship_id not in addr_dict:
                                    addr_dict.update({addr: ship_id})
                                if ship_id in self.disconnect_client_list:
                                    self.disconnect_client_list.remove(ship_id)
                                lng = float(rec_list[1]) / 1000000.0
                                lat = float(rec_list[2]) / 1000000.0
                                dump_energy = round(float(rec_list[3]), 1)
                                current_angle = round(float(rec_list[4]), 1)
                                current_mode = int(rec_list[5])
                                angle_error = int(rec_list[6])
                                speed = int(rec_list[7].split('Z')[0])
                                self.ship_status_data_dict.update(
                                    {ship_id: [lng, lat, dump_energy, current_angle, current_mode, angle_error, speed]})
                                # print(time.time(), "接收客户端的状态数据:", recv_content)
                                # print(self.client_dict, addr_dict)
                        if recv_content.startswith('B'):
                            rec_list = recv_content.split(',')
                            if len(rec_list) == 6:
                                wt = int(rec_list[1])
                                ph = int(rec_list[2])
                                doDo = int(rec_list[3])
                                ec = int(rec_list[4])
                                td = int(rec_list[5].split('Z')[0])
                                self.ship_detect_data_dict.update(
                                    {ship_id: [wt, ph, doDo, ec, td]})
                                print('深度数据反馈消息%s\r\n' % recv_content.strip())
                            elif len(rec_list) == 2:
                                deep = int(rec_list[1].split('Z')[0])
                                self.ship_detect_data_dict.update(
                                    {ship_id: [deep]})
                                print('检测数据反馈消息%s\r\n' % recv_content.strip())
                        if recv_content.startswith('C'):
                            rec_list = recv_content.split(',')
                            if len(rec_list) == 5:
                                bottle_id = int(rec_list[1])
                                draw_status = int(rec_list[2])
                                dump_draw_time = int(rec_list[3])
                                full_draw_time = int(rec_list[4].split('Z')[0])
                                self.ship_draw_dict.update(
                                    {ship_id: [bottle_id, draw_status, dump_draw_time, full_draw_time]})
                            # print('抽水反馈消息：%s\r\n' % recv_content.strip())
                        if recv_content.startswith('D'):
                            rec_list = recv_content.split(',')
                            if len(rec_list) >= 4:
                                obj_id = int(rec_list[1])
                                obj_angle = 2 * int(rec_list[2]) - 90
                                obj_distance = int(rec_list[3].split('Z')[0]) / 100.0
                                self.ship_obstacle_data_dict.update(
                                    {ship_id: {obj_id: [obj_angle, obj_distance]}})
                                # print('障碍物检测反馈消息', recv_content.strip())
                    else:
                        print(time.time(),'接收客户端的确认数据:%s\r\n' % recv_content.strip())
                        self.receive_confirm_data = recv_content.strip()
            except TimeoutError or WindowsError or 10054 as e:
                print(' WindowsError', e)
                time.sleep(5)
                return
            except Exception as e:
                print('tcp接受数据报错..', e)
                print(addr_dict, addr_dict.get(addr))
                if addr_dict.get(addr):
                    print('断开连接删除船只:%d\r\n' % addr_dict.get(addr))
                    if addr_dict.get(addr) not in self.disconnect_client_list:
                        self.disconnect_client_list.append(addr_dict.get(addr))
                    if addr_dict.get(addr) in self.client_dict:
                        del self.client_dict[addr_dict.get(addr)]
                time.sleep(5)
                return

    def close(self):
        self.tcp_server_socket.close()

    def write_data(self, ship_id, data):
        try:
            if ship_id in self.client_dict.keys():
                if data != 'S8Z':
                    print('tcp发送数据%s\r\n' % data)
                # print('tcp发送数据', data, self.client_dict)
                self.client_dict.get(ship_id).send(data.encode())
        # except ConnectionAbortedError or ConnectionResetError or ConnectionResetError as e:
        except Exception as e:
            del self.client_dict[ship_id]
            print('tcp发送收据报错..', e)


def te_():
    while True:
        for i in range(4):
            obj.write_data(i, str(i))
        time.sleep(1)


if __name__ == '__main__':
    obj = TcpServer()
    te_handler = threading.Thread(target=te_)
    # 子线程守护主线程
    te_handler.setDaemon(True)
    te_handler.start()
    obj.start_server()

"""
入口函数
"""
import threading
import time
import config
import tcp_server
from utils import log
from messageBus import data_manager

logger = log.LogHandler('main_log')


class Main:
    def __init__(self):
        self.tcp_server_obj = tcp_server.TcpServer()  # tcp发送数据对象
        self.damanager_dict = {}


def main():
    config.update_setting()
    main_obj = Main()
    start_server_thread = threading.Thread(target=main_obj.tcp_server_obj.start_server)
    start_server_thread.start()
    ship_thread_dict = {}
    while True:
        for ship_id in list(main_obj.tcp_server_obj.client_dict.keys()):
            if ship_id not in main_obj.damanager_dict:
                print('ship_id', ship_id)
                if 'XXLJC4LCGSCSD1DA00' + str(ship_id) not in config.ship_code_type_dict:
                    continue
                main_obj.damanager_dict[ship_id] = data_manager.DataManager(ship_id=ship_id,
                                                                            tcp_server_obj=main_obj.tcp_server_obj)
                ship_thread = threading.Thread(target=main_obj.damanager_dict[ship_id].thread_control)
                ship_thread.start()
                ship_thread_dict[ship_id] = ship_thread
        for ship_id in ship_thread_dict:
            if not ship_thread_dict.get(ship_id).is_alive():
                if ship_id in list(main_obj.damanager_dict.keys()):
                    print('删除船号对象', ship_id)
                    del main_obj.damanager_dict[ship_id]
        time.sleep(1)


if __name__ == '__main__':
    main()

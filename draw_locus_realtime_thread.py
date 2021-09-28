import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import os
import socket
import time
import threading
######读取标定H矩阵######
def getHomography(homography_path):
    global H_array = []
    for i, h_path in enumerate(homography_path):
        print("------",h_path)
        H_array.append(self.get_xy(h_path))
    print('Homography has been loaded!, Total: {}'.format(len(H_array)))
    return H_array    
######UDP接收数据######
class Plot_Realtime(threading.Thread):
    def __init__(self, H_array,ratio=1):
        threading.Thread.__init__(self)
        #self.board_path = board_path
        #self.homography_path = homography_path
        self.H_array = H_array
        self.ratio=ratio
    def run(self):    
        global locus
        # UDP 建立
        #建立IPv4,UDP的socket
        sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(len(self.H_array))]
        #绑定端口：
        for i, s in enumerate(sockets):
            s.bind(('192.168.3.8', 9990+i))
            s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                     
            s1.bind(('192.168.3.8', 9989-i))
        # 实时接收数据，并绘制轨迹
        while True:
            #接收来自客户端的数据,使用recvfrom
            for i, s in enumerate(sockets):
                t1=time.time()
                data, addr = s.recvfrom(1024)
                data1, addr = s1.recvfrom(1024)
                t2=time.time()
                #print("tttttttttttt:",t2-t1)
                #print("1111111",data)
                data=np.fromstring(data)
                data1=np.fromstring(data1)
                #print("99999999",data)
                #data_red, data_yellow = data[0], data[1]
                data_red = data.reshape(-1,5)
                data_yellow = data1.reshape(-1,5)
                red_locus_num, yellow_locus_num = 2*i, 2*i+1    #对应locus字典的编号
                for j, cord in enumerate(data_red):
                    x_world, y_world = self.get_world_xy(int((cord[0]+cord[2])/2), int((cord[1]+cord[3])/2), H_array[i])
                    print("x_world, y_world:",x_world, y_world)
                    if cord[4] not in locus[red_locus_num].keys():
                        locus[red_locus_num][int(cord[4])] = ([[x_world], [y_world]])
                    else:
                        locus[red_locus_num][int(cord[4])][0].append(x_world)
                        locus[red_locus_num][int(cord[4])][1].append(y_world)
                    print(cord[4])
                for j, cord in enumerate(data_yellow):
                    x_world, y_world = self.get_world_xy(int((cord[0]+cord[2])/2), int((cord[1]+cord[3])/2), H_array[i])
                    
                    if cord[4] not in locus[yellow_locus_num].keys():
                        locus[yellow_locus_num][int(cord[4])] = ([[x_world], [y_world]])
                    else:
                        locus[yellow_locus_num][int(cord[4])][0].append(x_world)
                        locus[yellow_locus_num][int(cord[4])][1].append(y_world)
                    print("cord[4]",cord[4])
        
    def get_xy(self,xy_path):
        # 将坐标点的集合文件.csv读取，并转换成numpy数组进行返回
        xy_csv = open(xy_path, encoding='utf-8')
        xy_data = pd.read_csv(xy_csv, header=None)
        print('loaded data from CSV!')
        xy_numpy = xy_data.to_numpy()
        return xy_numpy
    
    def get_world_xy(self,x,y,homography):
        '''
        功能：通过单应性矩阵将图像坐标x，y转换成世界坐标x_world,y_world
        '''
        xy_src = np.float32([[x], [y], [1]])
        xy_world = np.matmul(homography, xy_src)
        x_world = xy_world[0] / xy_world[2]
        y_world = xy_world[1] / xy_world[2]
        return x_world, y_world
######画图线程######
class plotThread(threading.Thread):
    def __init__(self,board_path):
        threading.Thread.__init__(self)
        self.board_path = board_path
    def run(self):
        locus = ctypes.cast(locus_address, ctypes.py_object).value
        plt.ion()
        img = plt.imread(self.board_path)
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[0, 510.6 * ratio, 0, 161 * ratio])

        #----------------------------------#
        #           刷写坐标
        #----------------------------------#
        plot_t1=time.time()
        plt.cla()
                #print("00000000000000000000000000000")
        ax.imshow(img, extent=[0, 510.6 * ratio, 0, 161 * ratio])
                #print("11111111111111111111111111111")
        #----------------------------------#
        #       统计冰壶球个数
        #----------------------------------#
        yellow_nums = len(locus[-1].keys())     #黄色冰壶数量
        red_nums = len(locus[-2].keys())        #红色冰壶数量
        plt.text(0, 165, s='yellow:{}'.format(yellow_nums), fontsize=10)
        plt.text(0, 180, s='red:{}'.format(red_nums), fontsize=10)
                ## print('y=', yellow_nums)
                ## print('r=', red_nums)
        #----------------------------------#
        #           实时绘制坐标
        #——————————————————————————————————#
        colors = ['red', 'yellow']
        for i in range(len(locus)):
            for j, ids in enumerate(locus[i]):
                color = colors[i % 2]
                plt.plot(locus[i][ids][0], locus[i][ids][1], color=color)
        plot_t2=time.time()
        print("画图时间：",plot_t2-plot_t1)
        plt.pause(0.001)
        plt.ion()
    

if __name__ == "__main__":
    img_path = 'dihu_board.jpg'
    homograpthy_path_1 = '/home/zl/Desktop/tibH1.csv'
    #homograpthy_path_2 = 'Homography_array/Homography-2.csv'
    #homograpthy_path_3 = 'Homography_array/Homography-3.csv'
    H_path = [homograpthy_path_1]#, homograpthy_path_2, homograpthy_path_3]
    H_array = getHomography(H_path)
    locus = [{} for i in range( len(H_array)*2 ) ]
    locus_address=id(locus)
    
    getLocus=Plot_Realtime()
    thread_01 = getLocus(H_array)

    plotTrajectory = plotThread()
    thread_02 = plotTrajectory(img_path)

    # 启动线程
    thread_01.start()
    thread_02.start()
    #P = Plot_Realtime(img_path, H_path)     # create a new instance
    

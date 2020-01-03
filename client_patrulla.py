import socket
import struct
import time
import pickle
import math
from DeteccionObj import DeteccionObj
import threading
import cv2
import numpy as np
import serial  # Importing the serial library to communicate with Arduino
from multiprocessing import Value, Process
from ctypes import c_bool
import numpy as np
from interpreter import Automata
import time
from map_grilla import map_grilla
from Grilla import grilla



flag = True
import os
i = 30
angulo = Value('i', 0)
x = Value('i', 0)
y = Value('i', 0)

t_ref = Value('i', 0) # es el ángulo de referencia
x_ref = Value('i', 0)
y_ref = Value('i', 0)

coord_x_ref = Value('i', 0)
coord_y_ref = Value('i', 0)

coord_x_ref_ant = Value('i', 0)
coord_y_ref_ant = Value('i', 0)


ready = Value(c_bool, False)
flag = Value(c_bool, True)

flag_connected = Value(c_bool, False)
arrived_flag = Value(c_bool, False)

def ard():
    i = 0
    j = 0
    while 1:
        msg = ser.readline()
        # print(msg[0])
        # print(msg)
        if msg[0] == 49:
            i += 1
            if i == 1:
                # print("Llegue")
                arrived_flag.value = True
                time.sleep(2)
                j = 0

        else:
            i = 0
            # if msg[0] == 0:
            arrived_flag.value = False
            if (j % 5) == 0:
                print("Yendo a [" + str(coord_x_ref.value) + '][' + str(coord_y_ref.value) + ']...')
            j += 1

        #print(ser.realine())
# def ard_write(vel1, vel2, sen1, sen2,t_ref, t_act, x_ref,y_ref, x, y, sgn_ref_ang, sgn_ang): # los tiempos de 0.2 se colocaron luego de prueba y error. Vi que con delay de 0.1
#                                        # el arduino hace mal la asignacion de las variables en el codigo
#     print("arduino : " +str(vel1))
#     ser.write([vel1, vel2, sen1, sen2, abs(t_ref), abs(t_act), x_ref, y_ref, x, y, sgn_ref_ang+1, sgn_ang+1])  # Envio dato pwm1 al Arduino
#                                                                                 #si sgn_ref_ang = 0, es negativo,
#                                                                                 # si = 1 es 0 y si es 2 es positivo
#     time.sleep(0.005)
#

def ard_write(t_ref, t_act, x_ref,y_ref, x, y, sgn_ref_ang, sgn_ang): # los tiempos de 0.2 se colocaron luego de prueba y error. Vi que con delay de 0.1
                                       # el arduino hace mal la asignacion de las variables en el codigo
    # print("arduino : " +str(vel1))
    ser.write([abs(t_ref), abs(t_act), x_ref, y_ref, x, y, sgn_ref_ang+1, sgn_ang+1])  # Envio dato pwm1 al Arduino
                                                                                #si sgn_ref_ang = 0, es negativo,
                                                                                # si = 1 es 0 y si es 2 es positivo
    time.sleep(0.005)


def controlador(t_act, x_ref, y_ref, xx, yy):#t_ref, t_act, x_ref, y_ref, xx, yy):  # los tiempos de 0.2 se colocaron luego de prueba y error. Vi que con delay de 0.1
    # el arduino hace mal la asignacion de las variables en el codigo
    # print("Ang_ref : " + str(t_ref))
    # ser.write([t_ref, t_act, x_ref, y_ref, x, y])  # Envio datos al Arduino
    # time.sleep(0.005)
    # x_act = struct.pack("H",xx)
    # y_act = struct.pack("H",yy)
    # x_ref_b = struct.pack("H", x_ref)
    # y_ref_b = struct.pack("H", y_ref)

    x_ref_b_1 = int(x_ref >> 8)
    x_ref_b_2 = int(x_ref & 0xFF)
    y_ref_b_1 = int(y_ref >> 8)
    y_ref_b_2 = int(y_ref & 0xFF)
    # ser.write([x_ref_b, y_ref_b])
    x_act_1 = int(xx >> 8)
    x_act_2 = int(xx & 0xFF)
    y_act_1 = int(yy >> 8)
    y_act_2 = int(yy & 0xFF)
    #
    # print(int(abs(t_ref)), int(abs(t_act)), x_ref_b_1, x_ref_b_2, y_ref_b_1, y_ref_b_2, x_act_1, x_act_2, y_act_1, y_act_2, int(np.sign(t_ref)+1), int(np.sign(t_act)+1))

    ser.write([int(abs(t_act)), x_ref_b_1, x_ref_b_2, y_ref_b_1, y_ref_b_2, x_act_1, x_act_2, y_act_1, y_act_2, int(np.sign(t_act)+1)])#int(abs(t_ref)), int(abs(t_act)), x_ref_b_1, x_ref_b_2, y_ref_b_1, y_ref_b_2, x_act_1, x_act_2, y_act_1, y_act_2, int(np.sign(t_ref)+1), int(np.sign(t_act)+1)])  # Envio dato pwm1 al Arduino
                                                                                #si sgn_ref_ang = 0, es negativo,
                                                            # si = 1 es 0 y si es 2 es positivo
    time.sleep(0.05)

def recibe_imagen():
    # cv2.namedWindow("frame", cv2.WINDOW_AUTOSIZE)
    # cv2.startWindowThread()
    # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    Dt = 0.1
    im_count = 0
    # HOST = '127.0.0.1'  # localost
    HOST = '192.168.1.4' # este es la PC desde la red de labo Labing
    # HOST = '192.168.1.37' # este es la rapsberry desde la red de costaazul

    PORT = 9009  # puerto

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    connection = client_socket.makefile('wb')

    client_socket.sendall(b'Cliente Listo ')
    data = client_socket.recv(1024)
    print(data.decode(encoding='utf-8', errors='strict'))

    time.sleep(0.1)
    print("Preparando Camara...\n")

    T0 = math.floor(time.time()) % 1000
    T = 0
    while T < 5:  # espero 5 seg antes de empezar el codigo
        time.sleep(0.9)
        T = math.floor(time.time()) % 1000 - T0 + 1
        print(T)

    client_socket.sendall(b'0')  # Flag. Indica que pasaron los 5 seg
    # data = b""
    ready.value = True
##----------------------------------------------------------------------------------------------------
# begins MTSA algorithm


##----------------------------------------------------------------------------------------------------

    payload_size = struct.calcsize(">L")
    data = b""
    data2 = b""
    angle = 0
    while flag.value:
        # d = time.time()
        # data = b""
        while len(data) < payload_size:
            data += client_socket.recv(4096) # aca se lee el encabezado del mensaje y se conoce el tamaño de la imagen que
                                            # va a llegar

        packed_msg_size = data[:payload_size]# aca se lee el encabezado del mensaje y se conoce el tamaño de la imagen que
                                            # va a llegar
        data = data[payload_size:]          # si en  client_socket.recv(4096) entro parte del mensaje que contiene la imagen se
                                            # lee acá
        msg_size = struct.unpack(">L", packed_msg_size)[0] # se lee el tamaño de la imagen que llega. en Packe_msg_size esta
                                                        # esa informacion

        while len(data) < msg_size:
            data += client_socket.recv(4096)    # se lee el resto del mensaje.
        frame_data = data[:msg_size] # se almacena el mensaje acá

        data = data[msg_size:] # si entró información del paquete siguiente se lo almacena acá.

        im_count += 1
        # print(im_count)
        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        x.value, y.value, angulo.value = DeteccionObj(frame, False, coord_x_ref, coord_y_ref)
        # client_socket.sendall(b'0')

        # print(angulo.value)
        # if im_count == 5:
        #     print("Se reciben por segundo: " + str(im_count/(time.time()-tiempo_in)))
        #     im_count = 0
        # delay = (i + 1) * Dt - (time.time() - ts)
        # if (delay)<0:
        #     # print("Tiempo menor a 0: "  +str(delay))
        #     time.sleep(0.1)
        #     pass
        # else:
        #     time.sleep(delay) # duermo el sistema un tiempo Dt
        # i+=1
        # print("Tiempo:" +str(time.time() - d))
        # controlador(int(t_ref.value), int(angulo.value), int(x_ref.value), int(y_ref.value), int(x.value), int(y.value))
        ref = (map_grilla(coord_x_ref.value, coord_y_ref.value))
        # print("La ref es")
        # print(ref[0], ref[1])

        if angulo.value == 9999:
            pass
        else:
            angle = angulo.value
        # t_ref.value =int(np.round(np.rad2deg(math.atan2(y_ref.value-y.value, x_ref.value-x.value))))

        # print(ref[0], ref[1])
        #     controlador(angle, x_ref.value, y_ref.value, x.value, y.value)#x.value, y.value)#round(t_ref.value), angle, x_ref.value, y_ref.value, x.value, y.value)#x.value, y.value)
            controlador(angle, int(ref[0]), int(ref[1]), x.value, y.value)#x.value, y.value)#round(t_ref.value), angle, x_ref.value, y_ref.value, x.value, y.value)#x.value, y.value)
    print("you did it!")
    client_socket.close()

ser = serial.Serial('/dev/ttyUSB0', 115200) #hay que ver en que puerto está el arduino
# ser = serial.Serial('/dev/tty.wchusbserial1410', 9600)

print("\033[H\033[J")  # esto limpia toda la consola

# esta es la parte de la comunicacion Cliente (RPI) servidor (la PC con la camara)


T = time.time()  # esto es para generar un vector de tiempo
k = 0
# while os.path.isfile("Caracterizacion_5/11/19{}.txt".format(k)):
#     k += 1

# ang_file = open("Caracterizacion_5/11/19.txt", "w+") # aca voy a guardar el angulo y el tiempo para la etapa de caracterizacion
# ang_file = open("Caracterizacion_planta.txt", "w+")
thread1 = threading.Thread(target=ard)
thread1.start()

thread2 = Process(target=recibe_imagen)
# thread2 = threading.Thread(target= recibe_imagen)
thread2.start()
while not ready.value:
    time.sleep(1)

def go(x, y):
    global event_queue
    x = int(x)
    y = int(y)
    coord_x_ref.value = x
    coord_y_ref.value = y
    # print(automata._event2[:2])
    i = 0
    while arrived_flag.value:
        time.sleep(1)
        print("esperando cambio de referencia")
        # pass
    while 1:
        if arrived_flag.value:
            i += 1
            if i == 1:
                # print('Llegue a [{:d}][{:d}]'.format(x, y))
                event_queue.put('arrived[{:d}][{:d}]'.format(x, y))
                # time.sleep(2)
                break


function_list = []
function_list.append(go)

automata = Automata(function_list, verbose=True)
event_queue = automata.get_event_queue()
automata.load_automata_from_file('grilla.txt')
automata.start()

# i=0
# im_count = 0
# p = 0
# Tmax = 50
# Dt = 0.1 #Es el tiempo que quiero que esté dormido el sistema
# N = int(Tmax/Dt)
#
# # ang_file.write("T_tot\tTiempo\tAngulo\tVelocidad\n")
#
# t = time.time()
# ts = time.time()
# sen1 = 0
# sen2 = 0
# vel = 0
# while (time.time()-ts) < 3: # le doy 3 segundose de y se tiene  que quedar quieto hasta que se acomode la camara
#     pass
# genero el .txt con 4 columnoas,Tiempo total, tiempo parcial, angulo, vel
#     t_par = time.time() - ts # tiempo transcurrido
#     t_tot = time.time() - t #tiempo total transcurrido
#     ang_file.write("%5.4f\t%5.4f\t%d\t%d\n" % (t_tot,t_par, angulo.value, vel))  # tiempo transcurrido, angulo, velocidad.
#
#     ard_write(vel, vel, sen1, sen2)
    # time.sleep(0.1)

    # delay = (i + 1) * Dt - (time.time() - ts)
    # if (delay) < 0:
    #     print("Tiempo menor a 0: " +str(delay))
    #     time.sleep(0.05)
    #     pass
    # else:
    #     time.sleep(delay)  # duermo el sistema un tiempo Dt
    # i += 1

# Esta parte le da escalones de distintos PWM al robot
# i = 0
# for i in range (0, 16): #,16): #arranca con PWM = 95
# ts = time.time()
# sen1 = 1
# sen2 = 1
# vel = 105 + i * 10
#
# while (time.time()-ts) < 14: # le doy 20 segundose de pruebas
# genero el .txt con 4 columnoas,Tiempo total, tiempo parcial, angulo, vel
#         t_par = time.time() - ts # tiempo transcurrido
#         t_tot = time.time() - t #tiempo total transcurrido
#         ang_file.write("%5.4f\t%5.4f\t%d\t%d\n" % (t_tot,t_par, angulo.value, vel))  # tiempo transcurrido, angulo, velocidad.
#         # print("angulo : " + str(angulo.value))
#         ard_write(vel, vel, sen1, sen2)
    # time.sleep(0.1)

    # delay = (i + 1) * Dt - (time.time() - ts)
    # if (delay)<0:
    #     time.sleep(0.05)
    #     pass
    # else:
    #     time.sleep(delay) # duermo el sistema un tiempo Dt
    # i+=1
# kk = 0
# # t_ref.value = 90
# x_ref.value = 105
# y_ref.value = 135
# ts = time.time()
# # # tiempo = time.time()-ts
# #
# while os.path.isfile("trayectoria_{}.txt".format(kk)):
#     kk+=1
# #
#
try:
    while 1:
        pass
#         xx = 105
#         yy = 135
#         while time.time() - ts < 10:
#             if x_ref.value is not xx or y_ref.value is not yy:
#                 x_ref.value = xx
#                 y_ref.value = yy
#             tray = open("trayectoria_{}.txt".format(kk), "a+")
#             tray.write("%f\t%d\t%d\t%d\t%d\n" % (time.time()-ts, x.value, y.value, x_ref.value, y_ref.value))
#             tray.close()
#         xx = 75
#         yy = 135
#         while time.time() - ts < 20:
#             if x_ref.value is not xx or y_ref.value is not yy:
#                 x_ref.value = xx
#                 y_ref.value = yy
#             tray = open("trayectoria_{}.txt".format(kk), "a+")
#             tray.write("%f\t%d\t%d\t%d\t%d\n" % (time.time()-ts,x.value, y.value, x_ref.value, y_ref.value))
#             tray.close()
#         xx = 75
#         yy = 105
#         while time.time() - ts < 30:
#             if x_ref.value is not xx or y_ref.value is not yy:
#                 x_ref.value = xx
#                 y_ref.value = yy
#             tray = open("trayectoria_{}.txt".format(kk), "a+")
#             tray.write("%f\t%d\t%d\t%d\t%d\n" % (time.time()-ts,x.value, y.value, x_ref.value, y_ref.value))
#             tray.close()
#         xx = 75
#         yy = 75
#         while time.time() - ts < 40:
#             if x_ref.value is not xx or y_ref.value is not yy:
#                 x_ref.value = xx
#                 y_ref.value = yy
#             tray = open("trayectoria_{}.txt".format(kk), "a+")
#             tray.write("%f\t%d\t%d\t%d\t%d\n" % (time.time()-ts,x.value, y.value, x_ref.value, y_ref.value))
#             tray.close()
#         ts = time.time()








    # if time.time() - ts > kk * 10:
    #     t_ref.value = t_ref.value + 45
    #     kk += 1
    #     if t_ref.value > 180:
    #         t_ref.value = -180


    # time.sleep(3)
    # if t_ref.value > 250:
    #     break
#
# vel = 0
# sen2 = 0
# sen1 = 0
    # while (time.time()-ts) < 14: # le doy 3 segundose de y se tiene  que quedar quieto hasta que se acomode la camara
    #
    # # genero el .txt con 4 columnoas,Tiempo total, tiempo parcial, angulo, vel
    #     t_par = time.time() - ts # tiempo transcurrido
    #     t_tot = time.time() - t #tiempo total transcurrido
    #     ang_file.write("%5.4f\t%5.4f\t%d\t%d\n" % (t_tot,t_par, angulo.value, vel))  # tiempo transcurrido, angulo, velocidad.
    #     # print("angulo : " + str(angulo.value))
    #     ard_write(vel, vel, sen1, sen2)
    #     # time.sleep(0.1)

        # delay = (i + 1) * Dt - (time.time() - ts)
        # if (delay) < 0:
        #     time.sleep(0.05)
        #     pass
        # else:
        #     time.sleep(delay)  # duermo el sistema un tiempo Dt
        # i += 1
# i = 0







except KeyboardInterrupt:
# flag.value = False
# ard_write(0,0,0,0)
    ser.close()
# ang_file.close()

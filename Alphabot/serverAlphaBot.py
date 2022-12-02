from multiprocessing import connection
import time
from tracemalloc import stop
import RPi.GPIO as GPIO
import socket
import sqlite3

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

class AlphaBot(object):
    def __init__(self, in1=13, in2=12, ena=6, in3=21, in4=20, enb=26):
        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.ENA = ena
        self.ENB = enb
        self.PA  = 50
        self.PB  = 50

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        self.PWMA = GPIO.PWM(self.ENA,500)
        self.PWMB = GPIO.PWM(self.ENB,500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        self.stop()

    def left(self):
        self.PWMA.ChangeDutyCycle(self.PA - 17)
        self.PWMB.ChangeDutyCycle(self.PB - 18)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

    def stop(self):
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)

    def right(self):
        self.PWMA.ChangeDutyCycle(self.PA - 20)
        self.PWMB.ChangeDutyCycle(self.PB - 20)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

    def forward(self, speed=82):
        self.PWMA.ChangeDutyCycle(speed + 5)
        self.PWMB.ChangeDutyCycle(speed + 18)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

    def backward(self, speed=88):
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed + 12)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        
    def set_pwm_a(self, value):
        self.PA = value
        self.PWMA.ChangeDutyCycle(self.PA)

    def set_pwm_b(self, value):
        self.PB = value
        self.PWMB.ChangeDutyCycle(self.PB)    
    
    def set_motor(self, left, right):
        if (right >= 0) and (right <= 100):
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif (right < 0) and (right >= -100):
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= 100):
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif (left < 0) and (left >= -100):
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)

def main():
    Ab = AlphaBot()
    s.bind(("0.0.0.0", 5000))
    s.listen()
    print("In attesa di connessione...")
    connection, _ = s.accept()

    while True:
        messaggio = connection.recv(4096)
        messaggio = messaggio.decode()
        con = sqlite3.connect("./databaseAlphaBot.db")
        cur = con.cursor()
        res = cur.execute("SELECT MOVIMENTO FROM Tabbella_movimenti WHERE ID = " + messaggio)
        serie = res.fetchall()
        stringaComandi = serie[0][0]
        msgSplit = stringaComandi.split(";")
        print(msgSplit)
        for k in range(0,3):
            msg = msgSplit[k].split(",")
            print(msg)
            if msg[0] == "f":
                Ab.forward()
                time.sleep(float(msg[1]))
                Ab.stop()
            if msg[0] == "r":
                Ab.right()
                time.sleep(float(msg[1]))
                Ab.stop()
            if msg[0] == "l":
                Ab.left()
                time.sleep(float(msg[1]))
                Ab.stop()
            if msg[0] == "b":
                Ab.backward()
                time.sleep(float(msg[1]))
                Ab.stop()

if __name__ == '__main__':
    main()
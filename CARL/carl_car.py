from Arduino import Arduino
from RealSense import *
import cv2
import imutils	
import cv2
import time
import argparse

import sys
sys.path.append('../testing')
from remote_cam_test import load_prompt, run_inference

# while True:
#     command = input("Enter a command:\n")
#     if command == 's':
#         angle = input("Enter a steering angle (-30 ~ 30):\n")
#         Car.steer(float(angle))
#     elif command == 'd':
#         speed = input("Enter a drive speed (-3.0 ~ 3.0):\n")
#         Car.drive(float(speed))
#     elif command == 'm':
#         melody = input("Enter a number (0 ~ 8):\n")
#         Car.music(int(melody))
#     elif command == 'z':
#         pwm = input("Enter a PWM value (~1500):\n")
#         Car.zero(int(pwm))
#     elif command == 'p':
#         flag = input("Enter 1 to turn on PID and 0 to turn off:\n")
#         Car.pid(int(flag))
#     elif command == 'e':
#         print(int(Car.encoder().strip()))   # need to strip character of \r or \n
#     elif command == 'q':
#         if Car.CarConnected:
#             del Car
#         break

class CARL:

    def __init__(self):
        self.speed = 1.0
        self.turn_angle = 15.0
        self.pid_enable = 0
        self.wait_time_ms = 100
        self.enableDepth = False 
        self.rs = RealSense("/dev/video1", RS_VGA, self.enableDepth)    # RS_VGA, RS_720P, or RS_1080P
        self.Car = Arduino("/dev/ttyUSB0", 115200)
        self.Car.pid(int(self.pid_enable))

        prompt = input("Please enter prompt: ")
        load_prompt(prompt)

    def __del__(self):
        print("In destructor")
        try:
            del self.rs
        except Exception as e:
            print(e)
        cv2.destroyAllWindows()
        if self.Car.CarConnected:
            del self.Car

    
    def update_car_param(self, test: bool):
        print("You have 5 second to enter a command")
        if test:
            key = input("Enter q, a-steer_angle, d-drive, p-pid, w-wait_time_ms\n")
        else:
            key = cv2.waitKey(1)
        print(f"Entered key: {key}")
        if key == 'q':
            raise ValueError("Stopping")
        elif key == 'a':
            ret = float(input("Enter a steering angle (0 ~ 30):\n"))
            if ret >= 0 and ret <= 30:
                self.turn_angle = float(ret)
        elif key == 'd':
            ret = float(input("Enter a drive speed (-3.0 ~ 3.0):\n"))
            if ret > -3.0 and ret < 3.0:
                self.speed = float(ret)
        elif key == 'p':
            flag = int(input("Enter 1 to turn on PID and 0 to turn off:\n"))
            if flag == 0 or flag == 1:
                self.pid_enable = int(flag)
        elif key == 'w':
            ret = int(input("Enter a move time between start and stop in ms:\n"))
            self.wait_time_ms = abs(ret)
        else:
            print("No valid command entered. Continuing...")



    def move_car(self, angle):
        # Turn wheels
        self.Car.steer(float(angle))
        # Move
        self.Car.drive((self.speed))
        # Wait
        start = time.time()
        while (time.time() - start) < (self.wait_time_ms/1000.0):
            pass
        # Stop
        self.Car.drive(0.0)
        self.Car.steer(0.0)



    def car_step(self, input):
        '''
        Input:
            - input: 0 - stop, 1 - straight, 2 - turn left, 3 - turn right
        '''
        # self.update_car_param()

        if input == 0:
            # Stop
            print("Don't move")
            pass
        elif input == 1:
            # Drive Straight
            print("Going Straight")
            self.move_car(0.0)
        elif input == 2:
            # Turn Left
            print("Turning Left")
            self.move_car(-self.turn_angle)
        elif input == 3:
            # Turn Right
            print("Turning Right")
            self.move_car(self.turn_angle)
        else:
            raise ValueError("Invalid input to car_step()")


        

    def run(self):
        
        
        writer = None
        frameIndex = 0
        print("Now starting run()")
        try:
            while True:
                (time, rgb, depth, accel, gyro) = self.rs.getData(self.enableDepth)
                cv2.imshow("CARL Camera", rgb)

                # Run inference
                command = run_inference(rgb)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise ValueError("Ending live stream")

                
        except Exception as e:
            print(e)
            # if writer:
            #     writer.release()

    def test_car(self):
        try:
            while True:
                ret = input("\nEnter a number; 0-stop, 1-straight, 2-left, 3-right; u-update or q-quit\n")
                if ret == 'q':
                    print(f"""Last parameters used:\n\tturn_angle - {self.turn_angle}\n\tspeed - {self.speed}\n\tpid_enable - {self.pid_enable}\n\twait_time_ms - {self.wait_time_ms}""")
                    break
                elif ret == 'u':
                    self.update_car_param(test=True)
                elif ret == '0' or ret == '1' or ret == '2' or ret == '3':
                    self.car_step(int(ret))
                else:
                    print("Not a valid input. Try again")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    
    print("Test")
    print("Running")
    carl = CARL()
    carl.run()

    print("Deleting carl")
    del carl
    print("End\n")
    

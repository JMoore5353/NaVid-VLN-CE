from Arduino import Arduino
from RealSense import *
import cv2
import imutils	
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
        self.speed = 0.5
        self.turn_angle = 30.0
        self.straight_angle=3.0
        self.pid_enable = 0
        self.wait_time_ms = 85
        self.enableDepth = False 
        self.rs = RealSense("/dev/video1", RS_VGA, self.enableDepth)    # RS_VGA, RS_720P, or RS_1080P
        self.Car = Arduino("/dev/ttyUSB0", 115200)
        self.Car.pid(int(self.pid_enable))
        self.Car.zero(1500)
        # self.add_prompt()
        

    def __del__(self):
        print("In destructor")
        try:
            del self.rs
        except Exception as e:
            print(e)
        cv2.destroyAllWindows()
        try:
            if self.Car.CarConnected:
                self.stop_car()
                del self.Car
        except Exception as e:
            print(e)

    def add_prompt(self):
        prompt = input("Please enter prompt: ")
        load_prompt(prompt)
    
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
        elif key == 'o':
            ret = float(input("Enter a straight angle offset:\n"))
            self.straight_angle = ret
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

    def stop_car(self):
        # Stop
        self.Car.drive(0.0)
        # start = time.time()
        # while (time.time() - start) < (500/1000.0):
        #     pass
        # self.Car.steer(self.straight_angle)


    def move_car(self, angle):
        # Turn wheels
        self.Car.steer(float(angle))
        # Move
        
        self.Car.drive(float(self.speed))
        # Wait
        start = time.time()
        if angle == self.straight_angle:
            waittime = 50 / 1000.0
            print("Straight Wait time: ", waittime)

            while (time.time() - start) < (waittime):
                pass
        else:
            while (time.time() - start) < (self.wait_time_ms/1000.0):
                pass
        self.stop_car()



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
            self.move_car(self.straight_angle)
        elif input == 2:
            # Turn Left
            print("Turning Left")
            self.move_car(-self.turn_angle+self.straight_angle)
        elif input == 3:
            # Turn Right
            print("Turning Right")
            self.move_car(self.turn_angle+self.straight_angle)
        else:
            raise ValueError("Invalid input to car_step()")


        

    def run(self, view):
        
        

        writer = None
        frameIndex = 0
        print("Now starting run()")
        try:
            (time, rgb, depth, accel, gyro) = self.rs.getData(self.enableDepth)
            cv2.imshow("CARL Camera", rgb)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()

            while True:
                (time, rgb, depth, accel, gyro) = self.rs.getData(self.enableDepth)
                if view:
                    cv2.imshow("CARL Camera", rgb)

                # Run inference
                command = run_inference(rgb)
                command_distance = command[2:]
                command = command[0]
                if command == '0':
                    print("Receiced '0' Breaking out of loop.")
                    break
                print("Command received: ", command)
                self.car_step(int(command))

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise ValueError("Ending live stream")

                
        except Exception as e:
            print(e)
            # if writer:
            #     writer.release()

    def print_parameters(self):
            print(f"Last parameters used:\n\tturn_angle - {self.turn_angle}\n\tspeed - {self.speed}\n\tpid_enable - {self.pid_enable}\n\twait_time_ms - {self.wait_time_ms}\n\tstraight offset - {self.straight_angle}")

    def test_car(self):
        try:
            while True:
                ret = input("\nEnter a number; 0-stop, 1-straight, 2-left, 3-right; u-update or q-quit\n")
                if ret == 'q':
                    self.print_parameters()
                    break
                elif ret == 'u':
                    self.update_car_param(test=True)
                elif ret == 'p':
                    self.print_parameters()
                elif ret == '0' or ret == '1' or ret == '2' or ret == '3':
                    self.car_step(int(ret))
                else:
                    print("Not a valid input. Try again")
        except Exception as e:
            print(e)


# if __name__ == "__main__":
    
#     print("Test")
#     print("Running")
#     carl = CARL()
#     carl.run()

#     print("Deleting carl")
#     del carl
#     print("End\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Script for RC car running NaVid')
    # parser.add_argument('--test', type=int, help='An integer number')
    parser.add_argument('-t', '--test', action='store_true', help='Test the car control')
    parser.add_argument('-v', '--view', action='store_true', help='View the camera via openCV')

    args = parser.parse_args()
    test = args.test
    view = args.view

    print(f"Test: {test}")
    print(f"View: {view}")

    
    # print("Test")
    print("Running")
    carl = CARL()
    if test:
        carl.test_car()
    else:
        carl.print_parameters()
        try:
            while True:
                carl.add_prompt()
                carl.run(view)
        except Exception as e:
            print(e)

    print("Deleting carl")
    try:
        del carl
    except Exception as e:
        print(e)
    print("End\n")
    

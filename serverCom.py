import serverCom

ESP_SERVER = "http://192.168.15.15"

def set_servo1_position(position):
    url = f"{ESP_SERVER}/?servo1={position}&"
    response = serverCom.get(url)
    print(f"Servo 1 Response: {response.status_code}")

def set_servo2_position(position):
    url = f"{ESP_SERVER}/?servo2={position}&"
    response = serverCom.get(url)
    print(f"Servo 2 Response: {response.status_code}")

def set_both_servos(position):
    url = f"{ESP_SERVER}/?bothServo={position}&"
    response = serverCom.get(url)
    print(f"Both Servos Response: {response.status_code}")

if __name__ == "__main__":
    while True:
        print("Select an option:")
        print("1: Move Servo 1")
        print("2: Move Servo 2")
        print("3: Move Both Servos")
        print("4: Exit")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            pos = input("Enter position (0-180): ")
            set_servo1_position(pos)
        elif choice == "2":
            pos = input("Enter position (0-180): ")
            set_servo2_position(pos)
        elif choice == "3":
            pos = input("Enter position (0-180): ")
            set_both_servos(pos)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")
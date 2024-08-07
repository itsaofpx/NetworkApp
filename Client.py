import socket
from encryption import encrypt_message, decrypt_message

def send_request(sock, request):
    encrypted_request = encrypt_message(request)
    sock.send(encrypted_request)
    response = sock.recv(4096)
    decrypted_response = decrypt_message(response)
    print(decrypted_response)
    return decrypted_response

def main():
    server_ip = '127.0.0.1'
    server_port = 9999

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    logged_in = False

    while True:
        if not logged_in:
            print("\n1. Sign up")
            print("2. Log in")
            print("3. Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                student_id = input("Enter Student ID: ")
                name = input("Enter Name: ")
                password = input("Enter Password: ")
                send_request(client_socket, f"SIGNUP {student_id} {name} {password}")

            elif choice == '2':
                student_id = input("Enter Student ID: ")
                password = input("Enter Password: ")
                response = send_request(client_socket, f"LOGIN {student_id} {password}")
                if "Login successful" in response:
                    logged_in = True

            elif choice == '3':
                send_request(client_socket, "EXIT")
                break

            else:
                print("Invalid option. Try again.")
        
        else:
            print("\n1. View Enrollable Subjects")
            print("2. Enroll")
            print("3. Unenroll")
            print("4. Set Grade")
            print("5. View GPAX")
            print("6. View Enrolled Subjects")
            print("7. Logout")
            choice = input("Choose an option: ")

            if choice == '1':
                subjects = send_request(client_socket, "VIEW_SUBJECTS")
                print("Enrollable Subjects:")
                for code, details in eval(subjects).items():
                    print(f"{code}: {details['name']} ({details['credits']} credits)")

            elif choice == '2':
                subject_code = input("Enter Subject Code: ")
                send_request(client_socket, f"ENROLL {subject_code}")

            elif choice == '3':
                subject_code = input("Enter Subject Code: ")
                send_request(client_socket, f"UNENROLL {subject_code}")

            elif choice == '4':
                subject_code = input("Enter Subject Code: ")
                grade = input("Enter Grade (A, B+, B, C+, C, D+, D, F): ")
                send_request(client_socket, f"SET_GRADE {subject_code} {grade}")

            elif choice == '5':
                send_request(client_socket, "GPAX")

            elif choice == '6':
                enrolled_subjects = send_request(client_socket, "VIEW_ENROLLED_SUBJECTS")
                print("Enrolled Subjects:")
                for code, details in eval(enrolled_subjects).items():
                    print(f"{code}: {details['name']} ({details['credits']} credits)")

            elif choice == '7':
                response = send_request(client_socket, "LogOut")
                if "Logged out successfully" in response:
                    logged_in = False


            else:
                print("Invalid option. Try again.")

    client_socket.close()

if __name__ == "__main__":
    main()

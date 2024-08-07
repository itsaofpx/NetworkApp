import socket
from protocol import create_message, parse_response, create_response
from encryption import encrypt_message, decrypt_message

def send_request(sock, request):
    try:
        encrypted_request = encrypt_message(request)
        sock.sendall(encrypted_request)
        response = sock.recv(4096)
        decrypted_response = decrypt_message(response)
        return decrypted_response
    except Exception as e:
        print(f"Error in sending/receiving data: {e}")
        return None

def main():
    server_ip = '127.0.0.1'
    server_port = 5050

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
    except Exception as e:
        print(f"Could not connect to server: {e}")
        return

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
                response = send_request(client_socket, create_message("SIGNUP", student_id, name, password))
                if response:
                    status_code, message, protocol_code = parse_response(response)
                    print(f"{status_code} {message}\n{protocol_code}")

            elif choice == '2':
                student_id = input("Enter Student ID: ")
                password = input("Enter Password: ")
                response = send_request(client_socket, create_message("LOGIN", student_id, password))
                if response:
                    status_code, message, protocol_code = parse_response(response)
                    print(f"{status_code} {message}\n{protocol_code}")
                    if status_code == 200:
                        logged_in = True

            elif choice == '3':
                response = send_request(client_socket, create_message("EXIT"))
                if response:
                    status_code, message, protocol_code = parse_response(response)
                    print(f"{status_code} {message}\n{protocol_code}")
                break

            else:
                response = create_response(400, "Invalid option selected.", "INVALID_OPTION")
                status_code, message, protocol_code = parse_response(response)
                print(f"{status_code} {message}\n{protocol_code}")

        else:
            print("\n1. View Enrollable Subjects")
            print("2. View Enrolled Subjects")
            print("3. Enroll")
            print("4. Unenroll")
            print("5. Set Grade")
            print("6. View GPAX")
            print("7. Logout")
            choice = input("Choose an option: ")

            if choice == '1':
                response = send_request(client_socket, create_message("VIEW_SUBJECTS"))
                if response:
                    subjects = response
                    print("Enrollable Subjects:")
                    try:
                        subjects_dict = eval(subjects)  # Be cautious with eval
                        for code, details in subjects_dict.items():
                            print(f"{code}: {details['name']} ({details['credits']} credits)")
                    except Exception as e:
                        print(f"Error parsing subjects: {e}")
            elif choice == '2':
                response = send_request(client_socket, create_message("VIEW_ENROLLED_SUBJECTS"))
                if response:
                    enrolled_subjects = response
                    try:
                        enrolled_dict = eval(enrolled_subjects)  # Be cautious with eval
                        print("Enrolled Subjects:")
                        for code, details in enrolled_dict.items():
                            print(f"{code}: {details['name']} ({details['credits']} credits)")
                    except Exception as e:
                        print(f"Error parsing enrolled subjects: {e}")
            elif choice == '3':
                subject_code = input("Enter Subject Code: ")
                response = send_request(client_socket, create_message("ENROLL", subject_code))
                if response:
                    status_code, message, protocol_code = parse_response(response)
                    print(f"{status_code} {message}\n{protocol_code}")

            elif choice == '4':
                subject_code = input("Enter Subject Code: ")
                response = send_request(client_socket, create_message("UNENROLL", subject_code))
                if response:
                    status_code, message, protocol_code = parse_response(response)
                    print(f"{status_code} {message}\n{protocol_code}")

            elif choice == '5':
                subject_code = input("Enter Subject Code: ")
                grade = input("Enter Grade (A, B+, B, C+, C, D+, D, F): ")
                response = send_request(client_socket, create_message("SET_GRADE", subject_code, grade))
                if response:
                    status_code, message, protocol_code = parse_response(response)
                    print(f"{status_code} {message}\n{protocol_code}")

            elif choice == '6':
                response = send_request(client_socket, create_message("GPAX"))
                if response:
                    print(response)


            elif choice == '7':
                response = send_request(client_socket, create_message("LogOut"))
                if response:
                    status_code, message, protocol_code = parse_response(response)
                    print(f"{status_code} {message}\n{protocol_code}")
                    if status_code == 200:
                        logged_in = False

            else:
                response = create_response(400, "Invalid option selected.", "INVALID_OPTION")
                status_code, message, protocol_code = parse_response(response)
                print(f"{status_code} {message}\n{protocol_code}")

    client_socket.close()

if __name__ == "__main__":
    main()

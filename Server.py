import socket
import threading
import json
from encryption import encrypt_message, decrypt_message
from enrollment import EnrollmentSystem

PORT = 9999

def handle_client(client_socket, enrollment_system):
    logged_in = False
    current_student_id = None

    while True:
        try:
            request = client_socket.recv(4096)
            if not request:
                break
            decrypted_request = decrypt_message(request)
            command, *args = decrypted_request.split()
            response = ""

            if not logged_in:
                if command == "SIGNUP":
                    student_id, name, password = args
                    if enrollment_system.signup(student_id, name, password):
                        response = "Signup successful."
                    else:
                        response = "Student ID already exists."
                
                elif command == "LOGIN":
                    student_id, password = args
                    if enrollment_system.login(student_id, password):
                        logged_in = True
                        current_student_id = student_id
                        response = "Login successful."
                    else:
                        response = "Invalid credentials."
                
                elif command == "EXIT":
                    response = "Goodbye!"
                    client_socket.send(encrypt_message(response))
                    break
                else:
                    response = "Please sign up or log in first."
            
            else:
                if command == "VIEW_SUBJECTS":
                    subjects = enrollment_system.view_subjects()
                    response = json.dumps(subjects)
                
                elif command == "ENROLL":
                    subject_code = args[0]
                    if enrollment_system.enroll(current_student_id, subject_code):
                        response = "Enrollment successful."
                    else:
                        response = "Enrollment failed."
                
                elif command == "UNENROLL":
                    subject_code = args[0]
                    if enrollment_system.unenroll(current_student_id, subject_code):
                        response = "Unenrollment successful."
                    else:
                        response = "Unenrollment failed."
                
                elif command == "SET_GRADE":
                    subject_code, grade = args
                    if enrollment_system.set_grade(current_student_id, subject_code, grade):
                        response = "Grade set successfully."
                    else:
                        response = "Failed to set grade."
                
                elif command == "GPAX":
                    student = enrollment_system.students.get(current_student_id)
                    if student:
                        response = f"GPAX: {student.get('gpax', 'Not calculated'):.2f}"
                    else:
                        response = "Student not found."

                elif command == "VIEW_ENROLLED_SUBJECTS":
                    enrolled_subjects = enrollment_system.view_enrolled_subjects(current_student_id)
                    response = json.dumps(enrolled_subjects)
                elif command == "LogOut":
                    logged_in = False
                    response = "Logged out successfully."

                else:
                    response = "Invalid command."

            client_socket.send(encrypt_message(response))

        except Exception as e:
            print(f"Error handling client: {e}")
            break

    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen()
    print(f"Server listening on port {PORT}")

    enrollment_system = EnrollmentSystem()

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, enrollment_system))
        client_handler.start()

if __name__ == "__main__":
    main()

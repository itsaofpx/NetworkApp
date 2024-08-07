import socket
import threading
import json
from datetime import datetime
from protocol import create_response, parse_message
from encryption import encrypt_message, decrypt_message
from enrollment import EnrollmentSystem

PORT = 5050

def log_with_timestamp(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def handle_client(client_socket, enrollment_system):
    logged_in = False
    current_student_id = None

    while True:
        try:
            log_with_timestamp("Waiting for request...")
            request = client_socket.recv(4096)
            if not request:
                log_with_timestamp("No request received. Closing connection.")
                break
            
            log_with_timestamp("Request received. Decrypting...")
            decrypted_request = decrypt_message(request)
            log_with_timestamp(f"Decrypted request: {decrypted_request}")
            
            command, args = parse_message(decrypted_request)
            response = ""

            if not logged_in:
                log_with_timestamp(f"Processing command: {command} with args: {args}")
                
                if command == "SIGNUP":
                    student_id, name, password = args
                    if enrollment_system.signup(student_id, name, password):
                        response = create_response(201, "Signup successful.", protocol_code="SIGNUP_SUCCESS")
                        log_with_timestamp("Signup successful.")
                    else:
                        response = create_response(400, "Student ID already exists.", protocol_code="SIGNUP_FAIL")
                        log_with_timestamp("Signup failed. Student ID already exists.")
                
                elif command == "LOGIN":
                    student_id, password = args
                    if enrollment_system.login(student_id, password):
                        logged_in = True
                        current_student_id = student_id
                        response = create_response(200, "Login successful.", protocol_code="LOGIN_SUCCESS")
                        log_with_timestamp("Login successful.")
                    else:
                        response = create_response(401, "Invalid credentials.", protocol_code="LOGIN_FAIL")
                        log_with_timestamp("Login failed. Invalid credentials.")
                
                elif command == "EXIT":
                    response = create_response(200, "Goodbye!", protocol_code="EXIT")
                    log_with_timestamp("Client requested exit.")
                    client_socket.send(encrypt_message(response))
                    break
                else:
                    response = create_response(400, "Invalid command.", protocol_code="INVALID_COMMAND")
                    log_with_timestamp("Invalid command received.")
            
            else:
                log_with_timestamp(f"Processing command: {command} with args: {args}")
                
                if command == "VIEW_SUBJECTS":
                    subjects = enrollment_system.get_subjects()
                    response = json.dumps(subjects)
                    log_with_timestamp("Subjects viewed.")
                
                elif command == "ENROLL":
                    subject_code = args[0]
                    result = enrollment_system.enroll(current_student_id, subject_code)
                    if result:
                        response = create_response(200, "Enrolled successfully.", protocol_code="ENROLL_SUCCESS")
                        log_with_timestamp("Enrollment successful.")
                    else:
                        response = create_response(400, "Enrollment failed or subject not available.", protocol_code="ENROLL_FAIL")
                        log_with_timestamp("Enrollment failed.")
                
                elif command == "UNENROLL":
                    subject_code = args[0]
                    result = enrollment_system.unenroll(current_student_id, subject_code)
                    if result:
                        response = create_response(200, "Unenrolled successfully.", protocol_code="UNENROLL_SUCCESS")
                        log_with_timestamp("Unenrollment successful.")
                    else:
                        response = create_response(400, "Unenrollment failed or subject not enrolled.", protocol_code="UNENROLL_FAIL")
                        log_with_timestamp("Unenrollment failed.")
                
                elif command == "SET_GRADE":
                    subject_code, grade = args
                    result = enrollment_system.set_grade(current_student_id, subject_code, grade)
                    if result:
                        response = create_response(200, "Grade set successfully.", protocol_code="GRADE_SUCCESS")
                        log_with_timestamp("Grade set successfully.")
                    else:
                        response = create_response(400, "Failed to set grade.", protocol_code="GRADE_FAIL")
                        log_with_timestamp("Failed to set grade.")
                
                elif command == "GPAX":
                    gpax = enrollment_system.calculate_gpax(current_student_id)
                    response = f"Your GPAX is: {gpax:.2f}"
                    log_with_timestamp(f"GPAX calculated: {gpax:.2f}")

                elif command == "VIEW_ENROLLED_SUBJECTS":
                    enrolled_subjects = enrollment_system.get_enrolled_subjects(current_student_id)
                    response = json.dumps(enrolled_subjects)
                    log_with_timestamp("Viewed enrolled subjects.")
                
                elif command == "LogOut":
                    logged_in = False
                    current_student_id = None
                    response = create_response(200, "Logged out successfully.", protocol_code="LOGOUT_SUCCESS")
                    log_with_timestamp("Logged out successfully.")
                
                else:
                    response = create_response(400, "Invalid command.", protocol_code="INVALID_COMMAND")
                    log_with_timestamp("Invalid command received.")
            
            log_with_timestamp(f"Sending response: {response}")
            client_socket.send(encrypt_message(response))
        
        except Exception as e:
            log_with_timestamp(f"Exception occurred: {e}")
            response = create_response(500, "Internal server error.", protocol_code="SERVER_ERROR")
            client_socket.send(encrypt_message(response))
            break

    client_socket.close()
    log_with_timestamp("Client socket closed.")

def main():
    log_with_timestamp("Server running on port 5050...")
    enrollment_system = EnrollmentSystem()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(5)

    while True:
        try:
            log_with_timestamp("Waiting for connection...")
            client_socket, addr = server_socket.accept()
            log_with_timestamp(f"Connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket, enrollment_system))
            client_handler.start()
        except Exception as e:
            log_with_timestamp(f"Error accepting connection: {e}")

if __name__ == "__main__":
    main()

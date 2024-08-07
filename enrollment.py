import json

class EnrollmentSystem:
    def __init__(self):
        self.subjects = self.load_subjects()
        self.students = self.load_students()

    def load_subjects(self):
        with open('subjects.json', 'r') as file:
            return json.load(file)

    def save_subjects(self):
        with open('subjects.json', 'w') as file:
            json.dump(self.subjects, file, indent=4)

    def load_students(self):
        try:
            with open('students.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}  # No student data yet

    def save_students(self):
        with open('students.json', 'w') as file:
            json.dump(self.students, file, indent=4)

    def signup(self, student_id, name, password):
        if student_id in self.students:
            return False
        self.students[student_id] = {"name": name, "password": password, "enrolled": {}, "grades": {}}
        self.save_students()
        return True

    def login(self, student_id, password):
        student = self.students.get(student_id)
        return student and student["password"] == password

    def enroll(self, student_id, subject_code):
        student = self.students.get(student_id)
        subject = self.subjects.get(subject_code)
        if student and subject and subject_code not in student["enrolled"]:
            student["enrolled"][subject_code] = subject
            self.save_students()
            return True
        return False

    def unenroll(self, student_id, subject_code):
        student = self.students.get(student_id)
        if student and subject_code in student["enrolled"]:
            del student["enrolled"][subject_code]
            self.save_students()
            return True
        return False

    def set_grade(self, student_id, subject_code, grade):
        student = self.students.get(student_id)
        valid_grades = {"A", "B+", "B", "C+", "C", "D+", "D", "F"}
        if student and subject_code in student["enrolled"] and grade in valid_grades:
            student["grades"][subject_code] = grade
            self.save_students()
            return True
        return False

    def get_subjects(self):
        return self.subjects

    def get_enrolled_subjects(self, student_id):
        student = self.students.get(student_id)
        return student["enrolled"] if student else {}

    def calculate_gpax(self, student_id):
        student = self.students.get(student_id)
        if not student:
            return 0.0
        total_credits = 0
        total_points = 0
        grades = {
            "A": 4.0, "B+": 3.5, "B": 3.0, "C+": 2.5, "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0
        }
        for subject_code, grade in student["grades"].items():
            subject = self.subjects.get(subject_code)
            if subject:
                total_credits += subject["credits"]
                total_points += grades.get(grade, 0) * subject["credits"]
        return total_points / total_credits if total_credits > 0 else 0.0

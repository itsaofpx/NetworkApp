import json

class EnrollmentSystem:
    def __init__(self):
        self.students = {}
        self.subjects = self.load_subjects()
        self.load_students()

    def load_subjects(self):
        """Load subjects from a JSON file."""
        try:
            with open('subjects.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: 'subjects.json' file not found. Please create this file with the required subjects.")
            return {}

    def load_students(self):
        """Load students from a JSON file."""
        try:
            with open('students.json', 'r') as f:
                self.students = json.load(f)
        except FileNotFoundError:
            self.students = {}

    def save_subjects(self, subjects):
        """Save subjects to a JSON file."""
        with open('subjects.json', 'w') as f:
            json.dump(subjects, f, indent=4)

    def save_students(self):
        """Save students to a JSON file."""
        with open('students.json', 'w') as f:
            json.dump(self.students, f, indent=4)

    def signup(self, student_id, name, password):
        """Register a new student."""
        if student_id not in self.students:
            self.students[student_id] = {
                "name": name,
                "password": password,
                "enrolled_subjects": {},
                "gpax": 0
            }
            self.save_students()
            return True
        return False

    def login(self, student_id, password):
        """Authenticate a student."""
        student = self.students.get(student_id)
        return student and student["password"] == password

    def view_subjects(self):
        """Return the list of available subjects."""
        return self.subjects

    def enroll(self, student_id, subject_code):
        """Enroll a student in a subject."""
        student = self.students.get(student_id)
        if student and subject_code in self.subjects:
            if subject_code not in student["enrolled_subjects"]:
                student["enrolled_subjects"][subject_code] = self.subjects[subject_code]
                self.save_students()
                return True
            return False  # Already enrolled
        return False

    def unenroll(self, student_id, subject_code):
        """Unenroll a student from a subject."""
        student = self.students.get(student_id)
        if student and subject_code in student["enrolled_subjects"]:
            del student["enrolled_subjects"][subject_code]
            self.save_students()
            return True
        return False

    def set_grade(self, student_id, subject_code, grade):
        """Set or update a grade for a subject."""
        student = self.students.get(student_id)
        if student and subject_code in student["enrolled_subjects"]:
            valid_grades = {"A": 4.0, "B+": 3.5, "B": 3.0, "C+": 2.5, "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0}
            if grade in valid_grades:
                student["enrolled_subjects"][subject_code]["grade"] = grade
                self.calculate_gpax(student_id)
                self.save_students()
                return True
        return False

    def view_enrolled_subjects(self, student_id):
        """View all subjects a student is currently enrolled in."""
        student = self.students.get(student_id)
        if student:
            return student["enrolled_subjects"]
        return {}

    def calculate_gpax(self, student_id):
        """Calculate the GPA (GPAX) for a student."""
        student = self.students.get(student_id)
        if student:
            total_credits = 0
            total_points = 0
            for subject_code, details in student["enrolled_subjects"].items():
                grade = details.get("grade")
                if grade:
                    credits = details["credits"]
                    grade_points = {"A": 4.0, "B+": 3.5, "B": 3.0, "C+": 2.5, "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0}
                    total_points += grade_points.get(grade, 0) * credits
                    total_credits += credits
            student["gpax"] = total_points / total_credits if total_credits > 0 else 0

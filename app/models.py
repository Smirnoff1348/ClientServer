from datetime import datetime
from threading import Lock

_lock = Lock()


class Student:
    def __init__(self, id, fullName, email, year):
        self.id = id
        self.fullName = fullName
        self.email = email
        self.year = int(year)
        self.enrolledOn = datetime.utcnow()
        self.deleted = False
        self.course_ids = []
        self._history = 0

    def to_dict(self):
        return {
            "id": self.id,
            "fullName": self.fullName,
            "email": self.email,
            "year": self.year,
            "enrolledOn": self.enrolledOn.isoformat(),
        }

    def status(self):
        return {
            "rating": self._history,
            "courses": [{"id": cid} for cid in self.course_ids],
        }


class Course:
    def __init__(self, id, title, credits, capacity):
        self.id = id
        self.title = title
        self.credits = int(credits)
        self.capacity = int(capacity)
        self.deleted = False
        self.student_ids = []
        self._popularity = 0

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "credits": self.credits,
            "capacity": self.capacity,
        }

    def status(self):
        return {
            "total": self.capacity,
            "available": max(0, self.capacity - len(self.student_ids)),
            "popularity": self._popularity,
            "students": [{"id": sid} for sid in self.student_ids],
        }


class Storage:
    def __init__(self):
        self.students = {}
        self.courses = {}

    def add_student(self, s):
        with _lock:
            if s.id in self.students:
                raise ValueError(f"Student {s.id} already exists")
            self.students[s.id] = s

    def get_student(self, sid):
        s = self.students.get(sid)
        return None if (s is None or s.deleted) else s

    def update_student(self, sid, patch):
        s = self.get_student(sid)
        if not s:
            return None
        for f in ("fullName", "email", "year"):
            if f in patch:
                setattr(s, f, int(patch[f]) if f == "year" else patch[f])
        return s

    def delete_student(self, sid):
        s = self.students.get(sid)
        if not s:
            return False
        s.deleted = True
        return True

    def list_students(self):
        return [s for s in self.students.values() if not s.deleted]

    def add_course(self, c):
        with _lock:
            if c.id in self.courses:
                raise ValueError(f"Course {c.id} already exists")
            self.courses[c.id] = c

    def get_course(self, cid):
        c = self.courses.get(cid)
        return None if (c is None or c.deleted) else c

    def update_course(self, cid, patch):
        c = self.get_course(cid)
        if not c:
            return None
        for f in ("title", "credits", "capacity"):
            if f in patch:
                c.__setattr__(f, int(patch[f]) if f in ("credits", "capacity") else patch[f])
        return c

    def delete_course(self, cid):
        c = self.courses.get(cid)
        if not c:
            return False
        c.deleted = True
        return True

    def list_courses(self):
        return [c for c in self.courses.values() if not c.deleted]

    def enroll(self, sid, cid):
        s = self.get_student(sid)
        c = self.get_course(cid)
        if not s or not c:
            raise LookupError("Student or course not found")
        if sid in c.student_ids:
            raise ValueError("Already enrolled")
        if len(c.student_ids) >= c.capacity:
            raise RuntimeError("Course is full")
        c.student_ids.append(sid)
        c._popularity += 1
        s.course_ids.append(cid)
        s._history += 1

    def drop(self, sid, cid):
        s = self.get_student(sid)
        c = self.get_course(cid)
        if not s or not c:
            raise LookupError("Student or course not found")
        if sid not in c.student_ids:
            raise ValueError("Not enrolled")
        c.student_ids.remove(sid)
        s.course_ids.remove(cid)


storage = Storage()

storage.add_course(Course("CS101", "Введение в программирование", 5, 30))
storage.add_course(Course("DB201", "Базы данных", 4, 20))
storage.add_student(Student("S-ADMIN", "Смирнов Артем Сергеевич", "smirnov-as@isuct.ru", 3))
storage.add_student(Student("S-001", "Петров Иван Иванович", "ivan_petrov@isuct.ru", 2))
storage.add_student(Student("S-002", "Смирнова Анна Викторовна", "anna_smirnova@isuct.ru", 1))

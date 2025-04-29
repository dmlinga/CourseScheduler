from django.db import models

# ─────────────────────────────────────────────
# 👨‍🏫 Instructor
# ─────────────────────────────────────────────

class Instructor(models.Model):
    name = models.CharField(max_length=100)  # e.g., Dr. Feng

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
# 🏫 Location
# ─────────────────────────────────────────────

class Location(models.Model):
    building_name = models.CharField(max_length=100)  # e.g., BHSN
    room_number = models.CharField(max_length=10)     # e.g., 224

    class Meta:
        unique_together = ('building_name', 'room_number')

    def __str__(self):
        return f"{self.building_name} {self.room_number}"


# ─────────────────────────────────────────────
# 📘 Course
# ─────────────────────────────────────────────

class Course(models.Model):
    course_name = models.CharField(max_length=100)               # e.g., Software Engineering
    course_code = models.CharField(max_length=10, unique=True)   # e.g., CS330
    credit_hours = models.PositiveIntegerField()                 # e.g., 3

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


# ─────────────────────────────────────────────
# 🧾 Section
# ─────────────────────────────────────────────

DAY_OPTIONS = [
    ('M', 'Monday'),
    ('T', 'Tuesday'),
    ('W', 'Wednesday'),
    ('Th', 'Thursday'),
    ('F', 'Friday'),
]

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    section_number = models.CharField(max_length=10)  # e.g., 01
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    frequency_per_week = models.PositiveIntegerField(help_text="e.g., 3 for M, W, F")
    
    # Preferred schedule
    days_of_week = models.CharField(max_length=20, help_text="E.g., M,W,F")
    start_time = models.TimeField()  # e.g., 09:00
    end_time = models.TimeField()    # e.g., 10:00

    class Meta:
        unique_together = ('course', 'section_number')

    def __str__(self):
        return f"{self.course.course_code} - Section {self.section_number}"

    def get_schedule_summary(self):
        return {
            "Course": str(self.course),
            "Section": self.section_number,
            "Instructor": str(self.instructor),
            "Days": self.days_of_week,
            "Time": f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}",
            "Location": str(self.location),
            "Frequency": self.frequency_per_week
        }

    def conflicts_with(self, other_section):
        """Check if this section conflicts with another based on time, day, and location."""
        if self.location != other_section.location:
            return False

        self_days = set(self.days_of_week.split(','))
        other_days = set(other_section.days_of_week.split(','))

        if not self_days.intersection(other_days):
            return False

        # Time overlap: start < other end AND end > other start
        return self.start_time < other_section.end_time and self.end_time > other_section.start_time




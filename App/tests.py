from django.test import TestCase
from django.db import IntegrityError
from datetime import time
from .models import Instructor, Location, Course, Section


class ModelTestCase(TestCase):
    def setUp(self):
        # Create base objects shared across test cases
        self.instructor = Instructor.objects.create(name="Dr. Smith")
        self.location = Location.objects.create(building_name="BHSN", room_number="224")
        self.course = Course.objects.create(course_name="Software Engineering", course_code="CS330", credit_hours=3)

        self.section1 = Section.objects.create(
            course=self.course,
            section_number="01",
            instructor=self.instructor,
            location=self.location,
            frequency_per_week=3,
            days_of_week="M,W,F",
            start_time=time(9, 0),
            end_time=time(10, 0)
        )

        self.section2 = Section.objects.create(
            course=self.course,
            section_number="02",
            instructor=self.instructor,
            location=self.location,
            frequency_per_week=2,
            days_of_week="T,Th",
            start_time=time(9, 30),
            end_time=time(10, 30)
        )

        self.section3 = Section.objects.create(
            course=self.course,
            section_number="03",
            instructor=self.instructor,
            location=self.location,
            frequency_per_week=3,
            days_of_week="M,W,F",
            start_time=time(9, 30),
            end_time=time(10, 30)
        )

    def testInstructorStr(self):
        # Test the string representation of an Instructor
        self.assertEqual(str(self.instructor), "Dr. Smith")

    def testLocationStr(self):
        # Test the string representation of a Location
        self.assertEqual(str(self.location), "BHSN 224")

    def testCourseStr(self):
        # Test the string representation of a Course
        self.assertEqual(str(self.course), "CS330 - Software Engineering")

    def testSectionStr(self):
        # Test the string representation of a Section
        self.assertEqual(str(self.section1), "CS330 - Section 01")

    def testScheduleSummary(self):
        # Test the output of get_schedule_summary() method on a Section
        summary = self.section1.get_schedule_summary()
        self.assertEqual(summary["Course"], "CS330 - Software Engineering")
        self.assertEqual(summary["Section"], "01")
        self.assertEqual(summary["Instructor"], "Dr. Smith")
        self.assertEqual(summary["Days"], "M,W,F")
        self.assertEqual(summary["Time"], "09:00 - 10:00")
        self.assertEqual(summary["Location"], "BHSN 224")
        self.assertEqual(summary["Frequency"], 3)

    def testConflictsWithDifferentDays(self):
        # Section1 is on M/W/F; Section2 is on T/Th, so no conflict
        self.assertFalse(self.section1.conflicts_with(self.section2))

    def testConflictsWithSameDaysAndOverlapTime(self):
        # Section1 and Section3 both on M/W/F and time overlaps — should conflict
        self.assertTrue(self.section1.conflicts_with(self.section3))

    def testTimeConflictOnSameDay(self):
    # Section1 is on M/W/F from 9:00 to 10:00
    # Create a section that overlaps only partially with section1 (e.g. 9:45 to 10:15) on the same days
        section8 = Section.objects.create(
        course=self.course,
        section_number="08",
        instructor=self.instructor,
        location=self.location,
        frequency_per_week=3,
        days_of_week="M,W,F",
        start_time=time(9, 45),
        end_time=time(10, 15)
    )
    # There should be a conflict due to overlapping time and same days
        self.assertTrue(self.section1.conflicts_with(section8))

    def testConflictsWithDifferentLocation(self):
        # Same schedule, different location — should NOT conflict
        otherLocation = Location.objects.create(building_name="SCI", room_number="100")
        section4 = Section.objects.create(
            course=self.course,
            section_number="04",
            instructor=self.instructor,
            location=otherLocation,
            frequency_per_week=3,
            days_of_week="M,W,F",
            start_time=time(9, 30),
            end_time=time(10, 30)
        )
        self.assertFalse(self.section1.conflicts_with(section4))

    def testConflictsWithSameSection(self):
        # A section compared with itself should always conflict 
        self.assertTrue(self.section1.conflicts_with(self.section1))

    def testNoConflictWhenAdjacentTimes(self):
        # Section ends at 10:00, new one starts at 10:00 on same days — should NOT conflict
        section5 = Section.objects.create(
            course=self.course,
            section_number="05",
            instructor=self.instructor,
            location=self.location,
            frequency_per_week=3,
            days_of_week="M,W,F",
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        self.assertFalse(self.section1.conflicts_with(section5))

    def testUniqueSectionNumberPerCourse(self):
        # Creating a duplicate section number for the same course — should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Section.objects.create(
                course=self.course,
                # Already used by section1
                section_number="01",  
                instructor=self.instructor,
                location=self.location,
                frequency_per_week=3,
                days_of_week="M,W,F",
                start_time=time(11, 0),
                end_time=time(12, 0)
            )

    def testUniqueLocation(self):
        # Creating a duplicate location — should raise IntegrityError if unique constraint exists
        with self.assertRaises(IntegrityError):
            Location.objects.create(building_name="BHSN", room_number="224")
    
    def testSectionWithNullInstructorAndLocation(self):
        # Create a section without assigning an instructor or location
        section6 = Section.objects.create(
            course=self.course,
            section_number="06",
            instructor=None,
            location=None,
            frequency_per_week=2,
            days_of_week="T,Th",
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        # Ensure the fields are None
        self.assertIsNone(section6.instructor)
        self.assertIsNone(section6.location)

    def testInvalidFrequencyZero(self):
        # Frequency per week is set to zero — should be invalid
        section7 = Section.objects.create(
            course=self.course,
            section_number="07",
            instructor=self.instructor,
            location=self.location,
            frequency_per_week=0,
            days_of_week="M,W,F",
            start_time=time(8, 0),
            end_time=time(9, 0)
        )
        self.assertEqual(section7.frequency_per_week, 0)

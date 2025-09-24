from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import random
import string

# Custom User Model
class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=10, unique=False, blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions_set", blank=True)

    def generate_referral_code(self):
        self.referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.save()

# Course Model
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Course fee
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    for_teacher=models.BooleanField(default=False)

    def __str__(self):
        return self.title

class CoursePayment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Fix: Renamed from 'test' to 'course'
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    amount = models.CharField(max_length=255)
    payment_status = models.CharField(
        max_length=20, choices=[("Pending", "Pending"), ("Paid", "Paid")], default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.payment_status}"


# Enrollment Model
class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    payment_status = models.BooleanField(default=False)  # True if payment is successful
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({'Paid' if self.payment_status else 'Pending'})"

# Lecture Model
class Lecture(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=255)
    video_url = models.URLField()  # Ensure correct embed URL is stored
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Convert regular YouTube link to embed link
        if "watch?v=" in self.video_url:
            self.video_url = self.video_url.replace("watch?v=", "embed/")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.course.title})"

# Assignment Model
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Assignment Submission Model
class AssignmentSubmission(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="submissions")
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    answer_text = models.TextField(blank=True, null=True)
    answer_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)

    # New fields for scoring
    score = models.IntegerField(null=True, blank=True)  # Numeric score (e.g., 0-100)
    is_correct = models.BooleanField(null=True, blank=True)  # Correct/Incorrect option

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} ({'Graded' if self.score is not None else 'Pending'})"

# E-Book Model
class Ebook(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='ebooks/')
    course = models.ForeignKey(Course, related_name="ebooks", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# For-Sale E-Book Model
class For_Sale_Ebook(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='sale_ebooks/')
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title

# E-Book Purchase Model
class EBookPurchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ebook_purchases")
    ebook = models.ForeignKey(For_Sale_Ebook, on_delete=models.CASCADE, related_name="purchases")
    purchased_at = models.DateTimeField(auto_now_add=True)

# Teacher-Student Relationship Model
class TeacherStudent(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="students")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="assigned_teacher")

    def __str__(self):
        return f"{self.teacher.username} - {self.student.username}"



from multiselectfield import MultiSelectField

from django.db import models
from django.contrib.auth import get_user_model
from multiselectfield import MultiSelectField

CustomUser = get_user_model()

class Test(models.Model):
    OPERATION_CHOICES = [
        ('+', 'Addition'),
        ('-', 'Subtraction'),
        ('*', 'Multiplication'),
        ('/', 'Division'),
    ]

    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tests")
    title = models.CharField(max_length=255)
    num_questions = models.IntegerField(default=10)
    range_min = models.IntegerField(default=-10)
    range_max = models.IntegerField(default=10)
    num_items_per_question = models.IntegerField(default=5)
    operations = MultiSelectField(choices=OPERATION_CHOICES)  
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)  # ✅ Add price field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (By {self.teacher.username})"

class TestPayment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    amount = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Paid", "Paid")], default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.test.title} - {self.payment_status}"

# Question Model (Generated Randomly)
import random
import operator

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=255)
    answer = models.FloatField()

    @staticmethod
    def generate_question(test):
        OPERATION_FUNCTIONS = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
        }

        selected_operations = test.operations  # Get selected operations
        numbers = [random.randint(test.range_min, test.range_max) for _ in range(test.num_items_per_question)]
        ops = [random.choice(selected_operations) for _ in range(test.num_items_per_question - 1)]

        question_text = str(numbers[0])
        answer = numbers[0]

        for i in range(1, test.num_items_per_question):
            question_text += f" {ops[i-1]} {numbers[i]}"
            answer = OPERATION_FUNCTIONS[ops[i-1]](answer, numbers[i])

        return question_text, round(answer, 2)

# Result Model
class Result(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="results")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="results")
    score = models.IntegerField()
    time_taken = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.test.title} (Score: {self.score})"


from django.db import models
from django.contrib.auth.models import User

class Test_time_self(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    num_questions = models.IntegerField()
    time_limit = models.IntegerField()  # Time limit in minutes

class Question_time_self(models.Model):
    test = models.ForeignKey(Test_time_self, on_delete=models.CASCADE, related_name="questions")  
    question_text = models.TextField()
    answer = models.CharField(max_length=255)


class StudentTestAttempt(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey(Test_time_self, on_delete=models.CASCADE)  # ✅ Corrected ForeignKey
    score = models.FloatField()
    time_taken = models.IntegerField()  # Time in seconds
    timestamp = models.DateTimeField(auto_now_add=True)


class TestPayment_self(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey(Test_time_self, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    amount = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Paid", "Paid")], default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.test.title} - {self.payment_status}"

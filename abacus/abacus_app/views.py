from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def teacher_dashboard(request):
    if not request.user.is_teacher:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('teacher_login')

    students = CustomUser.objects.filter(referral_code=request.user.referral_code)
    print("Students found:", students)  # Debugging

    # Fetch assignments submitted by these students
    assignments = AssignmentSubmission.objects.filter(student__in=students)

    # Fetch test results submitted by these students
    test_results = Result.objects.filter(student__in=students)
    test_results_2 = StudentTestAttempt.objects.filter(student__in=students)

    print("Test Results Found:", test_results)  # Debugging

    return render(request, 'abacus_app/teacher_dashboard.html', {
        'students': students,
        'assignments': assignments,
        'test_results': test_results,"test_results_2":test_results_2
    })

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
import random
import string

CustomUser = get_user_model()

def register_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'abacus_app/register_teacher.html')

        teacher = CustomUser.objects.create(
            username=username,
            email=email,
            password=make_password(password),  # Hash password before saving
            is_teacher=True  # Mark as teacher
        )
        
        teacher.generate_referral_code()  # Generate referral code after creating user

        messages.success(request, "Teacher registered successfully!")
        return redirect('teacher_login')

    return render(request, 'abacus_app/register_teacher.html')

@login_required
def teacher_courses(request):
    if not request.user.is_teacher:
        return redirect("home")
    
    courses = Course.objects.filter(available_for_teachers=True)
    return render(request, "abacus_app/teacher_courses.html", {"courses": courses})




from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CoursePayment, CustomUser, Question_time_self, TeacherStudent, Test_time_self, TestPayment_self
from .forms import CustomUserRegistrationForm

def user_register(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            referral_code = form.cleaned_data.get("referral_code")

            if referral_code:
                teacher = CustomUser.objects.filter(referral_code=referral_code, is_teacher=True).first()
                if teacher:
                    TeacherStudent.objects.create(teacher=teacher, student=user)
                    messages.success(request, f"Registered successfully! Linked to teacher: {teacher.username}.")
                else:
                    messages.warning(request, "Invalid referral code. Proceeding without a teacher.")

            login(request, user)
            return redirect("dashboard")  # Redirect to dashboard after registration

    else:
        form = CustomUserRegistrationForm()

    return render(request, "abacus_app/register.html", {"form": form})



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Use .get() to avoid KeyError
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'abacus_app/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')  # Redirect to dashboard after login
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'abacus_app/login.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, AssignmentSubmission

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from .models import CustomUser

from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CustomUser  # Ensure your CustomUser model is imported

from django.contrib.auth import login, get_user_model
from django.contrib import messages

CustomUser = get_user_model()

def teacher_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return render(request, 'abacus_app/teacher_login.html')

        if not user.check_password(password):
            messages.error(request, "Invalid username or password.")
            return render(request, 'abacus_app/teacher_login.html')

        if not user.is_teacher:
            messages.error(request, "You are not authorized to access this section.")
            return render(request, 'abacus_app/teacher_login.html')

        # Log in the teacher
        login(request, user)
        messages.success(request, "Login successful!")
        return redirect('teacher_dashboard')  # Redirect to teacher's dashboard

    return render(request, 'abacus_app/teacher_login.html')

# Student Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# Dashboard (Only accessible after login)
@login_required
def dashboard(request):
    return render(request, 'abacus_app/dashboard.html')


from django.shortcuts import render, get_object_or_404
from .models import For_Sale_Ebook, Lecture, Assignment

# Dashboard View
def dashboard(request, lecture_id=None):
    lectures = Lecture.objects.all()
    assignments = Assignment.objects.all()

    # Show the first lecture by default if none is selected
    selected_lecture = lectures.first() if not lecture_id else get_object_or_404(Lecture, id=lecture_id)

    return render(request, 'abacus_app/dashboard.html', {
        'lectures': lectures,
        'assignments': assignments,
        'selected_lecture': selected_lecture
    })


from django.shortcuts import render, get_object_or_404
from .models import Assignment

def assignment_list(request):
    assignments = Assignment.objects.all()
    return render(request, 'abacus_app/assignments.html', {'assignments': assignments})

from django.shortcuts import render, get_object_or_404
from .models import Assignment, Course

def assignment_detail(request, course_id, assignment_id):
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    return render(request, "abacus_app/assignment_detail.html", {
        "assignment": assignment,
        "course": course,
    })


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Assignment, AssignmentSubmission

# Function to check if user is a superuser
def is_superuser(user):
    return user.is_superuser

@login_required
# @user_passes_test(is_superuser)  # Restrict access to superusers only
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)

    return render(request, "abacus_app/assignment_submissions.html", {"assignment": assignment, "submissions": submissions})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Assignment, AssignmentSubmission
from .forms import AssignmentSubmissionForm

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if the user has already submitted
    submission = AssignmentSubmission.objects.filter(student=request.user, assignment=assignment).first()

    if submission and submission.is_submitted:
        return render(request, 'abacus_app/already_submitted.html', {'assignment': assignment,'submission': submission})

    # if timezone.now().date() > assignment.due_date:
    #     return render(request, 'abacus_app/submission_closed.html', {'assignment': assignment})

    if request.method == "POST":
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.assignment = assignment
            submission.is_submitted = True  # Lock submission
            submission.save()
            return redirect('dashboard')
    else:
        form = AssignmentSubmissionForm()

    return render(request, 'abacus_app/submit_assignment.html', {
        'assignment': assignment, 
        'form': form
    })

import razorpay
from django.shortcuts import render
from django.conf import settings
from abacus_app.models import Test, TestPayment

def buy_test(request, test_id):
    test = Test.objects.get(id=test_id)
    amount = 300  # Fixed price in INR

    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Order
    order_data = {
        "amount": amount * 100,  # Razorpay accepts amount in paise
        "currency": "INR",
        "payment_capture": "1"
    }
    order = client.order.create(data=order_data)

    # Store Order Details in DB
    test_payment = TestPayment.objects.create(
        student=request.user,
        test=test,
        razorpay_order_id=order['id'],  # Store order ID
        amount=amount,
        payment_status="Pending"
    )

    return render(request, "abacus_app/buy_test.html", {
        "test": test,
        "amount": amount,
        "order_id": order["id"],  # Ensure this is passed to the template
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# @csrf_exempt
# def verify_payment(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             print("Received JSON:", data)  # 🔍 Debugging Line

#             razorpay_order_id = data.get("razorpay_order_id")
#             razorpay_payment_id = data.get("razorpay_payment_id")
#             razorpay_signature = data.get("razorpay_signature")

#             if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
#                 return JsonResponse({"success": False, "error": "Missing payment details"}, status=400)

#             return JsonResponse({"success": True})

#         except json.JSONDecodeError:
#             return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from abacus_app.models import Test, Question, TestPayment

@login_required
def access_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    # Check if student has paid
    payment = TestPayment.objects.filter(student=request.user, test=test, payment_status="Paid").first()
    
    if not payment:
        messages.error(request, "You need to pay ₹300 to access this test.")
        return redirect("buy_test", test_id=test.id)
    if 'test_start_time' not in request.session:
        request.session['test_start_time'] = now().isoformat()  # Store time as string (ISO format)

    # Fetch questions for this test
    questions = Question.objects.filter(test=test)  # Ensure Question model has a ForeignKey to Test
    print(questions)
    return render(request, "abacus_app/test_page.html", {"test": test, "questions": questions})

@login_required
def access_test_self(request, test_id):
    test = get_object_or_404(Test_time_self, id=test_id)
    
    # Check if student has paid
    payment = TestPayment_self.objects.filter(student=request.user, test=test, payment_status="Paid").first()
    
    if not payment:
        messages.error(request, "You need to pay ₹300 to access this test.")
        return redirect("buy_test", test_id=test.id)
    if 'test_start_time' not in request.session:
        request.session['test_start_time'] = now().isoformat()  # Store time as string (ISO format)

    # Fetch questions for this test
    questions = Question_time_self.objects.filter(test=test)  # Ensure Question model has a ForeignKey to Test
    print(questions)
    return render(request, "abacus_app/test_page.html", {"test": test, "questions": questions})



@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)

    return render(request, "abacus_app/assignment_submissions.html", {"assignment": assignment, "submissions": submissions})


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import AssignmentSubmission


def check_assignments(request):
    submissions = AssignmentSubmission.objects.all()
    return render(request, 'abacus_app/check_assignments.html', {'submissions': submissions})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import AssignmentSubmission

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import AssignmentSubmission

def is_teacher(user):
    return user.is_authenticated and hasattr(user, 'is_teacher') and user.is_teacher

from django.core.exceptions import PermissionDenied

# @user_passes_test(is_teacher)
def grade_assignment(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)

    # Ensure the teacher can only grade students registered under their referral code
    if submission.student.referral_code != request.user.referral_code:
        messages.error(request, "You are not authorized to grade this student's assignment.")
        return redirect('teacher_dashboard')  # Redirect to teacher dashboard

    if request.method == "POST":
        score = request.POST.get("score")
        is_correct = request.POST.get("is_correct") == "on"  # Checkbox handling

        if score and score.isdigit():
            submission.score = int(score)
        else:
            messages.error(request, "Invalid score input. Please enter a valid number.")
            return redirect('teacher_dashboard')

        submission.is_correct = is_correct
        submission.save()

        messages.success(request, "Assignment graded successfully!")
        return redirect('teacher_dashboard')

    return render(request, 'abacus_app/grade_assignment.html', {'submission': submission})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Course, Enrollment

@login_required
def course_list(request):
    if request.user.is_teacher:
        # Teachers see only courses meant for teachers
        courses = Course.objects.filter(for_teacher=True)
    else:
        # Students see only courses meant for students
        courses = Course.objects.filter(for_teacher=False)

    enrollments = Enrollment.objects.filter(student=request.user, payment_status=True).values_list('course_id', flat=True)

    return render(request, 'abacus_app/course_list.html', {'courses': courses, 'enrolled_courses': enrollments})


import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Course, Enrollment

# Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Create Razorpay order
    order_amount = int(course.price * 100)  # Razorpay accepts amount in paise
    order_currency = 'INR'
    payment_order = razorpay_client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'payment_capture': '1'
    })
    
    return render(request, 'abacus_app/checkout.html', {
        'course': course,
        'order_id': payment_order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID
    })

@login_required
def checkout_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Create Razorpay order
    order_amount = int(course.price * 100)  # Convert to paise
    order_currency = "INR"
    payment_order = razorpay_client.order.create(
        {"amount": order_amount, "currency": order_currency, "payment_capture": "1"}
    )

    # Save the payment record in the database
    CoursePayment.objects.create(
        student=request.user,
        course=course,
        razorpay_order_id=payment_order["id"],
        amount=course.price,
        payment_status="Pending",
    )

    return render(
        request,
        "abacus_app/checkout_course.html",
        {
            "course": course,
            "order_id": payment_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
        },
    )



@csrf_exempt
def verify_payment_course(request):
    if request.method == "POST":
        try:
            print("Raw request body:", request.body.decode("utf-8"))

            data = json.loads(request.body)
            print("Parsed JSON:", data)

            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")

            if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
                return JsonResponse({"success": False, "error": "Missing payment details"}, status=400)

            # Verify the payment signature
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }

            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({"success": False, "error": "Signature verification failed"}, status=400)

            # Find the payment in the database
            try:
                payment = CoursePayment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.payment_status = "Paid"
                payment.save()

                # Ensure the student is enrolled after successful payment
                enrollment, created = Enrollment.objects.get_or_create(
                    student=payment.student, course=payment.course
                )
                enrollment.payment_status = True
                enrollment.razorpay_payment_id = razorpay_payment_id  # Store payment ID
                enrollment.save()

                return JsonResponse({"success": True})
            except CoursePayment.DoesNotExist:
                return JsonResponse({"success": False, "error": "Payment record not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from abacus_app.models import TestPayment

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        try:
            # Print raw request data for debugging
            print("Raw request body:", request.body.decode('utf-8'))  

            data = json.loads(request.body)  # Parse JSON data
            print("Parsed JSON:", data)  # Log parsed data

            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")

            if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
                return JsonResponse({"success": False, "error": "Missing payment details"}, status=400)

            # Find the payment record in the database
            try:
                payment = TestPayment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.payment_status = "Paid"
                payment.save()
                return JsonResponse({"success": True})
            except TestPayment.DoesNotExist:
                return JsonResponse({"success": False, "error": "Payment record not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)


from django.shortcuts import render, get_object_or_404
from .models import Course, Enrollment, Lecture

from django.shortcuts import render, get_object_or_404
from .models import Course, Lecture, Assignment

from django.shortcuts import render, get_object_or_404
from .models import Course, Lecture, Assignment, Ebook

def view_ebook(request, ebook_id):
    """
    View to display an E-Book in a new page.
    """
    ebook = get_object_or_404(Ebook, id=ebook_id)
    return render(request, 'abacus_app/view_ebook.html', {'ebook': ebook})

@login_required
def my_ebooks(request):
    purchased_books = EBookPurchase.objects.filter(user=request.user)
    return render(request, "abacus_app/my_ebooks.html", {"purchased_books": purchased_books})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import razorpay
from .models import Ebook, EBookPurchase



def ebook_list(request):
    ebooks = For_Sale_Ebook.objects.all()
    return render(request, "abacus_app/ebook_list.html", {"ebooks": ebooks})

import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import For_Sale_Ebook, EBookPurchase

@login_required
def purchase_ebook(request, ebook_id):
    ebook = get_object_or_404(For_Sale_Ebook, id=ebook_id)

    # Check if user already purchased
    if EBookPurchase.objects.filter(user=request.user, ebook=ebook).exists():
        messages.info(request, "You have already purchased this book.")
        return redirect("ebook_detail", ebook_id=ebook.id)

    # Initialize Razorpay Client with settings
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Debug API keys
    print("RAZORPAY_KEY_ID:", settings.RAZORPAY_KEY_ID)
    print("RAZORPAY_KEY_SECRET:", settings.RAZORPAY_KEY_SECRET)

    # Create Razorpay order
    try:
        amount_in_paisa = int(float(ebook.price) * 100)  # Convert to paisa
        print("Amount (paisa):", amount_in_paisa)  # Debugging

        payment = client.order.create({
            "amount": amount_in_paisa,
            "currency": "INR",
            "payment_capture": "1"
        })
        print("Razorpay Order Created:", payment)  # Debugging

    except razorpay.errors.BadRequestError as e:
        print("Razorpay Error:", str(e))
        messages.error(request, "Payment failed. Please try again.")
        return redirect("ebook_list")

    return render(request, "abacus_app/purchase_ebook.html", {
        "ebook": ebook,
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })


from django.http import JsonResponse

@login_required
def confirm_purchase(request, ebook_id):
    if request.method == "POST":
        ebook = get_object_or_404(For_Sale_Ebook, id=ebook_id)

        # Save purchase record
        EBookPurchase.objects.create(user=request.user, ebook=ebook)

        messages.success(request, "Payment successful! You can now access the book.")
        return redirect("ebook_detail", ebook.id)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def ebook_detail(request, ebook_id):
    ebook = get_object_or_404(For_Sale_Ebook, id=ebook_id)

    # Check if the user has purchased the book
    if not EBookPurchase.objects.filter(user=request.user, ebook=ebook).exists():
        messages.error(request, "You need to purchase this book first.")
        return redirect("ebook_list")

    return render(request, "abacus_app/view_ebook.html", {"ebook": ebook})


def course_detail(request, course_id):
    """
    View to display course details with lectures, assignments, and e-books.
    By default, it selects the first lecture (if available).
    """
    course = get_object_or_404(Course, id=course_id)
    lectures = course.lectures.all()
    assignments = course.assignments.all()
    ebooks = Ebook.objects.filter(course=course)  # Fetch E-Books related to the course

    selected_lecture = lectures.first() if lectures else None  # Default first lecture

    return render(request, 'abacus_app/course_detail.html', {
        'course': course,
        'lectures': lectures,
        'assignments': assignments,
        'ebooks': ebooks,  # Pass E-Books to the template
        'selected_lecture': selected_lecture,
    })

def view_lecture(request, course_id, lecture_id):
    course = get_object_or_404(Course, id=course_id)
    selected_lecture = get_object_or_404(Lecture, id=lecture_id, course=course)

    return render(request, 'abacus_app/course_detail.html', {
        'course': course,
        'lectures': course.lectures.all(),
        'assignments': course.assignments.all(),
        'selected_lecture': selected_lecture,
    })

def assignment_detail(request, course_id, assignment_id):
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)

    return render(request, 'abacus_app/assignment_detail.html', {
        'course': course,
        'assignment': assignment,
    })


# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render, get_object_or_404, redirect
# from .models import AssignmentSubmission

#  # Only superusers/staff can access this view
# def grade_assignment(request, submission_id):
#     submission = get_object_or_404(AssignmentSubmission, id=submission_id)

#     if request.method == "POST":
#         score = request.POST.get("score")
#         is_correct = request.POST.get("is_correct") == "on"  # Checkbox handling

#         if score.isdigit():
#             submission.score = int(score)
#             submission.is_correct = is_correct
#             submission.save()

#         return redirect("check_assignments")  # Redirect to assignment list

#     return render(request, "abacus_app/grade_assignment.html", {"submission": submission})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Test, Result
from .forms import TestForm  # Assuming you have a form for test creation
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Test, Question, Result, CustomUser, TeacherStudent
import random
import time

@login_required
def create_test(request):
    if request.method == "POST":
        title = request.POST.get("title")
        num_questions = int(request.POST.get("num_questions"))
        range_min = int(request.POST.get("range_min"))
        range_max = int(request.POST.get("range_max"))
        num_items_per_question = int(request.POST.get("num_items_per_question"))
        operations = request.POST.getlist("operations")  # Get selected operations

        test = Test.objects.create(
            teacher=request.user,
            title=title,
            num_questions=num_questions,
            range_min=range_min,
            range_max=range_max,
            num_items_per_question=num_items_per_question,
            operations=operations,
        )

        # Generate questions
        for _ in range(num_questions):
            question_text, answer = Question.generate_question(test)
            Question.objects.create(test=test, question_text=question_text, answer=answer)

        return redirect("teacher_dashboard")

    return render(request, "abacus_app/create_test.html")



@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()
    
    if request.method == "POST":
        start_time = int(request.POST.get("start_time"))
        end_time = int(time.time())
        total_time = end_time - start_time
        score = 0

        for question in questions:
            user_answer = int(request.POST.get(f"question_{question.id}", 0))
            if user_answer == question.answer:
                score += 1

        Result.objects.create(student=request.user, test=test, score=score, time_taken=total_time)

        return redirect("view_result", test_id=test.id)

    return render(request, "abacus_app/take_test.html", {"test": test, "questions": questions, "start_time": int(time.time())})

@login_required
def view_result(request, test_id):
    result = get_object_or_404(Result, student=request.user, test_id=test_id)
    return render(request, "abacus_app/result.html", {"result": result})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Test, Test_time_self, Result, CustomUser

@login_required
def test_list(request):
    user = request.user
    print(f"Logged-in User: {user.username}, Is Teacher: {user.is_teacher}")

    # Ensure these variables are always defined
    given_tests_ = []  # Default empty list

    if user.is_teacher:
        # Fetch tests created by the logged-in teacher
        tests = Test.objects.filter(teacher=user)
        tests_2 = Test_time_self.objects.filter(teacher=user)
        given_tests = []  # Teachers don't give tests

        print(f"Teacher {user.username} - Created Tests: {tests}")
        print(f"Teacher {user.username} - Created Self-Timed Tests: {tests_2}")

    else:
        # Get the student's referral code
        user_cur = CustomUser.objects.get(username=user.username)
        referral_code = user_cur.referral_code
        print(f"Student {user.username} - Referral Code: {referral_code}")

        # Find the teacher with this referral code
        teacher = CustomUser.objects.filter(referral_code=referral_code, is_teacher=True).first()
        print(f"Teacher found using referral code '{referral_code}': {teacher}")

        if teacher:
            # Fetch tests created by this teacher
            tests = Test.objects.filter(teacher=teacher)
            tests_2 = Test_time_self.objects.filter(teacher=teacher)

            print(f"Tests assigned by teacher {teacher.username}: {tests}")
            print(f"Self-Timed Tests assigned by teacher {teacher.username}: {tests_2}")
        else:
            tests = Test.objects.none()  # No matching teacher
            tests_2 = Test_time_self.objects.none()
            print("No teacher found for this referral code. No tests assigned.")

        # Get tests the student has already taken
        given_tests = Result.objects.filter(student=user).values_list('test_id', flat=True)
        given_tests_ = StudentTestAttempt.objects.filter(student=user).values_list('test_id', flat=True)
        
        print(f"Student {user.username} - Given Tests: {given_tests}")

    return render(request, "abacus_app/test_list.html", {
        'tests': tests,
        'tests_2': tests_2,
        'given_tests': given_tests,
        'given_tests_2': given_tests_,  # Now always defined
    })



@login_required
def view_test_results(request, test_id):
    test = get_object_or_404(Test, id=test_id)

    # Ensure only the teacher who created the test can view results
    if request.user.is_teacher and request.user != test.teacher:
        return JsonResponse({'error': 'You can only see results of tests you created'}, status=403)

    results = Result.objects.filter(test=test).select_related('student')

    return render(request, "abacus_app/test_results.html", {'test': test, 'results': results})


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Test_time_self, StudentTestAttempt

@login_required
def view_test_results_self(request, test_id):
    test = get_object_or_404(Test_time_self, id=test_id)

    # Ensure only the teacher who created the test can view results
    if request.user.is_teacher and request.user != test.teacher:
        return JsonResponse({'error': 'You can only see results of tests you created'}, status=403)

    # Fetch test results from StudentTestAttempt model
    results = StudentTestAttempt.objects.filter(test=test).select_related('student')

    return render(request, "abacus_app/test_results.html", {'test': test, 'results': results})

# @login_required
# def submit_test(request, test_id):
#     test = get_object_or_404(Test, id=test_id)

#     if request.method == "POST":
#         score = request.POST.get("score")  # Assume score is calculated in frontend/backend

#         # Save test result
#         Result.objects.create(
#             student=request.user,
#             test=test,
#             score=score
#         )

#         return redirect('test_list')

#     return render(request, "abacus_app/submit_test.html", {'test': test})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from abacus_app.models import Test, Question, Result, TestPayment
from django.utils.timezone import now
import datetime

from django.utils.timezone import now
from datetime import datetime

@login_required
def submit_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    # Check if student has paid
    payment = TestPayment.objects.filter(student=request.user, test=test, payment_status="Paid").first()
    if not payment:
        messages.error(request, "You need to pay ₹300 to access this test.")
        return redirect("buy_test", test_id=test.id)

    # Fetch test questions
    questions = Question.objects.filter(test=test)

    correct_answers = 0
    total_questions = questions.count()

    # Retrieve start time from session
    start_time_str = request.session.get('test_start_time', None)
    
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str)  # Convert stored string to datetime object
            time_taken = (now() - start_time).seconds  # Calculate time taken in seconds
        except ValueError:
            time_taken = 0  # If there's an error in conversion, default to 0
    else:
        time_taken = 0  # Default to zero if session data is missing (should not happen if properly set)

    print(f"Test Started At: {start_time}, Submitted At: {now()}, Time Taken: {time_taken} seconds")  # Debugging

    # Check answers
    for question in questions:
        user_answer = request.POST.get(f'question_{question.id}', "").strip()

        try:
            user_answer = int(user_answer)  # Convert user input to an integer
        except ValueError:
            user_answer = None  # Handle case where user leaves the answer blank

        correct_answer = question.answer  # Already stored as an integer

        if user_answer == correct_answer:
            correct_answers += 1

    # Calculate score
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0

    # Save result in the database
    result = Result.objects.create(
        student=request.user,
        test=test,
        score=score,
        time_taken=time_taken,
        completed_at=now()
    )

    # Clear session variable after submission
    if 'test_start_time' in request.session:
        del request.session['test_start_time']

    messages.success(request, "Test submitted successfully!")
    return redirect("view_test_results", test_id=test.id)

    test = get_object_or_404(Test, id=test_id)
    
    # Check if student has paid
    payment = TestPayment.objects.filter(student=request.user, test=test, payment_status="Paid").first()
    if not payment:
        messages.error(request, "You need to pay ₹300 to access this test.")
        return redirect("buy_test", test_id=test.id)

    # Fetch test questions
    questions = Question.objects.filter(test=test)

    correct_answers = 0
    total_questions = questions.count()
    
    start_time = request.session.get('test_start_time', now())  # Get start time
    time_taken = (now() - start_time).seconds  # Calculate time taken

    for question in questions:
        user_answer = request.POST.get(f'question_{question.id}', "").strip()  # Remove `.lower()` since it's a number
        correct_answer = str(question.answer).strip()  # Convert to string

        print(f"User Answer: {user_answer}, Correct Answer: {correct_answer}")  # Debugging

        if user_answer == correct_answer:
            correct_answers += 1

    

    # Calculate score
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    print(score)
    # Save result in database
    result = Result.objects.create(
        student=request.user,
        test=test,
        score=score,
        time_taken=time_taken,
        completed_at=now()
    )

    messages.success(request, "Test submitted successfully!")
    return redirect("view_test_results", test_id=test.id)  # ✅ Correct



@login_required
def test_result(request, result_id):
    result = get_object_or_404(Result, id=result_id, student=request.user)
    return render(request, "abacus_app/test_result.html", {"result": result})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Test, Question, StudentTestAttempt
import json

@login_required
def create_test_time_self(request):
    if request.method == "POST":
        title = request.POST.get("title")
        num_questions = int(request.POST.get("num_questions"))
        time_limit = int(request.POST.get("time_limit"))  # Time in minutes

        # Create test instance
        test = Test_time_self.objects.create(
            teacher=request.user,
            title=title,
            num_questions=num_questions,
            time_limit=time_limit,
        )

        # Save questions and answers
        for i in range(num_questions):
            question_text = request.POST.get(f"question_{i}")
            answer = request.POST.get(f"answer_{i}")
            Question_time_self.objects.create(test=test, question_text=question_text, answer=answer)

        return redirect("teacher_dashboard")

    return render(request, "abacus_app/create_test_time_self.html")

@login_required
def start_test_time_self(request, test_id):
    test = Test_time_self.objects.get(id=test_id)
    questions = test.questions.all()  # Now using the related_name
    return render(request, "abacus_app/start_test_time_self.html", {"test": test, "questions": questions})

import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Test_time_self, Question_time_self, StudentTestAttempt

import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Test_time_self, StudentTestAttempt

@login_required
def submit_test_time_self(request, test_id):
    if request.method == "POST":
        test = get_object_or_404(Test_time_self, id=test_id)
        student = request.user
        data = json.loads(request.body)
        student_answers = data.get("answers", {})
        time_taken = data.get("time_taken", 0)  # Get time taken from request

        # Calculate score
        correct_answers = 0
        for question in test.questions.all():  # Using related_name="questions"
            user_answer = student_answers.get(str(question.id), "").strip()
            if user_answer.lower() == question.answer.lower().strip():
                correct_answers += 1

        score = (correct_answers / test.num_questions) * 100

        # Save attempt with time taken
        StudentTestAttempt.objects.create(student=student, test=test, score=score, time_taken=time_taken)

        return JsonResponse({"message": "Test submitted successfully!", "score": score, "time_taken": time_taken})

    return JsonResponse({"error": "Invalid request"}, status=400)


def buy_test_time_self(request, test_id):
    test = Test_time_self.objects.get(id=test_id)
    amount = 300  # Fixed price in INR

    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Order
    order_data = {
        "amount": amount * 100,  # Razorpay accepts amount in paise
        "currency": "INR",
        "payment_capture": "1"
    }
    order = client.order.create(data=order_data)

    # Store Order Details in DB
    test_payment = TestPayment_self.objects.create(
        student=request.user,
        test=test,
        razorpay_order_id=order['id'],  # Store order ID
        amount=amount,
        payment_status="Pending"
    )

    return render(request, "abacus_app/buy_test_self.html", {
        "test": test,
        "amount": amount,
        "order_id": order["id"],  # Ensure this is passed to the template
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })

@csrf_exempt
def verify_payment_self(request):
    if request.method == "POST":
        try:
            print("Raw request body:", request.body.decode("utf-8"))

            data = json.loads(request.body)
            print("Parsed JSON:", data)

            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")

            if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
                return JsonResponse({"success": False, "error": "Missing payment details"}, status=400)

            # Verify Razorpay Signature
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }

            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({"success": False, "error": "Signature verification failed"}, status=400)

            # 🔹 Ensure Correct Model Reference 🔹
            try:
                payment = TestPayment_self.objects.get(razorpay_order_id=razorpay_order_id)
                payment.payment_status = "Paid"
                payment.save()

                return JsonResponse({"success": True})
            except TestPayment_self.DoesNotExist:
                return JsonResponse({"success": False, "error": "Payment record not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)


import random
import operator
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Operator mapping
OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

quiz_config = {}

def quiz_setup(request):
    """View to configure the quiz"""
    if request.method == "POST":
        global quiz_config
        quiz_config = {
            'num_questions': int(request.POST.get('num_questions', 10)),
            'min_range': int(request.POST.get('min_range', 0)),
            'max_range': int(request.POST.get('max_range', 9)),
            'length': int(request.POST.get('length', 5)),
            'time_per_question': int(request.POST.get('time_per_question', 10)),
            'operators': request.POST.getlist('operators')
        }
        return JsonResponse({'status': 'Quiz Configured'})

    return render(request, 'abacus_app/quiz_setup.html')

def generate_question():
    """Generate a math expression"""
    numbers = [random.randint(quiz_config['min_range'], quiz_config['max_range']) for _ in range(quiz_config['length'])]
    ops = [random.choice(quiz_config['operators']) for _ in range(quiz_config['length'] - 1)]
    
    expression_parts = []
    for i in range(len(numbers)):
        expression_parts.append(str(numbers[i]))
        if i < len(ops):
            expression_parts.append(ops[i])
    
    full_expression = ' '.join(expression_parts)
    try:
        answer = eval(full_expression)
    except ZeroDivisionError:
        return generate_question()

    return {'expression_parts': expression_parts, 'answer': answer}

def start_quiz(request):
    """Start the quiz"""
    if not quiz_config:
        return JsonResponse({'error': 'Quiz not configured'})

    quiz_questions = [generate_question() for _ in range(quiz_config['num_questions'])]
    request.session['quiz_questions'] = quiz_questions
    request.session['current_index'] = 0
    request.session['score'] = 0

    return render(request, 'abacus_app/quiz.html', {'time_per_question': quiz_config['time_per_question']})

@csrf_exempt
def quiz_question(request):
    """Serve questions one by one"""
    if request.method == 'POST':
        user_answer = request.POST.get('answer')
        index = request.session.get('current_index', 0)
        quiz_questions = request.session.get('quiz_questions', [])

        if index < len(quiz_questions):
            correct_answer = quiz_questions[index]['answer']
            if str(user_answer) == str(correct_answer):
                request.session['score'] += 1

        request.session['current_index'] = index + 1

    index = request.session.get('current_index', 0)
    quiz_questions = request.session.get('quiz_questions', [])

    if index >= len(quiz_questions):
        return JsonResponse({'finished': True, 'score': request.session.get('score', 0)})

    return JsonResponse({'question_parts': quiz_questions[index]['expression_parts']})

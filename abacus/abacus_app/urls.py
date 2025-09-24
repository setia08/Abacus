from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('', views.course_list, name='dashboard'),  # Dashboard after login
    path('lecture/<int:lecture_id>/', views.dashboard, name='view_lecture'),
    path('assignments/', views.assignment_list, name='assignments'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/checkout/', views.checkout, name='checkout'),
    path('courses/<int:course_id>/checkout_course/', views.checkout_course, name='checkout_course'),
    # path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/checkout/', views.checkout, name='checkout'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    path('verify_payment_course/', views.verify_payment_course, name='verify_payment_course'),
    path('courses/<int:course_id>/lectures/<int:lecture_id>/', views.view_lecture, name='view_lecture'),
    path('courses/<int:course_id>/assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('check-assignments/', views.check_assignments, name='check_assignments'),
    path('grade-assignment/<int:submission_id>/', views.grade_assignment, name='grade_assignment'),
    path('ebook/<int:ebook_id>/', views.view_ebook, name='view_ebook'),  # New URL
    path('ebooks/', views.ebook_list, name='ebook_list'),
    path('ebooks/<int:ebook_id>/', views.ebook_detail, name='ebook_detail'),
    path('ebooks/<int:ebook_id>/purchase/', views.purchase_ebook, name='purchase_ebook'),
    path('ebooks/<int:ebook_id>/confirm/', views.confirm_purchase, name='confirm_purchase'),
    path('my-ebooks/', views.my_ebooks, name='my_ebooks'),
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher_login", views.teacher_login, name="teacher_login"),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path("teacher/courses/", views.teacher_courses, name="teacher_courses"),
    path('check-assignments/', views.check_assignments, name='check_assignments'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('assignment/<int:submission_id>/grade/', views.grade_assignment, name='grade_assignment'),
    path('tests/create/', views.create_test, name='create_test'),
    path('tests/', views.test_list, name='test_list'),
    path('tests/<int:test_id>/results/', views.view_test_results, name='view_test_results'),
    path('tests-self/<int:test_id>/results/', views.view_test_results_self, name='view_test_results_self'),
    
    path('tests/<int:test_id>/submit/', views.submit_test, name='submit_test'),
    path("create_test/", views.create_test, name="create_test"),
    path("take_test/<int:test_id>/", views.take_test, name="take_test"),
    path("result/<int:test_id>/", views.view_result, name="view_result"),
    path("buy_test/<int:test_id>/", views.buy_test, name="buy_test"),
    path("buy_test_time_self/<int:test_id>/", views.buy_test_time_self, name="buy_test_time_self"),
    path("verify_payment_self/", views.verify_payment_self, name="verify_payment_self"),
    path("verify_payment/", views.verify_payment, name="verify_payment"),
    path("test/<int:test_id>/", views.access_test, name="access_test"),
    path("test_self/<int:test_id>/", views.access_test_self, name="access_test_self"),
    path("create-test-time-self/", views.create_test_time_self, name="create_test_time_self"),
    path("start-test-time-self/<int:test_id>/", views.start_test_time_self, name="start_test_time_self"),
    path("submit-test-time-self/<int:test_id>/", views.submit_test_time_self, name="submit_test_time_self"),
    path('quiz_setup/', views.quiz_setup, name='quiz_setup'),
    path('start_quiz/', views.start_quiz, name='start_quiz'),
    path('quiz_question/', views.quiz_question, name='quiz_question'),
]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
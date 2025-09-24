from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AssignmentSubmission, EBookPurchase, Ebook, For_Sale_Ebook, Lecture, Assignment, Course, Enrollment, Question, Question_time_self, Result, StudentTestAttempt, TeacherStudent, Test, Test_time_self, TestPayment

# ✅ Register `CustomUser` correctly
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_teacher', 'referral_code', 'is_staff', 'is_active')  # Add referral_code
    search_fields = ('username', 'email')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'referral_code')}),  # Add referral_code here
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_teacher', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_teacher', 'referral_code')}
        ),
    )

# ✅ Register other models
admin.site.register(Lecture)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Ebook)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(EBookPurchase)
admin.site.register(For_Sale_Ebook)
admin.site.register(TeacherStudent)
admin.site.register(Result)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(TestPayment)
admin.site.register(Question_time_self)
admin.site.register(Test_time_self)
admin.site.register(StudentTestAttempt)
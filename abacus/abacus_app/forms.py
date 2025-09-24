from django import forms
from .models import AssignmentSubmission, Result

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['answer_text', 'answer_file']


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserRegistrationForm(UserCreationForm):
    referral_code = forms.CharField(required=False, label="Enter Referral Code (If Any)")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'referral_code']


from django import forms
from .models import Test, Result

# Form for Creating a Test (Only for Teachers)
class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title']  # Add other fields if necessary

# Form for Submitting a Test Result (For Students)
class TestSubmissionForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['score']  # Adjust based on how students submit answers

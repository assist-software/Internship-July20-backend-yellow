from rest_auth.views import LoginView
from django.http import HttpResponseRedirect, HttpResponse
from .forms import PasswordResetForm
from django.core.mail import send_mail
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from users.models import User


class CustomLoginView(LoginView):
    def get_response(self):
        original_response = super().get_response()
        mydata = {"message": "Success!", "status": "success"}
        original_response.data.update(mydata)
        return original_response


class PasswordResetView(CreateView):
    def get_email(request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            model = User
            recipient = form.cleaned_data('email')
            user = model.objects.get(email=recipient)
            if user.is_active:
                password = model.objects.make_random_password()
                user.set_password(password)
                user.save()

                # Email
                message = ('Dear customer {}. You requested a password reset.'
                           'Your newly generated password is : {}'
                           'Use this new password to login in your account.'
                           'Club Management team.'.format(user.get_full_name(), password))
                send_mail('Password Reset Club Management', message, 'test.club.django@gmail.com', recipient)
            else:
                raise ValueError('The user either does not exist or is not active anymore.')
            return HttpResponseRedirect('templates.Password-Reset-Confirmed-template.html')
        else:
            return HttpResponse("Password reset.")

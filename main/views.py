from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login,logout, get_user_model
from django.contrib.auth.backends import ModelBackend
from .forms import LoginForm

User = get_user_model()


class RegisterView(View):
    template_name = 'register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        # phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')

        if not first_name:
            messages.error(request, "First name is required.")
            return redirect('/register')

        # if not phone_number:
        #     messages.error(request, "Phone number is required.")
        #     return redirect('/register')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('/register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email already exists")
            return redirect('/register')

        is_first_user = not User.objects.exists()

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password1),
            is_superuser=is_first_user,
            is_staff=is_first_user
        )
        user.save()
        login(request, user)

        return redirect('/login')


class LoginView(View):
    template = "login.html"
    context = {}

    def get(self, request):
        form = LoginForm()
        self.context.update({'form': form})
        return render(request, self.template, self.context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = EmailBackend.authenticate(request,email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/profile')
            else:
                messages.error(request, "Username or password is wrong !")
        print(">>>>>>>>>>>>>>>>>>>>>>>")
        return redirect('/login')




class Profile(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request):
        user = request.user
        context = {
            'firstname': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        photo = request.FILES.get('photo')

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        if email:
            if not User.objects.filter(email=email).exclude(pk=user.pk).exists():
                user.email = email
            else:
                messages.error(request, "This email is already taken.")
                return redirect('profile')

        if photo:
            user.profile_picture = photo

        user.save()
        messages.success(request, "Your profile has been updated!")
        return redirect('profile',)


class EmailBackend(ModelBackend):
    def authenticate(self, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
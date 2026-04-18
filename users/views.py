from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import CreateUserForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from .token import account_activation_token
from .forms import LoginForm
from .forms import UserUpdateForm
from django.contrib.auth import authenticate, login, logout

def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Verify your email to activate your account'
            message = render_to_string('users/email-verification.html', {
                'user': user,
                'domain': current_site.domain,       # ✅ fixed typo: 'domaim' → 'domain'
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # ✅ removed .encode()
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return redirect('email-verification-sent')

    return render(request, 'users/register.html', {'form': form})


def email_verifcation(request, uidb64, token):
    try:
        unique_id = urlsafe_base64_decode(uidb64).decode('utf-8')  # ✅ clean string '7'
        user = User.objects.get(pk=unique_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('email-verification-success')
    else:
        return redirect('email-verification-failed')
    

def email_verification_sent(request):
    return render(request, 'users/email-verification-sent.html')

def email_verification_success(request):
    return render(request, 'users/email-verification-success.html')

def email_verification_failed(request):
    return render(request, 'users/email-verification-failed.html')


def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password) 
            if user is not None:
                login(request, user)
                return redirect('index')
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('index')


def profile(request):
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('index')
    user_form = UserUpdateForm(instance=request.user)
    
        
    return render(request, 'users/profile.html', {'user_form': user_form})

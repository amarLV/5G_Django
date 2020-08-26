from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages 
from .forms import SignUpForm, EditProfileForm
import cv2
import sys
import numpy

def gps(request):
	return render(request,'authenticate/gps.html', {})

def home(request):
	return render(request, 'authenticate/home.html', {})

def login_user(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ('You Have Been Logged In!'))
			return redirect('home')

		else:
			messages.success(request, ('Error Logging In - Please Try Again...'))
			return redirect('login')
	else:
		return render(request, 'authenticate/login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ('You Have Been Logged Out...'))
	return redirect('home')

def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ('You Have Registered...'))
			return redirect('home')
	else:
		form = SignUpForm()
	
	context = {'form': form}
	return render(request, 'authenticate/register.html', context)



def edit_profile(request):
	if request.method == 'POST':
		form = EditProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, ('You Have Edited Your Profile...'))
			return redirect('home')
	else:
		form = EditProfileForm(instance=request.user)
	
	context = {'form': form}
	return render(request, 'authenticate/edit_profile.html', context)

def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(data=request.POST, user=request.user)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, form.user)
			messages.success(request, ('You Have Edited Your Password...'))
			return redirect('home')
	else:
		form = PasswordChangeForm(user=request.user)
	
	context = {'form': form}
	return render(request, 'authenticate/change_password.html', context)


def get_frame(post):
    #this section is scrapped code, can be ignored or removed
    '''
    post.startVideo()
    while True:
        encodedImage = post.getFrame()
        if encodedImage is None:
            continue
        stringData = encodedImage.tostring()
        yield (b'--frame\r\n' b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')

    '''
    video = Video()
    video.start(post.port)

    while True:
        #print('try ' + post.port)
        if not video.frame_available():
            continue
        frame = video.frame()
        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue
        yield (b'--frame\r\n' b'Content-Type: text/plain\r\n\r\n' + encodedImage.tostring() + b'\r\n')

#this is the call that can be reached from flask for data streaming
#passes the given post down to the get_frame() method
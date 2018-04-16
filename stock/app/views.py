from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def index(request):
	''''if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('trade'))
	else:'''
	return render(request, 'index.html')

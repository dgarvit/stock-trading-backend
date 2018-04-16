from django.shortcuts import render
from datetime import datetime

def index(request):
	today = datetime.now().strftime("%Y-%m-%d")
	return render(request, 'index.html', {
		'today': today,
		})

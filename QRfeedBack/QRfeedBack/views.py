from django.shortcuts import render
from django.http import HttpResponse

def main_page_view(request):
    return render(request, 'main.html')
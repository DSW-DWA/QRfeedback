from django.shortcuts import render


def main_page_view(request):
    return render(request, 'main.html')


def submit_form(request):
    return render(request, 'success.html')


def qr_form(request):
    return render(request, 'qrgen.html')

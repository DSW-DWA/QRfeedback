from django.shortcuts import render
from django.http import Http404


def main_page_view(request):
    address = request.GET.get('address', '')
    encrypted_data = request.GET.get('encrypted_data', '')
    if address == '' or encrypted_data == '':
        raise Http404()
    return render(request, 'main.html')


def submit_form(request):
    return render(request, 'success.html')


def qr_form(request):
    return render(request, 'qrgen.html')

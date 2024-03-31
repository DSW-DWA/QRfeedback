from django.shortcuts import render
from django.http import HttpResponseBadRequest


def main_page_view(request):
    address = request.GET.get("address", "").strip()
    encrypted_data = request.GET.get("encrypted_data", "").strip()
    if address == "" or encrypted_data == "":
        return HttpResponseBadRequest(b"<h1>Malformed request</h1>")
    return render(request, "main.html")


def submit_form(request):
    return render(request, "success.html")


def qr_form(request):
    return render(request, "qrgen.html")

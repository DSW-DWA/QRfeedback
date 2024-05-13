from django.shortcuts import render, redirect


def main_page_view(request):
    address = request.GET.get("address", "").strip()
    encrypted_data = request.GET.get("encrypted_data", "").strip()
    if address == "" or encrypted_data == "":
        return redirect("qr_gen")
    return render(request, "main.html")


def submit_form(request):
    return render(request, "success.html")


def qr_form(request):
    return render(request, "qrgen.html")

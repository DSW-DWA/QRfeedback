from django.shortcuts import render


def main_page_view(request):
    response = render(request, 'main.html')

    address = request.GET.get('address', '')
    tg_session_id = request.GET.get('encrypted_data', '')
    if address != '' and tg_session_id != '':
        response.set_cookie('address', address)
        response.set_cookie('tg_session_id', tg_session_id)

    return response


def submit_form(request):
    return render(request, 'success.html')


def qr_form(request):
    return render(request, 'qrgen.html')

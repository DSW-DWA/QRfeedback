from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from qrcode import QRCode


# POST http://127.0.0.1:8000/api/qr_generator/
# {
#     "url": "google.com"
# }

@api_view(['POST'])
def qr_generator(request):
    if request.method == 'POST':
        if 'url' in request.data:
            url = request.data['url']
        else:
            return JsonResponse({'error': 'Invalid URL'})

        qr_code = QRCode()
        qr_code.add_data(url)
        qr_code.make()

        img = qr_code.make_image()
        response = HttpResponse(content_type='image/png')
        img.save(response, 'PNG')

        return response

    return JsonResponse({'error': 'Invalid request method'})

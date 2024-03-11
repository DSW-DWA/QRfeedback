from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
import segno
import io

from .custom_renderers import PNGRenderer
from .models import Review
from .serializers import ReviewSerializer, QRSerializer


class ReviewList(APIView):
    parser_classes = [FormParser, MultiPartParser]

    def get(self, request):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ReviewDetail(APIView):
    def get(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    

class QRGenerator(APIView):
    renderer_classes = [PNGRenderer]

    def post(self, request):
        serializer = QRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        buffer = io.BytesIO()
        url, scale, border = serializer.data['url'], serializer.data['scale'], serializer.data['border']
        segno.make_qr(url).save(buffer, kind='png', scale=scale, border=border)
        img = buffer.getvalue()

        return Response(img)
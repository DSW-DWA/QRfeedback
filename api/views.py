from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
import segno
import io
import logging

from .custom_renderers import PNGRenderer
from .models import Review
from .serializers import ReviewSerializer, QRSerializer

logger = logging.getLogger(__name__)

class ReviewList(APIView):
    parser_classes = [FormParser, MultiPartParser]

    def get(self, request):
        try:
            reviews = Review.objects.all()
            serializer = ReviewSerializer(reviews, many=True)
            serializer.is_valid(raise_exception=True)

            logger.info('Reviews loaded')

            return Response(serializer.data)
        except Exception as ex:
            logger.error(ex)

            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            serializer = ReviewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info('Review created')

            return Response(serializer.data)
        except Exception as ex:
            logger.error(ex)

            return Response(status=status.HTTP_400_BAD_REQUEST)


class ReviewDetail(APIView):
    def get(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            serializer = ReviewSerializer(review)

            logger.info('Review loaded')

            return Response(serializer.data)
        except Review.DoesNotExist:
            logger.error('Review not found')

            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(ex)

            return Response(status=status.HTTP_400_BAD_REQUEST)
    

class QRGenerator(APIView):
    renderer_classes = [PNGRenderer]

    def post(self, request):
        try :
            serializer = QRSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            buffer = io.BytesIO()
            url, scale, border = serializer.data['url'], serializer.data['scale'], serializer.data['border']
            segno.make_qr(url).save(buffer, kind='png', scale=scale, border=border)
            img = buffer.getvalue()

            logger.info('QR generated')
            return Response(img, status= status.HTTP_200_OK, content_type='image/png')
        except Exception as ex:
            logger.error(ex)
            
            return Response(status=status.HTTP_400_BAD_REQUEST)
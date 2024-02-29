from rest_framework import serializers
from .models import Review, Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_url']


class ReviewSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    pub_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ['review_text', 'pub_date', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images')
        review = Review.objects.create(
            review_text=validated_data['review_text'])
        for img in images:
            Image.objects.create(review=review, **img)
        return review

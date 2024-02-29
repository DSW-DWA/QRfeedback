from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    pub_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'review_text', 'pub_date', 'image']

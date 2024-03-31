from rest_framework import serializers
from .models import Review, Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["image"]


class ReviewSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    pub_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "review_text", "pub_date", "images", "address", "tg_session_id"]

    def to_representation(self, instance):
        repr_data = {
            "id": instance.id,
            "review_text": instance.review_text,
            "pub_date": instance.pub_date,
            "address": instance.address,
            "tg_session_id": instance.tg_session_id,
        }

        images = instance.images.values_list("image")
        repr_data["images"] = [i[0] for i in images]

        return repr_data

    def to_internal_value(self, data):
        imagesData = []
        if "images" in data:
            images = data.pop("images")
            for imgData in images:
                imagesData.append({"image": imgData})
        if "review_text" in data:
            review_text = data["review_text"]
        if "address" in data:
            address = data["address"]
        if "tg_session_id" in data:
            tg_session_id = data["tg_session_id"].strip('"')

        processed_data = {
            "review_text": review_text,
            "images": imagesData,
            "address": address,
            "tg_session_id": tg_session_id,
        }

        return super().to_internal_value(processed_data)

    def create(self, validated_data):
        review = Review.objects.create(
            review_text=validated_data["review_text"],
            address=validated_data["address"],
            tg_session_id=validated_data["tg_session_id"],
        )

        for img in validated_data["images"]:
            Image.objects.create(review=review, image=img["image"])

        return review


class QRSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    scale = serializers.IntegerField(required=False, default=10)
    border = serializers.IntegerField(required=False, default=5)

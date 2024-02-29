from django.db import models
import os


def get_upload_path(instance, filename):
    return os.path.join('images', f'review_{instance.review.pk}', filename)


class Review(models.Model):
    review_text = models.TextField(blank=False, null=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        str_repr = ' '.join(self.review_text.split()[:5])
        if len(self.review_text) > len(str_repr):
            return str_repr + '...'
        return str_repr


class Image(models.Model):
    review = models.ForeignKey(
        Review, related_name='images', on_delete=models.CASCADE)
    image_url = models.ImageField(
        upload_to=get_upload_path, blank=True, null=True)

    def __str__(self):
        return self.image_url.url

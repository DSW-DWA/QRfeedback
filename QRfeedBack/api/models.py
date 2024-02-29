from django.db import models


class Review(models.Model):
    review_text = models.TextField(blank=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        str_repr = ' '.join(self.review_text.split()[:5])
        if len(self.review_text) > len(str_repr):
            return str_repr + '...'
        return str_repr


class Image(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images', blank=False)

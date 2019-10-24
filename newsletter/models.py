from django.db import models
from django.shortcuts import reverse


class NewsLetter(models.Model):
    GENDERS = (('a', 'Άνδρας'), ('b', 'Γυναίκα'))

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True)
    confirm = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    def get_edit_url(self):
        return reverse('newsletter:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('newsletter:delete', kwargs={'pk': self.id})
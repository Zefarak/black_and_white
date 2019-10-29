from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from datetime import datetime, timedelta
User = get_user_model()

CURRENCY = settings.CURRENCY
from catalogue.models import Product


class Subscribe(models.Model):
    CATEGORY_CHOICES = {
        ('a', 'Μέρες'),
        ('b', 'Εβδομαδες'),
        ('c', 'Μηνες')
    }
    active = models.BooleanField(default=True, verbose_name='Κατάσταση')
    title = models.CharField(unique=True, max_length=240, verbose_name='Τίτλος')
    value = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Αξία Καλαθιού')
    counter = models.PositiveIntegerField(default=0, verbose_name='Ποσότητα')
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, verbose_name='Κατηγορία')
    ordering = models.PositiveIntegerField(default=1, verbose_name='Ταξινόμηση')
    products = models.ManyToManyField(Product, blank=True, null=True)
    uses = models.IntegerField(default=1, verbose_name='Χρησεις')

    class Meta:
        ordering = ['ordering']

    def save(self, *args, **kwargs):
        self.uses = self.counter if self.category == 'a' else self.counter*7 if self.category == 'b' else self.counter*30
        super(Subscribe, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('subscribe:subscribe_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('subscribe:subscribe_delete_view', kwargs={'pk': self.id})

    def tag_value(self):
        return f'{self.value} {CURRENCY}'


class UserSubscribe(models.Model):
    active = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_subscribes')
    subscription = models.ForeignKey(Subscribe, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    uses = models.IntegerField(default=1)
    
    def save(self, *args, **kwargs):
        self.active = True if self.uses > 0 else False
        super(UserSubscribe, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} --> {self.subscription.title}'

    def duration(self):
        return f'{self.date_start} -- {self.date_end}'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def get_edit_url(self):
        return reverse('subscribe:user_subscribe_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('subscribe:user_subscribe_delete_view', kwargs={'pk': self.id})

    @staticmethod
    def check_active_subscription(user):
        sub_qs = UserSubscribe.objects.filter(user=user, active=True)
        return sub_qs.exists()

    @staticmethod
    def update_subscription(instance):
        sub_category = instance.subscription
        value = int(sub_category.value)
        added_date = timedelta(days=value) if sub_category.category == 'a' else timedelta(weeks=value) if sub_category.category == 'b' else timedelta(months=value)
        instance.date_start = datetime.now().date()
        instance.date_end = datetime.now().date() + added_date
        instance.value = sub_category.value
        
        instance.save()

    @staticmethod
    def create_subscription(subscription, user):
        sub_category = subscription.category
        new_object = UserSubscribe.objects.create(user=user, subscription=subscription, value=subscription.value)
        new_object.date_start = datetime.now().date()
        new_object.date_end = datetime.now().date()
        new_object.date_end += timedelta(days=sub_category.value) if sub_category == 'a' else timedelta(weeks=sub_category.value) if sub_category == 'b' else timedelta(months=sub_category.value)
        days = new_object.date_end - new_object.date_start
        new_object.uses = subscription.counter
        new_object.save()
        return True


@receiver(post_save, sender=UserSubscribe)
def update_blank_fields(sender, instance, created, **kwargs):
    if created:
        UserSubscribe.update_subscription(instance)



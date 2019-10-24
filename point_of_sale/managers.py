from django.db import models
from datetime import datetime


class RetailQuerySet(models.QuerySet):

    def sells(self, date_start=None, date_end=None):
        if date_start and date_end:
            return self.filter(order_type__in=['r', 'e'],
                               date_expired__range=[date_start, date_end]
                               )
        return self.filter(order_type__in=['r', 'e'])

    def new_orders(self):
        return self.sells().filter(status='1')

    def not_paid_sells(self):
        return self.sells().filter(is_paid=False)

    def eshop_orders(self):
        return self.sells().filter(order_type='e')

    def eshop_orders_filter_by_date(self, date_start, date_end):
        if date_end > date_start:
            return self.eshop_orders().filter(date_expired__range=[date_start, date_end])
        return self.eshop_orders()

    def eshop_orders_by_user(self, user):
        return self.eshop_orders().filter(user=user)

    def today_sells(self):
        return self.sells().filter(date_expired=datetime.now())

    def current_month_sells(self):
        first_day = datetime.today().replace(day=1)
        last_day = datetime.today()
        return self.sells().filter(date_expired__range=[first_day, last_day])

    def returns(self, date_start, date_end):
        return self.filter(order_type='b',
                           date_expired__range=[date_start, date_end]
                           )

    def export_invoices(self, date_start, date_end):
        return self.filter(order_type='wr',
                           date_expired__range=[date_start, date_end]
                           )

    def sells_by_date_range(self, date_start, date_end):
        return self.sells().filter(date_expired__range=[date_start, date_end])

    def all_by_date_range(self, date_start, date_end):
        return self.filter(date_expired__range=[date_start, date_end])


class OrderManager(models.Manager):

    def get_queryset(self):
        return RetailQuerySet(self.model, using=self._db)


class OrderItemManager(models.Manager):
    pass

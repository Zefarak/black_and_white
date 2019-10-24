from django.apps import AppConfig


class VoucherConfig(AppConfig):
    name = 'voucher'

    def ready(self):
        import voucher.signals



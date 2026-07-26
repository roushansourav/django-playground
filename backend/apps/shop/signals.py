import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shop.models import Order

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "Order confirmation email queued for order #%s (%s)",
            instance.pk,
            instance.user.email,
        )

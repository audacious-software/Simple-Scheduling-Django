# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

import importlib

from django.conf import settings
from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from ...models import ScheduledItem

class Command(BaseCommand):
    help = 'Query packages to update schedule.'

    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **options):
        for app in settings.INSTALLED_APPS:
            try:
                app_module = importlib.import_module('.simple_scheduling_api', package=app)

                events = app_module.fetch_scheduled_events()

                ScheduledItem.objects.upsert_scheduled_events(events)
            except ImportError:
                pass
            except AttributeError:
                pass

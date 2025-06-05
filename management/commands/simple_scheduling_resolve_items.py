# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

import importlib
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from ...models import ScheduledItem

from ... import SchedulingError

class Command(BaseCommand):
    help = 'Translates scheduled items into actoins.'

    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **options):
        now = timezone.now()

        for scheduled_item in ScheduledItem.objects.filter(outcome='pending', when__lte=now, resolved=None):
            for app in settings.INSTALLED_APPS:
                try:
                    app_module = importlib.import_module('.simple_scheduling_api', package=app)

                    executed = app_module.execute_scheduled_item(scheduled_item.action, scheduled_item.when, scheduled_item.context)

                    if executed:
                        scheduled_item.resolved = now
                        scheduled_item.outcome = 'success'
                        scheduled_item.save()

                        continue
                except SchedulingError:
                    scheduled_item.resolved = now
                    scheduled_item.outcome = 'failure'
                    scheduled_item.outcome_log = traceback.format_exc()
                    scheduled_item.save()
                except ImportError:
                    pass
                except AttributeError:
                    pass

# pylint: disable=line-too-long

import hashlib
import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone

SCHEDULED_ITEM_OUTCOMES = (
    ('pending', 'Pending',),
    ('pause', 'Paused',),
    ('success', 'Success',),
    ('failure', 'Failure',),
    ('cancel', 'Canceled',),
)

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

def dict_fingerprint(dict_obj):
    encoder = hashlib.sha256()
    encoder.update(json.dumps(dict_obj, sort_keys=True, cls=DjangoJSONEncoder).encode('utf-8'))

    return encoder.hexdigest()

class ScheduledItemManager(models.Manager): # pylint: disable=too-few-public-methods
    def upsert_scheduled_events(self, events): # pylint: disable=too-many-arguments, no-self-use
        for event in events:
            event_key = event.get('event_key', None)
            event_action = event.get('action', None)
            event_time = event.get('when', None)

            if (None in (event_key, event_action, event_time)) is False:
                if event_action == 'simple_scheduling.cancel':
                    for match in ScheduledItem.objects.filter(identifier=event_key):
                        match.cancel(context=event)
                else:
                    event_obj = ScheduledItem()

                    event_obj.update_from_dict(event)
            else:
                logger.error('Malformed event: %s', json.dumps(event))

class ScheduledItem(models.Model): # pylint:disable=too-many-instance-attributes
    objects = ScheduledItemManager()

    identifier = models.CharField(max_length=1024, unique=True)
    action = models.CharField(max_length=1024)
    when = models.DateTimeField()
    resolved = models.DateTimeField(null=True, blank=True)

    context = models.JSONField(default=dict, blank=True)

    outcome = models.CharField(max_length=4096, choices=SCHEDULED_ITEM_OUTCOMES, default='pending')
    outcome_log = models.TextField(max_length=(1024 * 1024), null=True, blank=True)

    fingerprint = models.CharField(max_length=1024)

    def update_from_dict(self, event_dict):
        event_key = event_dict.get('event_key', None)
        event_time = event_dict.get('when', None)
        event_action = event_dict.get('action', None)

        if (None in (event_key, event_time, event_action)) is False:
            fingerprint = dict_fingerprint(event_dict)

            match = ScheduledItem.objects.filter(identifier=event_key).first()

            if match is None:
                match = self

            if match.outcome in ('pending', 'paused'): # Don't updated items that already happened
                if fingerprint != match.fingerprint:
                    match.identifier = event_key
                    match.action = event_action
                    match.when = event_time

                    match.context = event_dict.get('context', {})

                    match.fingerprint = fingerprint

                    match.save()

    def cancel(self, context=None):
        now = timezone.now()

        if self.outcome in ('pending', 'pause',):
            self.outcome = 'cancel'
            self.outcome_log = 'Cancelled on %s.\n\nContext: %s' % (now.isoformat(), json.dumps(context, indent=2))
            self.resolved = now
            self.save()

    def resolve(self, when=timezone.now, success=True, outcome_log=None):
        if self.outcome == 'pending': # Don't resolve items that aren't already pending
            self.resolved = when

            if success:
                self.outcome = 'success'
            else:
                self.outcome = 'failure'

            self.outcome_log = outcome_log

            self.save()

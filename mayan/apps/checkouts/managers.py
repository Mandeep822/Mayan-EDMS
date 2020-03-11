from __future__ import absolute_import, unicode_literals

import logging

from django.apps import apps
from django.db import models, transaction
from django.utils.timezone import now

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document

from .events import (
    event_document_auto_check_in, event_document_check_in,
    event_document_forceful_check_in
)
from .exceptions import DocumentNotCheckedOut, NewDocumentVersionNotAllowed
from .literals import STATE_CHECKED_OUT, STATE_CHECKED_IN
from .permissions import (
    permission_document_check_in, permission_document_check_in_override
)

logger = logging.getLogger(__name__)


class DocumentCheckoutBusinessLogicManager(models.Manager):
    def check_in_document(self, document, user=None):
        # Convert any document submodel to the parent model class
        queryset = document._meta.default_manager.filter(pk=document.pk)

        if not self.filter(document__pk__in=queryset).exists():
            raise DocumentNotCheckedOut

        return self.check_in_documents(queryset=queryset, user=user)

    def check_in_documents(self, queryset, user=None):
        if user:
            user_document_checkouts = AccessControlList.objects.restrict_queryset(
                permission=permission_document_check_in,
                queryset=self.filter(user_id=user.pk, document__in=queryset),
                user=user
            )

            others_document_checkouts = AccessControlList.objects.restrict_queryset(
                permission=permission_document_check_in_override,
                queryset=self.exclude(user_id=user.pk, document__in=queryset),
                user=user
            )

        with transaction.atomic():
            if user:
                for checkout in user_document_checkouts:
                    event_document_check_in.commit(
                        actor=user, target=checkout.document
                    )
                    checkout.delete()

                for checkout in others_document_checkouts:
                    event_document_forceful_check_in.commit(
                        actor=user, target=checkout.document
                    )
                    checkout.delete()
            else:
                for checkout in self.filter(document__in=queryset):
                    event_document_auto_check_in.commit(
                        target=checkout.document
                    )
                    checkout.delete()


class DocumentCheckoutManager(models.Manager):
    def are_document_new_versions_allowed(self, document, user=None):
        try:
            check_out_info = self.document_check_out_info(document=document)
        except DocumentNotCheckedOut:
            return True
        else:
            return not check_out_info.block_new_version

    def check_in_expired_check_outs(self):
        for document in self.expired_check_outs():
            document.check_in()

    def check_out_document(self, document, expiration_datetime, user, block_new_version=True):
        return self.create(
            block_new_version=block_new_version, document=document,
            expiration_datetime=expiration_datetime, user=user
        )

    def checked_out_documents(self):
        CheckedOutDocument = apps.get_model(
            app_label='checkouts', model_name='CheckedOutDocument'
        )

        return CheckedOutDocument.objects.filter(
            pk__in=self.model.objects.values('document__id')
        )

    def get_check_out_info(self, document):
        try:
            return self.model.objects.get(document=document)
        except self.model.DoesNotExist:
            raise DocumentNotCheckedOut

    def get_check_out_state(self, document):
        if self.is_checked_out(document=document):
            return STATE_CHECKED_OUT
        else:
            return STATE_CHECKED_IN

    def expired_check_outs(self):
        CheckedOutDocument = apps.get_model(
            app_label='checkouts', model_name='CheckedOutDocument'
        )

        expired_list = CheckedOutDocument.objects.filter(
            pk__in=self.model.objects.filter(
                expiration_datetime__lte=now()
            ).values_list('document__pk', flat=True)
        )
        logger.debug('expired_list: %s', expired_list)
        return expired_list

    def get_by_natural_key(self, document_natural_key):
        try:
            document = Document.objects.get_by_natural_key(document_natural_key)
        except Document.DoesNotExist:
            raise self.model.DoesNotExist

        return self.get(document__pk=document.pk)

    def is_checked_out(self, document):
        return self.filter(document=document).exists()


class NewVersionBlockManager(models.Manager):
    def block(self, document):
        self.get_or_create(document=document)

    def get_by_natural_key(self, document_natural_key):
        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        try:
            document = Document.objects.get_by_natural_key(document_natural_key)
        except Document.DoesNotExist:
            raise self.model.DoesNotExist

        return self.get(document__pk=document.pk)

    def is_blocked(self, document):
        return self.filter(document=document).exists()

    def new_versions_allowed(self, document):
        if self.filter(document=document).exists():
            raise NewDocumentVersionNotAllowed

    def unblock(self, document):
        self.filter(document=document).delete()

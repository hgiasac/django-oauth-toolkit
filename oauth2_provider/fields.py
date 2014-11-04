# coding=utf-8
"""Utility fields."""
import logging
logger = logging.getLogger(__name__)

# Django imports
from django.db.models import fields
from django.conf import settings
from django.core import exceptions

from postgres.fields import json_field


class BigAutoField(fields.AutoField):
    """ Bigint auto increment field """
    def db_type(self, connection):
        if settings.DATABASE_ENGINE == 'mysql':
            return "bigint AUTO_INCREMENT"
        elif settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE[:8] == 'postgres':
            return "bigserial"
        else:
            raise NotImplemented

    def get_internal_type(self):
        return "BigAutoField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                ("This value must be a long integer.")
            )


class BigForeignKey(fields.related.ForeignKey):
    """ Foreign Key for bigint field """
    def db_type(self, connection):
        rel_field = self.rel.get_related_field()
        # next lines are the "bad tooth" in the original code:
        if (isinstance(rel_field, BigAutoField) or
           (isinstance(rel_field, BigUUIDField)) or
            (not connection.features.related_fields_match_type and
                isinstance(rel_field, fields.BigIntegerField))):
            # because it continues here in the django code:
            # return IntegerField().db_type()
            # thereby fixing any AutoField as IntegerField
            return fields.BigIntegerField().db_type(connection)
        return rel_field.db_type(connection)


class BigUUIDField(fields.AutoField):
    """ UUID auto created using bigint """
    def db_type(self, connection):
        return 'bigint DEFAULT id_generator()'

    def get_internal_type(self):
        return "BigUUIDField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                ("This value must be a long integer.")
            )


class JSONField(json_field.JSONField):
    """ Custom JSONField from Schinckel's django-postgres """

    def to_python(self, value):
        if value is None and not self.null and self.blank:
            return {}
        # Rely on psycopg2 to give us the value already converted.
        return value


class BigOneToOneField(fields.related.OneToOneField):
    """ Custom One to One field with Bigint db_type """

    def db_type(self, connection):
        return BigForeignKey.db_type(self, connection)

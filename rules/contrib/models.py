from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.db.models.base import ModelBase

from ..permissions import add_perm


class RulesModelBaseMixin:
    """
    Mixin for the metaclass of Django's Model that allows declaring object-level
    permissions in the model's Meta options.

    If set, the Meta attribute "rules_permissions" has to be a dictionary with
    permission types (like "add" or "change") as keys and predicates (like
    rules.is_staff) as values. Permissions are then registered with the rules
    framework automatically upon Model creation.

    This mixin can be used for creating custom metaclasses.
    """

    def __new__(cls, name, bases, attrs, **kwargs):
        model_meta = attrs.get("Meta")
        if hasattr(model_meta, "rules_permissions"):
            perms = model_meta.rules_permissions
            del model_meta.rules_permissions
            if not isinstance(perms, dict):
                raise ImproperlyConfigured(
                    "The rules_permissions Meta option of %s must be a dict, not %s."
                    % (name, type(perms))
                )
            perms = perms.copy()
        else:
            perms = {}

        new_class = super().__new__(cls, name, bases, attrs, **kwargs)
        new_class._meta.rules_permissions = perms
        new_class.preprocess_rules_permissions(perms)
        for perm_type, predicate in perms.items():
            add_perm(new_class.get_perm(perm_type), predicate)
        return new_class


class RulesModelBase(RulesModelBaseMixin, ModelBase):
    """
    A subclass of Django's ModelBase with the RulesModelBaseMixin mixed in.
    """


class RulesModelMixin:
    """
    A mixin for Django's Model that adds hooks for stepping into the process of
    permission registration, which are called by the metaclass implementation in
    RulesModelBaseMixin.

    Use this mixin in a custom subclass of Model in order to change its behavior.
    """

    @classmethod
    def get_perm(cls, perm_type):
        """Converts permission type ("add") to permission name ("app.add_modelname")

        :param perm_type: "add", "change", etc., or custom value
        :type  perm_type: str
        :returns str:
        """
        return "%s.%s_%s" % (cls._meta.app_label, perm_type, cls._meta.model_name)

    @classmethod
    def preprocess_rules_permissions(cls, perms):
        """May alter a permissions dict before it's processed further.

        Use this, for instance, to alter the supplied permissions or insert default
        values into the given dict.

        :param perms:
            Shallow-copied value of the rules_permissions model Meta option
        :type  perms: dict
        """


class RulesModel(RulesModelMixin, Model, metaclass=RulesModelBase):
    """
    An abstract model with RulesModelMixin mixed in, using RulesModelBase as metaclass.

    Use this as base for your models directly if you don't need to customize the
    behavior of RulesModelMixin and thus don't want to create a custom base class.
    """

    class Meta:
        abstract = True

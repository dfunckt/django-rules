from django.core.exceptions import ImproperlyConfigured, PermissionDenied


class AutoPermissionViewSetMixin:
    """
    Enforces object-level permissions in ``rest_framework.viewsets.ViewSet``,
    deriving the permission type from the particular action to be performed..

    As with ``rules.contrib.views.AutoPermissionRequiredMixin``, this only works when
    model permissions are registered using ``rules.contrib.models.RulesModelMixin``.
    """

    # Maps API actions to model permission types. None as value skips permission
    # checks for the particular action.
    # This map needs to be extended when custom actions are implemented
    # using the @action decorator.
    # Extend or replace it in subclasses like so:
    # permission_type_map = {
    #     **AutoPermissionViewSetMixin.permission_type_map,
    #     "close": "change",
    #     "reopen": "change",
    # }
    permission_type_map = {
        "create": "add",
        "destroy": "delete",
        "list": None,
        "partial_update": "change",
        "retrieve": "view",
        "update": "change",
    }

    def initial(self, *args, **kwargs):
        """Ensures user has permission to perform the requested action."""
        super().initial(*args, **kwargs)

        if not self.request.user:
            # No user, don't check permission
            return

        # Get the handler for the HTTP method in use
        try:
            if self.request.method.lower() not in self.http_method_names:
                raise AttributeError
            handler = getattr(self, self.request.method.lower())
        except AttributeError:
            # method not supported, will be denied anyway
            return

        try:
            perm_type = self.permission_type_map[self.action]
        except KeyError:
            raise ImproperlyConfigured(
                "AutoPermissionViewSetMixin tried to authorize a request with the "
                "{!r} action, but permission_type_map only contains: {!r}".format(
                    self.action, self.permission_type_map
                )
            )
        if perm_type is None:
            # Skip permission checking for this action
            return

        # Determine whether we've to check object permissions (for detail actions)
        obj = None
        extra_actions = self.get_extra_actions()
        # We have to access the unbound function via __func__
        if handler.__func__ in extra_actions:
            if handler.detail:
                obj = self.get_object()
        elif self.action not in ("create", "list"):
            obj = self.get_object()

        # Finally, check permission
        perm = self.get_queryset().model.get_perm(perm_type)
        if not self.request.user.has_perm(perm, obj):
            raise PermissionDenied

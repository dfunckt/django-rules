from braces.views import PermissionRequiredMixin


class RuleRequiredMixin(PermissionRequiredMixin):
    """
    Custom PermissionRequiredMixin for django-braces that plays nicely with
    rules library.

    Class Settings
    `permission_required` - the permissions list of lists to check for.
        This can be a single permission list or a list of permission lists.
        The first item in each permission list is the rule name, and the
        remaining items are arguments to the rule.
    `login_url` - the login url of site
    `redirect_field_name` - defaults to "next"
    `raise_exception` - defaults to False - raise 403 if set to True

    Example Usage

        class SomeView(RulesRequiredMixin, ListView):
            ...
            # required
            permission_required = ["app.permission", object]

            # optional
            login_url = "/signup/"
            redirect_field_name = "hollaback"
            raise_exception = True
            ...
    """
    def check_permissions(self, request):
        """
        Returns whether or not the user has permissions
        """
        perms = self.get_permission_required(request)
        if type(perms) is list and len(perms) > 0:
            if type(perms[0]) is list:
                # working with list of lists, so parse each entry
                for p in perms:
                    if not request.user.has_perm(*p):
                        return False
                return True
            else:
                # perms is a list, so unpack it for variable parsing
                return request.user.has_perm(*perms)

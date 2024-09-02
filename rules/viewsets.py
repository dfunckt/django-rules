# All auto permission mixins (both for DRF and Django views)
# inherit from this mixin.
class BaseAutoPermissionMixin:
    def get_perm(self, model, perm_type):
        return "%s.%s_%s" % (model._meta.app_label, perm_type, model._meta.model_name)

    def get_permission_for_model(self, model, perm_type):

        # Attempt to use model mixin. If model mixin is not available,
        # default to standard convetion of this project (or allow
        # overriding `get_perm` through a custom Mixin)
        try:
            use_model_mixin_method = callable(model.get_perm)
        except AttributeError:
            use_model_mixin_method = False

        if use_model_mixin_method:
            perm = model.get_perm(perm_type)
        else:
            perm = self.get_perm(model, perm_type)
        return perm

# All auto permission mixins (both for DRF and Django views)
# inherit from this mixin.
class BaseAutoPermissionMixin:
    def get_permission_for_model(self, model, perm_type):
        return model.get_perm(perm_type)

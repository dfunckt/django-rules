from django.contrib import admin
from django.contrib.auth import get_permission_codename

from ..permissions import perm_exists


class ObjectPermissionsModelAdminMixin(object):
    def has_view_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("view", opts)
        perm = "%s.%s" % (opts.app_label, codename)
        if perm_exists(perm):
            return request.user.has_perm(perm, obj)
        else:
            return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("change", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename), obj)

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("delete", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename), obj)


class ObjectPermissionsInlineModelAdminMixin(ObjectPermissionsModelAdminMixin):
    def has_change_permission(self, request, obj=None):  # pragma: no cover
        opts = self.opts
        if opts.auto_created:
            for field in opts.fields:
                if field.rel and field.rel.to != self.parent_model:
                    opts = field.rel.to._meta
                    break
        codename = get_permission_codename("change", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename), obj)

    def has_delete_permission(self, request, obj=None):  # pragma: no cover
        if self.opts.auto_created:
            return self.has_change_permission(request, obj)
        return super(
            ObjectPermissionsInlineModelAdminMixin, self
        ).has_delete_permission(request, obj)


class ObjectPermissionsModelAdmin(ObjectPermissionsModelAdminMixin, admin.ModelAdmin):
    pass


class ObjectPermissionsStackedInline(
    ObjectPermissionsInlineModelAdminMixin, admin.StackedInline
):
    pass


class ObjectPermissionsTabularInline(
    ObjectPermissionsInlineModelAdminMixin, admin.TabularInline
):
    pass

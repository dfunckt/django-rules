from __future__ import absolute_import

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ModelViewSet

import rules  # noqa
from rules.contrib.rest_framework import AutoPermissionViewSetMixin


class AutoPermissionRequiredMixinTests(TestCase):
    def setUp(self):
        from testapp.models import TestModel

        class TestModelSerializer(ModelSerializer):
            class Meta:
                model = TestModel
                fields = "__all__"

        class TestViewSet(AutoPermissionViewSetMixin, ModelViewSet):
            queryset = TestModel.objects.all()
            serializer_class = TestModelSerializer
            permission_type_map = AutoPermissionViewSetMixin.permission_type_map.copy()
            permission_type_map["custom_detail"] = "add"
            permission_type_map["custom_nodetail"] = "add"

            @action(detail=True)
            def custom_detail(self, request):
                return Response()

            @action(detail=False)
            def custom_nodetail(self, request):
                return Response()

            @action(detail=False)
            def unknown(self, request):
                return Response()

        self.model = TestModel
        self.vs = TestViewSet
        self.req = APIRequestFactory().get("/")
        self.req.user = AnonymousUser()

    def test_predefined_action(self):
        # Create should be allowed due to the add permission set on TestModel
        self.assertEqual(self.vs.as_view({"get": "create"})(self.req).status_code, 201)
        # List should be allowed due to None in permission_type_map
        self.assertEqual(
            self.vs.as_view({"get": "list"})(self.req, pk=1).status_code, 200
        )
        # Retrieve should be allowed due to the view permission set on TestModel
        self.assertEqual(
            self.vs.as_view({"get": "retrieve"})(self.req, pk=1).status_code, 200
        )
        # Destroy should be forbidden due to missing delete permission
        self.assertEqual(
            self.vs.as_view({"get": "destroy"})(self.req, pk=1).status_code, 403
        )

    def test_custom_actions(self):
        # Both should not produce 403 due to being mapped to the add permission
        self.assertEqual(
            self.vs.as_view({"get": "custom_detail"})(self.req, pk=1).status_code, 404
        )
        self.assertEqual(
            self.vs.as_view({"get": "custom_nodetail"})(self.req).status_code, 200
        )

    def test_unknown_action(self):
        with self.assertRaises(ImproperlyConfigured):
            self.vs.as_view({"get": "unknown"})(self.req)

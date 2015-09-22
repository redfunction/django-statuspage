#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-statuspage
------------

Tests for `django-statuspage` views module.
"""

import json
from django.test import TestCase, RequestFactory, override_settings
from mock import patch, MagicMock, call
from djstatuspage import views


class TestDjstatuspage(TestCase):

    def _get_status(self, status_page_class):
        factory = RequestFactory()
        request = factory.get('/statuspage')

        statuspage_view = status_page_class.as_view()
        response = statuspage_view(request)
        value = response.getvalue()
        response_json = json.loads(value.decode("utf-8"))

        return response_json

    def test_database(self):
        response = self._get_status(views.DefaultStatusPage)

        self.assertEqual(response["database"], "ok")

    def test_database_error(self):
        p = MagicMock(side_effect=Exception("Weird error"))
        with patch("djstatuspage.models.Status.objects.get_or_create", p):
            response = self._get_status(views.DefaultStatusPage)
            p.assert_has_calls([call(pk=1)])

        self.assertEqual(response["database"], "error")

    @override_settings(STATUSPAGE_TASKS=dict(testkey=lambda: "testvalue",
                                             another="value"))
    def test_custom_field(self):
        response = self._get_status(views.DefaultStatusPage)

        self.assertEqual(response["database"], "ok")
        self.assertEqual(response["testkey"], "testvalue")
        self.assertFalse("another" in response)

    def test_base_statuspage(self):
        response = self._get_status(views.BaseStatusView)
        self.assertEqual(response, {})

    @override_settings(STATUSPAGE_TRY_DATABASE=False)
    def test_no_database(self):
        response = self._get_status(views.DefaultStatusPage)
        self.assertEqual(response, {})

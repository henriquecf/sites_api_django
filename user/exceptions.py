# -*- coding: utf-8 -*-
from rest_framework.exceptions import APIException
from rest_framework import status


class OwnerValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'There was an error validating the owner.'
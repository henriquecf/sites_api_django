# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class OwnerValidationError(APIException):
    """Returns a Bad Request.

    This exception must be used when there is an exception during a pre_save call in a viewset.
    The message can and should be replaced when the Exception is called.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'There was an error validating the owner.'
from datetime import datetime, timedelta
from django.db import models

from resource.models import Resource


class Account(Resource):
    """
    This model must save any data related to the account of a person,
    including payment data, signature date controls, contact fields
    needed for payment, etc
    """
    expiration_date = models.DateField(editable=False, default=datetime.today()+timedelta(30))

    def __str__(self):
        return self.owner.username
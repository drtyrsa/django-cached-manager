# -*- coding:utf-8 -*-
from django.db import models

from cached_manager import CachedManager


class Person(models.Model):
    name = models.CharField(max_length=8)
    is_cool = models.BooleanField(default=False)
    age = models.IntegerField(default=0)

    objects = models.Manager()
    mng = CachedManager()
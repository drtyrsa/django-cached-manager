# -*- coding:utf-8 -*-
from django.db import models
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist


class NotInt(Exception):
    '''
    The exception raised when manager is told to convert some string to int,
    but it's impossible.
    '''
    pass

class CachedManager(models.Manager):
    def _from_cache(self, cache_key, kwargs=None, only=None,
                       none_on_error=True, int_only=False, empty_value=-1,
                       one_item=False, const_kwargs=None):
        '''
        Tries to find an object in cache by ``key``. If it's possible
        (``cache.get(key) != empty_value``) the object is returned.
        Else the object is queried, saved in cache and returned.

        Arguments:

        * ``cache_key`` - cache key of the object. If ``kwargs`` argument
        exists, ``cache_key`` should be valid format string to ``kwargs`` dict.
        * ``kwargs`` - dict, holding kwargs to ``filter()`` (or ``.get()``)
        method. ``cache_key`` should be valid format string for this dict. That
        means there will be unique cache key for every distinct ``kwargs``.
        * ``only`` - if is not ``None``, a list of args to ``.only()`` queryset
        method.
        * ``none_on_error`` - if ``True``, ``None`` will be returned on
        ``ObjectDoesNotExist`` and int conversion error. Else exceptions
        will be raised.
        * ``empty_value`` - if ``cache.get(key) != empty_value``, an object
        is in cache.
        * ``one_item`` - if ``True`` the method will try to make ``.get()`` call
        and return one object. Else it will make ``.filter()`` call and return
        list.
        * ``const_kwargs`` - same as ``kwargs``, but doesn't affect cache
        key.
        '''
        if kwargs is None:
            kwargs = {}
        try:
            if int_only and kwargs:
                new_kwargs = {}
                for k, v in kwargs.iteritems():
                    try:
                        new_kwargs[k] = int(v)
                    except (ValueError, TypeError):
                        raise NotInt
                kwargs = new_kwargs
            key = cache_key % kwargs
            if const_kwargs is None:
                const_kwargs = {}
            kwargs.update(const_kwargs)
            cached = cache.get(key, empty_value)
            if cached != empty_value:
                return cached
            qset = super(CachedManager, self).get_query_set()
            if only:
                qset = qset.only(*only)
            if one_item:
                result = qset.get(**kwargs)
            else:
                result = list(qset.filter(**kwargs))
        except NotInt:
            if none_on_error:
                return None
            else:
                raise NotInt
        except ObjectDoesNotExist:
            if none_on_error:
                result = None
            else:
                raise ObjectDoesNotExist
        cache.set(key, result)
        return result

    def _objects_by_pks(self, get_item_func, pks, cache_key, dict_key='pk', empty_value=-1):
        '''
        Returns a list of objects by a list of pk's (or any other fields).

        *``get_item_func`` - a function that returns an object by gived pk. It
        should be something like ``lambda pk: self._from_cache(`cache_key``, {dict_key: pk}, one_item=True, empty_value=empty_value)``
        *``pks`` - a list (or any other iterable) of pks.

        First the method tries to load the objects directly form cache and if
        some objects aren't found, calls ``get_item_func`` for them.
        '''
        cached = cache.get_many([cache_key % {dict_key: x} for x in pks])
        results = []
        for pk in pks:
            result = cached.get(cache_key % {dict_key: pk}, empty_value)
            if result == empty_value:
                result = get_item_func(pk)
            results.append(result)
        return results

=========================
Cached manager
=========================

Django models manager that encapsulates some common caching operations: try to get a model instance (or list of them) from cache, if can't - evaluate it and save to cache.
 
It can be ready in production right now, but I can't call it fully-featured reusable app. The development is still in progress.

``CachedManager`` extends ``models.Manager`` with two methods.

_from_cache
============
Method for retrieving a model instance (or list of them) from cache, evaluating and saving if necessary::
    
    _from_cache(self, cache_key, kwargs=None, only=None,
                none_on_error=True, int_only=False, empty_value=-1,
                one_item=False, const_kwargs=None)

Tries to find an object in cache by ``key``. If it's possible
(``cache.get(key) != empty_value``) the object is returned.
Else the object is queried, saved in cache and returned.

Arguments:

* ``cache_key`` - cache key of the object. If ``kwargs`` argument exists, ``cache_key`` should be valid format string to ``kwargs`` dict.
* ``kwargs`` - dict, holding kwargs to ``filter()`` (or ``.get()``) method. ``cache_key`` should be valid format string for this dict. That means there will be unique cache key for every distinct ``kwargs``.
* ``only`` - if is not ``None``, a list of args to ``.only()`` queryset method.
* ``none_on_error`` - if ``True``, ``None`` will be returned on ``ObjectDoesNotExist`` and int conversion error. Else exceptions will be raised.
* ``empty_value`` - if ``cache.get(key) != empty_value``, an object is in cache.
* ``one_item`` - if ``True`` the method will try to make ``.get()`` call and return one object. Else it will make ``.filter()`` call and return list.
* ``const_kwargs`` - same as ``kwargs``, but doesn't affect cache key.

_objects_by_pks
================

Returns a list of objects by a list of pk's (or any other fields). Why do we need this? For example we have a model ``Article`` that can be ``featured`` or not. So we need to cache a list of all articles and a list of featured articles. But there will be a lot of duplicating data. So there a another way: to cache only ``pk``'s and get "full" instances using this method.::

    _objects_by_pks(self, get_item_func, pks, cache_key,
                    dict_key='pk', empty_value=-1)
 
* ``get_item_func`` - a function that returns an object by gived pk. It should be something like ``lambda pk: self._from_cache(cache_key, {dict_key: pk}, one_item=True, empty_value=empty_value)``
* ``pks`` - a list (or any other iterable) of pks.

First the method tries to load the objects directly form cache and if
some objects aren't found, calls ``get_item_func`` for them.
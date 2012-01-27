# -*- coding:utf-8 -*-
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from cached_manager.tests.utils import SettingsTestCase
from cached_manager.tests.models import Person
from cached_manager.managers import NotInt

def clear_locmem_cache():
    cache._cache.clear()
    cache._expire_info.clear()

class TestManager(SettingsTestCase):
    def setUp(self):
        self.settings_manager.set(INSTALLED_APPS=('cached_manager.tests',))

        self.some_person1 = Person.objects.create(name='Bart',
                                                 is_cool=True,
                                                 age=10)
        self.some_person2 = Person.objects.create(name='Flanders',
                                                 is_cool=False,
                                                 age=60)
        self.some_person3 = Person.objects.create(name='Burns',
                                                 is_cool=True,
                                                 age=123)

    def test_get_one_item(self):
        clear_locmem_cache()

        from_db = Person.objects.get(name='Bart')
        from_manager = Person.mng._from_cache('person::%(name)s',
                                              {'name': 'Bart'},
                                              one_item=True)
        self.assertEqual(from_db, from_manager)

        from_cache = cache.get('person::%(name)s' % {'name': 'Bart'})
        self.assertEqual(from_db, from_cache)

    def test_get_many(self):
        clear_locmem_cache()

        from_db = Person.objects.all()
        from_manager = Person.mng._from_cache('people')
        self.assertEqual(set(from_db), set(from_manager))

        from_cache = cache.get('people')
        self.assertEqual(set(from_db), set(from_cache))

    def test_only(self):
        clear_locmem_cache()

        from_manager = Person.mng._from_cache('people', only=('id',))
        self.assertTrue(from_manager[0]._deferred)

    def test_int_only(self):
        clear_locmem_cache()

        from_db = Person.objects.filter(age__gt=20)
        from_manager = Person.mng._from_cache('people_by_age__gt::%(age__gt)d',
                                              {'age__gt': 20},
                                              int_only=True)
        self.assertEqual(set(from_db), set(from_manager))

        from_manager = Person.mng._from_cache('people_by_age__gt::%(age__gt)d',
                                              {'age__gt': '20'},
                                              int_only=True)
        self.assertEqual(set(from_db), set(from_manager))

    def test_int_only_returns_none_if_none_on_error(self):
        clear_locmem_cache()

        from_manager = Person.mng._from_cache('people_by_age__gt::%(age__gt)d',
                                              {'age__gt': ':-('},
                                              int_only=True,
                                              none_on_error=True)
        self.assertTrue(from_manager is None)

    def test_int_only_raises_exception_if_not_none_on_error(self):
        clear_locmem_cache()

        self.assertRaises(NotInt,
                          Person.mng._from_cache,
                         *('people_by_age__gt::%(age__gt)d', {'age__gt': ':-('}),
                        **dict(int_only=True, none_on_error=False))

    def test_does_not_exists_returns_none_if_none_on_error(self):
        clear_locmem_cache()

        from_manager = Person.mng._from_cache('person::%(name)s',
                                              {'name': u'Bender'},
                                              one_item=True,
                                              none_on_error=True)
        self.assertTrue(from_manager is None)

    def test_does_not_exists_raises_exception_if_not_none_on_error(self):
        clear_locmem_cache()

        self.assertRaises(ObjectDoesNotExist,
                          Person.mng._from_cache,
                         *('person::%(name)s', {'name': u'Bender'}),
                        **dict(one_item=True, none_on_error=False))

    def test_empty_value(self):
        clear_locmem_cache()

        cache.set('people', 5)

        from_db = Person.objects.all()
        from_manager = Person.mng._from_cache('people')
        self.assertEqual(from_manager, 5)

        from_manager = Person.mng._from_cache('people', empty_value=5)
        self.assertEqual(set(from_db), set(from_manager))

    def test_const_kwargs(self):
        clear_locmem_cache()

        from_db = Person.objects.filter(is_cool=True)
        from_manager = Person.mng._from_cache('cool_people',
                                              const_kwargs={'is_cool': True})
        self.assertEqual(set(from_db), set(from_manager))

    def test_objects_by_pks(self):
        clear_locmem_cache()

        get_item_func = lambda pk: Person.mng._from_cache('person::%(pk)d',
                                                          {'pk': pk},
                                                          one_item=True,)
        pks = Person.objects.values_list('id', flat=True)
        from_manager = Person.mng._objects_by_pks(get_item_func,
                                   pks,
                                   'person::%(pk)d',)
        from_db = Person.objects.all()
        self.assertEqual(set(from_db), set(from_manager))
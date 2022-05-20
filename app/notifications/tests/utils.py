from warnings import catch_warnings, simplefilter

from django.core.exceptions import ImproperlyConfigured
from django.db import models, connection


class AbstractModelMixin:

    abstract_model = None

    @classmethod
    def setUpClass(cls):
        if cls.abstract_model is None:
            raise ImproperlyConfigured(
                "Using AbstractModelMixin without "
                "the 'model' attribute is prohibited"
            )
        
        if (not issubclass(cls.abstract_model, models.Model)
                or not cls.abstract_model._meta.abstract):
            raise ImproperlyConfigured(
                "The 'model' attribute must define Django abstract model class"
            )

        with catch_warnings():
            simplefilter('ignore')
            cls.model = models.base.ModelBase(
                '__TestModel__' + cls.abstract_model.__name__, 
                (cls.abstract_model,),
                {'__module__': cls.abstract_model.__module__}
            )
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(cls.model)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(cls.model)
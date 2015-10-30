import pytest

from django.core.urlresolvers import reverse

from ban.core import context
from ban.core.tests.factories import UserFactory

from ban.core.database import test_db, db
from ban.core import models as cmodels
from ban.versioning import models as vmodels
models = [vmodels.Version, cmodels.Contact, cmodels.Municipality,
          cmodels.Street, cmodels.Locality, cmodels.HouseNumber,
          cmodels.Position]


def pytest_configure(config):
    test_db.connect()
    for model in models:
        model._meta.database = test_db
    for model in models:
        model.create_table(fail_silently=True)
    verbose = config.getoption('verbose')
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)


def pytest_unconfigure(config):
    db.drop_tables(models)
    test_db.close()


def pytest_runtest_setup(item):
    for model in models[::-1]:
        model.delete().execute()
        assert not len(model.select())


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture()
def staffuser():
    return UserFactory(is_staff=True)


@pytest.fixture()
def loggedclient(client, user):
    context.set_user(user)
    client.login(username=user.username, password='password')
    return client


@pytest.fixture()
def url():
    def _(name, **kwargs):
        return reverse(name, kwargs=kwargs)
    return _

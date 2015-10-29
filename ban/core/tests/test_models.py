import pytest

from ban.core import models

from .factories import (HouseNumberFactory, MunicipalityFactory,
                        PositionFactory, StreetFactory)

pytestmark = pytest.mark.django_db


def test_municipality_is_created_with_version_1():
    municipality = MunicipalityFactory()
    assert municipality.version == 1


def test_municipality_is_versioned():
    initial_name = "Moret-sur-Loing"
    municipality = MunicipalityFactory(name=initial_name)
    assert len(municipality.versions) == 1
    assert municipality.version == 1
    municipality.name = "Orvanne"
    municipality.increment_version()
    municipality.save()
    assert municipality.version == 2
    assert len(municipality.versions) == 2
    version1 = municipality.versions[0].load()
    version2 = municipality.versions[1].load()
    assert version1.name == "Moret-sur-Loing"
    assert version2.name == "Orvanne"


def test_street_is_versioned():
    initial_name = "Rue des Pommes"
    street = StreetFactory(name=initial_name)
    assert street.version == 1
    street.name = "Rue des Poires"
    street.increment_version()
    street.save()
    assert street.version == 2
    assert len(street.versions) == 2
    version1 = street.versions[0].load()
    version2 = street.versions[1].load()
    assert version1.name == "Rue des Pommes"
    assert version2.name == "Rue des Poires"


def test_tmp_fantoir_should_use_name():
    municipality = MunicipalityFactory(insee='93031')
    street = StreetFactory(municipality=municipality, fantoir='',
                           name="Rue des Pêchers")
    assert street.tmp_fantoir == '#RUEDESPECHERS'


def test_compute_cia_should_consider_insee_fantoir_number_and_ordinal():
    municipality = MunicipalityFactory(insee='93031')
    street = StreetFactory(municipality=municipality, fantoir='1491H')
    hn = HouseNumberFactory(street=street, number="84", ordinal="bis")
    assert hn.compute_cia() == '93031_1491H__84_BIS'


def test_compute_cia_should_let_ordinal_empty_if_not_set():
    municipality = MunicipalityFactory(insee='93031')
    street = StreetFactory(municipality=municipality, fantoir='1491H')
    hn = HouseNumberFactory(street=street, number="84", ordinal="")
    assert hn.compute_cia() == '93031_1491H__84_'


def test_compute_cia_should_use_locality_if_no_street():
    municipality = MunicipalityFactory(insee='93031')
    street = StreetFactory(municipality=municipality, fantoir='1491H')
    hn = HouseNumberFactory(street=street, number="84", ordinal="")
    assert hn.compute_cia() == '93031_1491H__84_'


def test_housenumber_should_create_cia_on_save():
    municipality = MunicipalityFactory(insee='93031')
    street = StreetFactory(municipality=municipality, fantoir='1491H')
    hn = HouseNumberFactory(street=street, number="84", ordinal="bis")
    assert hn.cia == '93031_1491H__84_BIS'


def test_housenumber_is_versioned():
    street = StreetFactory()
    hn = HouseNumberFactory(street=street, ordinal="b")
    assert hn.version == 1
    hn.ordinal = "bis"
    hn.increment_version()
    hn.save()
    assert hn.version == 2
    assert len(hn.versions) == 2
    version1 = hn.versions[0].load()
    version2 = hn.versions[1].load()
    assert version1.ordinal == "b"
    assert version2.ordinal == "bis"
    assert version2.street == street


def test_cannot_duplicate_housenumber_on_same_street():
    street = StreetFactory()
    HouseNumberFactory(street=street, ordinal="b", number="10")
    with pytest.raises(ValueError):
        HouseNumberFactory(street=street, ordinal="b", number="10")


def test_can_create_two_housenumbers_with_same_number_but_different_street():
    street = StreetFactory()
    street2 = StreetFactory()
    HouseNumberFactory(street=street, ordinal="b", number="10")
    HouseNumberFactory(street=street2, ordinal="b", number="10")


def test_housenumber_center():
    housenumber = HouseNumberFactory()
    position = PositionFactory(housenumber=housenumber)
    assert housenumber.center == position.center_json


def test_housenumber_center_without_position():
    housenumber = HouseNumberFactory()
    assert housenumber.center is None


def test_position_is_versioned():
    housenumber = HouseNumberFactory()
    position = PositionFactory(housenumber=housenumber, center=(1, 2))
    assert position.version == 1
    position.center = (3, 4)
    position.increment_version()
    position.save()
    assert position.version == 2
    assert len(position.versions) == 2
    version1 = position.versions[0].load()
    version2 = position.versions[1].load()
    assert version1.center == (1, 2)
    assert version2.center == (3, 4)
    assert version2.housenumber == housenumber


@pytest.mark.xfail
def test_position_attributes():
    position = PositionFactory(attributes={'foo': 'bar'})
    assert position.attributes['foo'] == 'bar'
    assert models.Position.objects.filter(attributes__foo='bar').exists()

import pytest
from django.core.management import call_command

from apps.tenants.models import Zoo


@pytest.fixture
def cedar_hollow(db):
    """The fictional test zoo, loaded from the shipped fixture. Every content test starts here."""
    call_command("loaddata", "fixtures/cedar_hollow_seed.json", verbosity=0)
    return Zoo.objects.get(slug="cedar-hollow")

from collections.abc import Iterator

import pytest
from django.core.cache import cache


@pytest.fixture
def redis_cache() -> Iterator[None]:
    # Redis tests opt in and use a clean keyspace.
    cache.clear()
    yield
    cache.clear()

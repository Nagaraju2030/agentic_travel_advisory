from datetime import date

import pytest
from pydantic import ValidationError

from app.models.schemas import TripRequest


def test_trip_days_inclusive():
    req = TripRequest(
        origin="Hyderabad, India",
        destination="Tokyo, Japan",
        start_date=date(2026, 9, 15),
        end_date=date(2026, 9, 20),
    )
    assert req.trip_days == 6


def test_rejects_invalid_date_range():
    with pytest.raises(ValidationError):
        TripRequest(
            origin="A",
            destination="B",
            start_date=date(2026, 9, 20),
            end_date=date(2026, 9, 15),
        )

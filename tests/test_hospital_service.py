"""
Unit tests for HospitalService.
Covers Test 5 (Hospital verification distinction), distance calculation,
and specialty filtering.
"""

import pytest
from services.hospital_service import HospitalService


@pytest.fixture
def service():
    return HospitalService()


def test_real_dataset_loads_ten_hospitals(service):
    hospitals = service.load_hospitals()
    assert len(hospitals) >= 10
    names = [h["hospital_name"] for h in hospitals]
    assert any("Kidwai" in n for n in names)
    assert any("Jayadeva" in n for n in names)
    assert any("Victoria" in n for n in names)


def test_hospital_verification_distinction(service):
    """
    TEST 5: Verified hospital location, but participation in a specific scheme is distinguished.
    """
    # KMIO specializes in Oncology, empaneled for PMJAY, ArK, RAN, but NOT Nikshay or Yeshasvini
    hospitals = service.search_hospitals(city="Bengaluru", condition="cancer")
    kmio = next((h for h in hospitals if "Kidwai" in h["hospital_name"]), None)

    assert kmio is not None
    assert kmio["location_verification_status"] == "VERIFIED"
    assert kmio["treatment_verification_status"] == "VERIFIED"

    # Participates in PMJAY and ArK
    assert "SCHEME-AB-PMJAY" in kmio["participating_schemes"]
    assert "SCHEME-AB-ARK" in kmio["participating_schemes"]

    # Does NOT participate in Yeshasvini
    assert "SCHEME-YESHASVINI" not in kmio["participating_schemes"]


def test_distance_calculation(service):
    """
    Haversine distance calculation between Vidhana Soudha (12.9797, 77.5912) and Victoria Hospital (12.9634, 77.5753).
    Approx distance is ~2.5 - 3.0 km.
    """
    dist = service.calculate_distance_km(12.9797, 77.5912, 12.9634, 77.5753)
    assert 2.0 <= dist <= 3.5


def test_specialty_filtering(service):
    cardiac_hospitals = service.search_hospitals(city="Bengaluru", condition="cardiac")
    names = [h["hospital_name"] for h in cardiac_hospitals]
    assert any("Jayadeva" in n for n in names)
    assert any("Narayana" in n for n in names)


def test_missing_data_resilience():
    service = HospitalService(data_path="data/non_existent.json")
    results = service.search_hospitals(city="Bengaluru")
    assert results == []

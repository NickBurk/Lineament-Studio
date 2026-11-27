from dataclasses import replace
from threading import Thread
from uuid import UUID, uuid4

import pytest

from lineament_core.application import (
    AlgorithmDescriptor,
    AlgorithmRegistry,
    CancellationToken,
    Parameter,
    ParameterType,
)
from lineament_core.diagnostics import ContractError, ErrorCode
from lineament_core.domain import (
    AlgorithmRef,
    ArtifactRef,
    CrsStatus,
    GeometricRank,
    GeologicalOrder,
    JobResult,
    ProjectRef,
    SourceAssetRef,
    SpatialReference,
)


def test_storage_neutral_references_and_crs():
    identity = uuid4()
    assert ProjectRef(identity).id == SourceAssetRef(identity).id
    with pytest.raises(ValueError):
        ProjectRef(UUID(int=0))
    assert SpatialReference(CrsStatus.ABSENT) != SpatialReference(CrsStatus.UNKNOWN)
    assert (
        SpatialReference(CrsStatus.KNOWN, "EPSG:4326", "degree").horizontal_unit
        == "degree"
    )
    with pytest.raises(ValueError):
        SpatialReference(CrsStatus.KNOWN, "EPSG:4326")
    with pytest.raises(ValueError):
        SpatialReference(CrsStatus.ABSENT, "EPSG:4326")
    assert GeometricRank.G1 != GeologicalOrder("G1")


def test_result_rejects_duplicate_ids_and_unknown_version(job):
    artifact = ArtifactRef(uuid4(), "summary")
    with pytest.raises(ValueError, match="Duplicate"):
        JobResult(job.id, job.algorithm, (artifact, artifact))
    with pytest.raises(ValueError, match="Unsupported"):
        JobResult(job.id, job.algorithm, version="2.0")


@pytest.fixture
def declaration(job):
    return AlgorithmDescriptor(
        job.algorithm,
        frozenset({"source"}),
        frozenset({"summary"}),
        {
            "title": Parameter(ParameterType.STRING),
            "tiles": Parameter(ParameterType.INTEGER, 1),
        },
        supports_progress=True,
        supports_cancellation=True,
    )


def test_registry_normalizes_defaults_and_checks_ownership(job, declaration):
    registry = AlgorithmRegistry()
    registry.register(declaration)
    assert registry.validate(job) == {"title": "Рельеф", "tiles": 1}
    assert registry.resolve(job.algorithm) is declaration
    with pytest.raises(ContractError) as caught:
        registry.register(declaration)
    assert caught.value.code == ErrorCode.DUPLICATE_OPERATION
    twin = replace(declaration, algorithm=AlgorithmRef(job.algorithm.id, "2.0.0"))
    registry.register(twin)
    assert registry.resolve(twin.algorithm) is twin


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("algorithm", AlgorithmRef("unknown", "1.0.0"), ErrorCode.UNKNOWN_OPERATION),
        (
            "algorithm",
            AlgorithmRef("example.summary", "2.0.0"),
            ErrorCode.UNSUPPORTED_ALGORITHM_VERSION,
        ),
        ("resource_profile", "unregistered", ErrorCode.INVALID_PARAMETERS),
        ("parameters", {}, ErrorCode.INVALID_PARAMETERS),
        ("parameters", {"title": "ok", "tiles": True}, ErrorCode.INVALID_PARAMETERS),
        ("parameters", {"title": "ok", "other": 0}, ErrorCode.INVALID_PARAMETERS),
        ("inputs", {}, ErrorCode.INVALID_INPUTS),
    ],
)
def test_registry_rejects_invalid_job(job, declaration, field, value, code):
    registry = AlgorithmRegistry()
    registry.register(declaration)
    with pytest.raises(ContractError) as caught:
        registry.validate(replace(job, **{field: value}))
    assert caught.value.code == code


def test_registry_checks_result_kind_and_identity(job, declaration):
    registry = AlgorithmRegistry()
    registry.register(declaration)
    result = JobResult(job.id, job.algorithm, (ArtifactRef(uuid4(), "summary"),))
    registry.validate_result(job, result)
    for invalid in (
        replace(result, job_id=uuid4()),
        replace(result, artifacts=(ArtifactRef(uuid4(), "wrong"),)),
    ):
        with pytest.raises(ContractError) as caught:
            registry.validate_result(job, invalid)
        assert caught.value.code == ErrorCode.INVALID_RESULT


def test_cooperative_signal_is_idempotent_across_threads():
    token = CancellationToken()
    assert not token.requested
    producer = Thread(target=token.request)
    producer.start()
    producer.join(timeout=2)
    assert token.requested
    token.request()
    assert token.requested


@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), {"nested": [float("inf")]}]
)
def test_parameter_rejects_non_finite_json_values(value):
    parameter_type = (
        ParameterType.OBJECT if isinstance(value, dict) else ParameterType.NUMBER
    )
    assert not parameter_type.accepts(value)

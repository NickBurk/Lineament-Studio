from dataclasses import FrozenInstanceError, replace
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


def test_job_nested_parameters_are_independent_and_immutable(job):
    from types import MappingProxyType

    original = {"thresholds": {"canny": [20, 40]}, "layers": [{"label": "Рельеф"}]}
    snapshot = replace(job, parameters=original)
    original["thresholds"]["canny"].append(80)
    original["layers"][0]["label"] = "changed"
    assert snapshot.parameters["thresholds"]["canny"] == (20, 40)
    assert snapshot.parameters["layers"][0]["label"] == "Рельеф"
    assert isinstance(snapshot.parameters["thresholds"], MappingProxyType)
    with pytest.raises(TypeError):
        snapshot.parameters["thresholds"]["canny"] = (1,)
    with pytest.raises(AttributeError):
        snapshot.parameters["thresholds"]["canny"].append(80)
    assert (
        replace(job, parameters=snapshot.parameters).parameters == snapshot.parameters
    )


@pytest.mark.parametrize(
    "invalid",
    [
        {"bad": object()},
        {"bad": float("nan")},
        {"bad": float("inf")},
        {1: "bad"},
        {"bad": {"nested": float("-inf")}},
    ],
)
def test_job_rejects_invalid_nested_json(job, invalid):
    with pytest.raises(ValueError):
        replace(job, parameters=invalid)


def test_job_rejects_cycles_and_excessive_nesting(job):
    cycle = []
    cycle.append(cycle)
    nested = []
    for _ in range(65):
        nested = [nested]
    for value in (cycle, nested):
        with pytest.raises(ValueError):
            replace(job, parameters={"value": value})


def test_registry_returns_stable_immutable_nested_parameters(job):
    original = {"options": {"cuts": [1, 2]}}
    declaration = {"options": Parameter(ParameterType.OBJECT)}
    descriptor = AlgorithmDescriptor(
        job.algorithm, {"source"}, {"summary"}, declaration
    )
    registry = AlgorithmRegistry()
    registry.register(descriptor)
    snapshot = replace(job, parameters=original)
    first = registry.validate(snapshot)
    original["options"]["cuts"].append(3)
    declaration["options"] = Parameter(ParameterType.STRING)
    with pytest.raises(TypeError):
        first["options"]["cuts"] = (3,)
    with pytest.raises(AttributeError):
        first["options"]["cuts"].append(3)
    assert first == registry.validate(snapshot)
    assert first["options"]["cuts"] == (1, 2)
    assert descriptor.parameters["options"].kind is ParameterType.OBJECT
    assert registry.resolve(job.algorithm) is descriptor
    with pytest.raises(TypeError):
        descriptor.parameters["options"] = Parameter(ParameterType.STRING)


def test_registry_accepts_immutable_json_arrays(job):
    registry = AlgorithmRegistry()
    registry.register(
        AlgorithmDescriptor(
            job.algorithm,
            {"source"},
            {"summary"},
            {"values": Parameter(ParameterType.ARRAY)},
        )
    )
    data = [1, {"nested": [2]}]
    snapshot = replace(job, parameters={"values": data})
    assert registry.validate(snapshot)["values"] == (1, {"nested": (2,)})
    data[1]["nested"].append(3)
    assert registry.validate(snapshot)["values"][1]["nested"] == (2,)


def test_result_normalizes_list_without_retaining_it(job):
    first = ArtifactRef(uuid4(), "summary")
    original = [first]
    result = JobResult(job.id, job.algorithm, original)
    original.append(ArtifactRef(uuid4(), "summary"))
    assert result.artifacts == (first,)
    assert JobResult(job.id, job.algorithm, (first,)).artifacts == (first,)
    with pytest.raises(FrozenInstanceError):
        result.artifacts += (first,)


@pytest.mark.parametrize(
    "artifacts", ["text", b"bytes", {"id": 1}, iter(()), [object()], (None,)]
)
def test_result_rejects_invalid_artifact_collection(job, artifacts):
    with pytest.raises(ValueError, match="artifact|Artifact"):
        JobResult(job.id, job.algorithm, artifacts)


def test_job_does_not_accept_mutable_custom_scalars(job):
    class MutableString(str):
        pass

    value = MutableString("first")
    snapshot = replace(job, parameters={"name": value})
    assert type(snapshot.parameters["name"]) is str

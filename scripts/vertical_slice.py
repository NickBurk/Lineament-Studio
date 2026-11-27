"""Generate a synthetic DEM and exercise project persistence in two processes."""

import argparse
import json
import subprocess
import sys
import shutil
from pathlib import Path
from uuid import uuid4

from lineament_core.infrastructure.data.manifest import checksum
from lineament_core.infrastructure.data.project import Project
from lineament_core.infrastructure.gis.raster import inspect_dem
from lineament_core.science.hillshade import Illumination


def smoke(folder):
    import numpy as np
    import rasterio
    from rasterio.transform import Affine

    folder.mkdir(exist_ok=True)
    source = folder / "Исходный DEM.tif"
    if source.exists():
        raise FileExistsError(source)
    with rasterio.open(
        source,
        "w",
        driver="GTiff",
        width=17,
        height=13,
        count=1,
        crs="EPSG:32633",
        transform=Affine(2, 0, 500000, 0, -2, 5500000),
        dtype="int16",
    ) as dst:
        rows, cols = np.indices((13, 17))
        dst.write((rows + cols * 2).astype("int16"), 1)
        dst.set_band_unit(1, "m")
        dst.scales = (0.5,)
        dst.offsets = (100.0,)
    original = checksum(source)
    with rasterio.Env(PROJ_NETWORK="OFF"):
        project = Project.create(folder / "Проект", project_crs="EPSG:32633")
        reference = project.add_dem(source, "reference", inspect_dem)
        project.add_dem(source, "copy", inspect_dem)
        preflight = inspect_dem(source)
        light = Illumination(315, 1, 1)
        assert preflight["raw_minimum"] == 0 and preflight["minimum"] == 100
        result = project.register_result(
            source_id=reference, job_id=str(uuid4()), light=light, tile=5
        )
        project.save(default_profiles={"hillshade": {"band": 1}})
        project.close()
    reopened = subprocess.check_output(
        [sys.executable, __file__, str(folder), "--reopen"]
    )
    state = json.loads(reopened)
    assert {a["storage_mode"] for a in state["assets"]} == {"copy", "reference"}
    assert state["default_profiles"] == {"hillshade": {"band": 1}}
    assert len(state["results"]) == 1 and state["results"][0]["id"] == result
    historical = state["results"][0]["provenance"]
    assert historical["source_version_id"] == next(
        asset["source_version_id"]
        for asset in state["assets"]
        if asset["asset_id"] == reference
    )
    alternate = folder / "Relink DEM.tif"
    shutil.copyfile(source, alternate)
    with rasterio.open(alternate, "r+") as ds:
        ds.offsets = (150.0,)
    project = Project.open(folder / "Проект")
    project.relink(reference, alternate, accept_changed=True)
    relinked = project.snapshot()
    assert historical == relinked["results"][0]["provenance"]
    assert historical["source_version_id"] != next(
        asset["source_version_id"]
        for asset in relinked["assets"]
        if asset["asset_id"] == reference
    )
    project.close()
    assert checksum(source) == original
    print(
        json.dumps(
            dict(
                project_id=state["project_id"],
                results=state["results"],
                preflight=preflight,
                fresh_process_reopen=True,
                historical_provenance_preserved=True,
                original_sha256=original,
            ),
            ensure_ascii=True,
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--reopen", action="store_true")
    args = parser.parse_args()
    if args.reopen:
        with_project = Project.open(args.folder / "Проект")
        print(json.dumps(with_project.snapshot(), ensure_ascii=True))
        with_project.close()
    else:
        smoke(args.folder)


if __name__ == "__main__":
    main()

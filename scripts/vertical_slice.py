"""Generate a synthetic DEM and exercise project persistence in two processes."""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from lineament_core.infrastructure.data.manifest import checksum
from lineament_core.infrastructure.data.project import Project
from lineament_core.infrastructure.gis.raster import inspect_dem
from lineament_core.science.hillshade import VERSION, Illumination, run


def smoke(folder):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

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
        transform=from_origin(500000, 5500000, 2, 2),
        dtype="float32",
    ) as dst:
        rows, cols = np.indices((13, 17))
        dst.write((rows + cols * 2).astype("float32"), 1)
        dst.set_band_unit(1, "m")
    original = checksum(source)
    with rasterio.Env(PROJ_NETWORK="OFF"):
        project = Project.create(folder / "Проект", project_crs="EPSG:32633")
        reference = project.add_dem(source, "reference", inspect_dem)
        project.add_dem(source, "copy", inspect_dem)
        preflight = inspect_dem(source)
        light = Illumination(315, 1, 1)
        output = folder / "hillshade.tif"
        run(source, output, light, tile=5)
        result = project.register_result(
            output,
            source_id=reference,
            job_id=str(uuid4()),
            provenance=dict(
                algorithm="hillshade",
                algorithm_version=VERSION,
                source_checksum=original,
                band=1,
                parameters=asdict(light),
                dependencies=dict(
                    rasterio=rasterio.__version__,
                    gdal=rasterio.__gdal_version__,
                    proj=rasterio.__proj_version__,
                    numpy=np.__version__,
                ),
                output=inspect_dem(output),
            ),
            inspect=inspect_dem,
        )
        project.close()
    reopened = subprocess.check_output(
        [sys.executable, __file__, str(folder), "--reopen"]
    )
    state = json.loads(reopened)
    assert {a["storage_mode"] for a in state["assets"]} == {"copy", "reference"}
    assert len(state["results"]) == 1 and state["results"][0]["id"] == result
    assert checksum(source) == original
    print(
        json.dumps(
            dict(
                project_id=state["project_id"],
                results=state["results"],
                preflight=preflight,
                fresh_process_reopen=True,
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

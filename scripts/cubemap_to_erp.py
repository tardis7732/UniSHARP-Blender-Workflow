"""Convert six UniSHARP-order cubemap faces to a 2:1 equirectangular panorama."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from unisharp.utils.pano import Cube2Equirec


FACE_ORDER = ("up", "back", "left", "front", "right", "down")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("up", type=Path)
    parser.add_argument("back", type=Path)
    parser.add_argument("left", type=Path)
    parser.add_argument("front", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("down", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    paths = [getattr(args, name) for name in FACE_ORDER]
    images = [Image.open(path).convert("RGB") for path in paths]
    side = min(min(image.size) for image in images)
    if side < 16:
        raise ValueError("Cubemap faces must be at least 16 pixels wide.")
    faces = [np.asarray(image.resize((side, side), Image.Resampling.LANCZOS), dtype=np.float32) / 255.0 for image in images]
    cube = torch.from_numpy(np.stack(faces)).permute(3, 0, 1, 2).unsqueeze(0)
    erp = Cube2Equirec(face_w=side, equ_h=side * 2, equ_w=side * 4)(cube)[0].permute(1, 2, 0).clamp(0.0, 1.0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((erp.numpy() * 255.0 + 0.5).astype(np.uint8)).save(args.output)
    print(f"Saved 360 ERP panorama: {args.output}")


if __name__ == "__main__":
    main()

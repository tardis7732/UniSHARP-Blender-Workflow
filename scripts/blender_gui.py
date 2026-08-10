"""Local GUI for converting normal images to UniSHARP Blender scenes."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
UNISHARP_PYTHON = REPO_ROOT.parent / "miniforge3" / "envs" / "unisharp" / "python.exe"
if UNISHARP_PYTHON.is_file() and Path(sys.executable).resolve() != UNISHARP_PYTHON.resolve():
    os.execv(str(UNISHARP_PYTHON), [str(UNISHARP_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

import gradio as gr


SCRIPTS = REPO_ROOT / "scripts"
DEFAULT_CHECKPOINT = REPO_ROOT / "checkpoints" / "pretained_model.pt"
APP_ROOT = Path(os.environ.get("UNISHARP_APP_ROOT", REPO_ROOT)).resolve()
DEFAULT_OUTPUT = APP_ROOT / "Blender_Output"
DEFAULT_BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
VIEWER_SCRIPT = SCRIPTS / "viser_ply_viewer.py"
_VIEWER_PROCESS: subprocess.Popen[str] | None = None


def _blender_executable() -> Path:
    configured = os.environ.get("BLENDER_EXE")
    candidates = [Path(configured)] if configured else []
    candidates.append(DEFAULT_BLENDER)
    for program_files in (os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432")):
        if program_files:
            blender_root = Path(program_files) / "Blender Foundation"
            candidates.extend(sorted(blender_root.glob("Blender */blender.exe"), reverse=True))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    discovered = shutil.which("blender")
    if discovered:
        return Path(discovered)
    raise RuntimeError("Blender executable was not found. Set BLENDER_EXE and reopen the GUI.")


def _run(command: list[str], label: str) -> None:
    completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    if completed.returncode:
        detail = (completed.stderr or completed.stdout or "No diagnostic output").strip()
        raise RuntimeError(f"{label} failed.\n\n{detail[-4000:]}")


def _safe_name(image: Path) -> str:
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in image.stem).strip("._") or "unisharp_scene"


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _wait_for_local_port(port: int, timeout_seconds: float = 8.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.25):
                return True
        except OSError:
            time.sleep(0.15)
    return False


def open_ply_viewer(selected_ply: str | None) -> str:
    """Start a local Viser WebGL viewer and return an iframe for Gradio."""
    global _VIEWER_PROCESS
    if not selected_ply:
        raise gr.Error("\ubbf8\ub9ac\ubcf4\uae30\ud560 Unreal\uc6a9 Gaussian Splat PLY\ub97c \uc120\ud0dd\ud574 \uc8fc\uc138\uc694.")
    ply_path = Path(selected_ply).resolve()
    if not ply_path.is_file():
        raise gr.Error(f"PLY\ub97c \ucc3e\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4: {ply_path}")
    if _VIEWER_PROCESS is not None and _VIEWER_PROCESS.poll() is None:
        _VIEWER_PROCESS.terminate()
        try:
            _VIEWER_PROCESS.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _VIEWER_PROCESS.kill()
    port = _free_local_port()
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    _VIEWER_PROCESS = subprocess.Popen(
        [sys.executable, str(VIEWER_SCRIPT), str(ply_path), "--port", str(port)],
        cwd=REPO_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    if not _wait_for_local_port(port):
        raise gr.Error("PLY \ubdf0\uc5b4\ub97c \uc2dc\uc791\ud558\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4.")
    url = f"http://127.0.0.1:{port}"
    return f'<iframe src="{url}" style="width:100%; height:720px; border:1px solid #444; border-radius:8px;"></iframe>'


def _generate_one(
    image: Path,
    scene_name: str,
    destination: Path,
    camera_kind: str,
    force_square_pixels: bool,
    point_radius: float,
    include_background: bool,
    include_metric_reference: bool,
    save_ply: bool,
    checkpoint_path: Path,
    blender: Path,
) -> str:
    image = image.resolve()
    output_blend = destination / f"{scene_name}_unisharp.blend"
    output_ue_ply = destination / f"{scene_name}_unreal_gaussian_splat.ply"
    with tempfile.TemporaryDirectory(prefix="unisharp_blender_") as temp:
        temp_root = Path(temp)
        inference_command = [
            sys.executable,
            str(SCRIPTS / "infer_unisharp.py"),
            "--checkpoint",
            str(checkpoint_path),
            "--image",
            str(image),
            "--out-dir",
            str(temp_root),
            "--camera",
            camera_kind,
            "--save-ply",
            "--blender-only",
        ]
        if force_square_pixels and camera_kind in {"auto", "perspective"}:
            inference_command.append("--force-square-pixels")
        _run(inference_command, "UniSHARP inference")
        gaussian_files = list(temp_root.rglob("gaussians.ply"))
        if len(gaussian_files) != 1:
            raise RuntimeError("UniSHARP did not produce the expected Gaussian PLY.")
        source_ply = gaussian_files[0]
        colored_ply = temp_root / "colored_points.ply"
        _run([sys.executable, str(SCRIPTS / "export_colored_ply.py"), str(source_ply), str(colored_ply)], "Color conversion")
        blender_command = [
            str(blender),
            "--background",
            "--factory-startup",
            "--python",
            str(SCRIPTS / "make_blender_camera_preview.py"),
            "--",
            str(source_ply),
            str(colored_ply),
            str(image),
            str(output_blend),
            "--point-radius",
            str(point_radius),
            "--orientation",
            "negative_x_xminus90",
        ]
        if not include_background:
            blender_command.append("--no-background")
        if not include_metric_reference:
            blender_command.append("--no-metric-reference")
        _run(blender_command, "Blender export")
        if not output_blend.is_file():
            raise RuntimeError("Blender exited without creating the requested .blend file.")
        if save_ply:
            _run([sys.executable, str(SCRIPTS / "export_ue_gaussian_ply.py"), str(source_ply), str(output_ue_ply)], "Unreal PLY export")
    return str(output_blend)


def generate_blend(
    images: list[str] | str | None,
    output_folder: str,
    camera_kind: str,
    force_square_pixels: bool,
    point_radius: float,
    include_background: bool,
    include_metric_reference: bool,
    save_ply: bool,
) -> tuple[list[str], str, dict[str, object]]:
    if point_radius <= 0:
        raise gr.Error("\uc810 \ud45c\uc2dc \ubc18\uc9c0\ub984\uc740 0\ubcf4\ub2e4 \ucee4\uc57c \ud569\ub2c8\ub2e4.")
    checkpoint_path = DEFAULT_CHECKPOINT
    if not checkpoint_path.is_file():
        raise gr.Error(f"UniSHARP \uccb4\ud06c\ud3ec\uc778\ud2b8\ub97c \ucc3e\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4: {checkpoint_path}")
    paths = [Path(item) for item in ([images] if isinstance(images, str) else (images or []))]
    if not paths:
        raise gr.Error("\uc774\ubbf8\uc9c0\ub97c \ud558\ub098 \uc774\uc0c1 \uc120\ud0dd\ud574 \uc8fc\uc138\uc694.")
    destination = Path(output_folder).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    blender = _blender_executable()
    final_files: list[str] = []
    ply_files: list[str] = []
    for image in paths:
        if not image.is_file():
            raise gr.Error(f"\uc785\ub825 \uc774\ubbf8\uc9c0\ub97c \ucc3e\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4: {image}")
        scene_name = _safe_name(image) + ("_square_pixels" if force_square_pixels and camera_kind in {"auto", "perspective"} else "")
        final_files.append(
            _generate_one(
                image,
                scene_name,
                destination,
                camera_kind,
                force_square_pixels,
                point_radius,
                include_background,
                include_metric_reference,
                save_ply,
                checkpoint_path,
                blender,
            )
        )
        if save_ply:
            output_ply = destination / f"{scene_name}_unreal_gaussian_splat.ply"
            if output_ply.is_file():
                ply_files.append(str(output_ply))
    ply_note = " Unreal\uc6a9 Gaussian Splat PLY\ub3c4 \uc800\uc7a5\ud588\uc2b5\ub2c8\ub2e4." if save_ply else " Blender \ud30c\uc77c\ub9cc \uc800\uc7a5\ud588\uc2b5\ub2c8\ub2e4."
    selected_ply = ply_files[0] if len(ply_files) == 1 else None
    return final_files, f"\uc644\ub8cc: Blender \ud30c\uc77c {len(final_files)}\uac1c\ub97c \uc0dd\uc131\ud588\uc2b5\ub2c8\ub2e4.{ply_note}\n\n{destination}", gr.update(choices=ply_files, value=selected_ply)


with gr.Blocks(
    title="UniSHARP -> Blender",
    css="""
        #unisharp-header { display: flex; align-items: center; gap: 0.8rem; margin: 0.2rem 0 1.1rem; }
        #unisharp-header h1 { margin: 0; }
        #unisharp-header a { color: #8b949e; font-size: 0.9rem; text-decoration: none; }
        #unisharp-header a:hover { color: #f0f6fc; text-decoration: underline; }
        #section-basic, #section-input, #section-options, #section-result {
            border: 0;
            border-left: 3px solid #6e7681;
            border-radius: 0;
            padding: 0.05rem 0 0.05rem 0.65rem;
            margin: 1.1rem 0 0.55rem;
        }
        #section-basic h3, #section-input h3, #section-options h3, #section-result h3 {
            color: inherit;
            margin: 0;
        }
        #generate-button { margin: 0.8rem 0; }
    """,
) as demo:
    gr.HTML(
        "<div id='unisharp-header'><h1>\ub2e8\uc77c \uc774\ubbf8\uc9c0 \uac00\uc6b0\uc2dc\uc548 \ubcc0\uacbd</h1>"
        "<a href='https://github.com/Insta360-Research-Team/UniSHARP' target='_blank' rel='noopener'>GitHub ↗</a></div>"
    )

    with gr.Column():
        gr.Markdown("### \uae30\ubcf8 \uc124\uc815", elem_id="section-basic")
        with gr.Row():
            output_folder = gr.Textbox(label="\ucd9c\ub825 \ud3f4\ub354", value=str(DEFAULT_OUTPUT), scale=3)
            camera_kind = gr.Dropdown(
                [("\uc790\ub3d9", "auto"), ("\uc6d0\uadfc", "perspective"), ("\uc5b4\uc548", "fisheye"), ("\ud30c\ub178\ub77c\ub9c8", "panorama")],
                value="perspective",
                label="\uce74\uba54\ub77c \uc885\ub958",
                scale=1,
            )

    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("### \uc785\ub825 \uc774\ubbf8\uc9c0", elem_id="section-input")
            images = gr.File(
                label="\uc774\ubbf8\uc9c0 \ucd94\uac00 (\uc77c\ubc18 / \uc5b4\uc548 / ERP \ud30c\ub178\ub77c\ub9c8)",
                file_types=["image"],
                file_count="multiple",
                type="filepath",
                height=305,
            )

        with gr.Column(scale=2):
            with gr.Column():
                gr.Markdown("### \uc635\uc158", elem_id="section-options")
                force_square_pixels = gr.Checkbox(
                    label="\uc815\uc0ac\uac01\ud615 \ud53d\uc140 \uac15\uc81c (\uc138\ub85c \uc624\ubc84\ub808\uc774 \ubcf4\uc815)",
                    value=True,
                    info="\uc6d0\uadfc \uc0ac\uc9c4\uc5d0\uc11c\ub9cc \uc801\uc6a9\ub429\ub2c8\ub2e4. \ucd94\uc815\ub41c fx\ub97c \uc720\uc9c0\ud558\uace0 fy=fx\ub85c \ub9de\ucd94\ub294 \uc635\uc158\uc785\ub2c8\ub2e4.",
                )
                point_radius = gr.Number(
                    label="\uac00\uc6b0\uc2dc\uc548 \uc810 \ud45c\uc2dc \ubc18\uc9c0\ub984 (m)",
                    value=0.006,
                    minimum=0.0001,
                    maximum=1.0,
                    info="Blender \ubdf0\ud3ec\ud2b8\uc5d0\uc11c \uc810\uc744 \uc5bc\ub9c8\ub098 \ud06c\uac8c \ubcf4\uc77c\uc9c0 \uc815\ud558\ub294 \ud654\uba74\uc6a9 \ud06c\uae30\uc785\ub2c8\ub2e4. \uc2e4\uc81c 3D Gaussian\uc758 scale\uc740 \ubc14\ub00c\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4. \uac12\uc744 \ud0a4\uc6b0\uba74 \ube48\ud2c8\uc774 \uc904\uace0, \ub108\ubb34 \ud06c\uba74 \ub514\ud14c\uc77c\uc774 \ubb49\uac1c\uc9d1\ub2c8\ub2e4.",
                )
                include_background = gr.Checkbox(label="\uc6d0\ubcf8 \uc774\ubbf8\uc9c0\ub97c \uce74\uba54\ub77c \ubc30\uacbd\uc73c\ub85c \ud3ec\ud568", value=True)
                include_metric_reference = gr.Checkbox(label="1m \ub808\ud37c\ub7f0\uc2a4 \ud050\ube0c \ud3ec\ud568", value=True)
                save_ply = gr.Checkbox(label="Unreal\uc6a9 Gaussian Splat PLY \uc800\uc7a5", value=True)
    generate = gr.Button("Blender \ud30c\uc77c \uc0dd\uc131", variant="primary", size="lg", elem_id="generate-button")
    with gr.Column():
        gr.Markdown("### \uc0dd\uc131 \uacb0\uacfc", elem_id="section-result")
        result_files = gr.File(label="\uc0dd\uc131\ub41c Blender \ud30c\uc77c", file_count="multiple")
        status = gr.Markdown()
    gr.Markdown("## Unreal\uc6a9 Gaussian Splat PLY \ubbf8\ub9ac\ubcf4\uae30")
    viewer_ply = gr.Dropdown(label="\ubbf8\ub9ac\ubcf4\uae30\ud560 PLY", choices=[], interactive=True)
    open_viewer = gr.Button("PLY \ubbf8\ub9ac\ubcf4\uae30 \uc5f4\uae30")
    viewer_html = gr.HTML("<div>PLY\ub97c \uc120\ud0dd\ud55c \ub4a4 \ubbf8\ub9ac\ubcf4\uae30\ub97c \uc5f4\uc5b4 \uc8fc\uc138\uc694.</div>")
    generate.click(
        generate_blend,
        inputs=[images, output_folder, camera_kind, force_square_pixels, point_radius, include_background, include_metric_reference, save_ply],
        outputs=[result_files, status, viewer_ply],
    )
    open_viewer.click(open_ply_viewer, inputs=viewer_ply, outputs=viewer_html)


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True, footer_links=[])

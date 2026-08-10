"""Create a Blender scene that displays a colored point-cloud PLY."""

from __future__ import annotations

import sys
from pathlib import Path

import bpy


def arguments() -> tuple[Path, Path]:
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit("Pass input PLY and output BLEND after --")
    values = argv[argv.index("--") + 1 :]
    if len(values) != 2:
        raise SystemExit("Usage: blender --background --python script.py -- input.ply output.blend")
    return Path(values[0]), Path(values[1])


def main() -> None:
    input_path, output_path = arguments()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.ply_import(filepath=str(input_path))
    point_mesh = bpy.context.selected_objects[0]
    point_mesh.name = "UniSHARP Colored Gaussians"

    material = bpy.data.materials.new("Gaussian vertex colors")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    color = nodes.new("ShaderNodeVertexColor")
    color.layer_name = "Col"
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = 1.0
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(color.outputs["Color"], shader.inputs["Base Color"])
    links.new(color.outputs["Alpha"], shader.inputs["Alpha"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])

    tree = bpy.data.node_groups.new("Display Gaussian points", "GeometryNodeTree")
    tree.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    tree.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    group_input = tree.nodes.new("NodeGroupInput")
    group_output = tree.nodes.new("NodeGroupOutput")
    mesh_to_points = tree.nodes.new("GeometryNodeMeshToPoints")
    mesh_to_points.mode = "VERTICES"
    mesh_to_points.inputs["Radius"].default_value = 0.006
    set_material = tree.nodes.new("GeometryNodeSetMaterial")
    set_material.inputs["Material"].default_value = material
    tree.links.new(group_input.outputs["Geometry"], mesh_to_points.inputs["Mesh"])
    tree.links.new(mesh_to_points.outputs["Points"], set_material.inputs["Geometry"])
    tree.links.new(set_material.outputs["Geometry"], group_output.inputs["Geometry"])
    modifier = point_mesh.modifiers.new("Render colored Gaussian points", "NODES")
    modifier.node_group = tree

    point_mesh.select_set(True)
    bpy.context.view_layer.objects.active = point_mesh
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()

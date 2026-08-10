"""Run inside Unreal Editor to create one MLSLabs Gaussian Splat Blueprint asset."""

from __future__ import annotations

import os

import unreal


ASSET_NAME = os.environ["UNREAL_SPLAT_ASSET_NAME"]
DESTINATION = os.environ["UNREAL_SPLAT_DESTINATION"]
RELATIVE_PLY = os.environ["UNREAL_SPLAT_RELATIVE_PLY"]
ASSET_PATH = f"{DESTINATION}/{ASSET_NAME}"


def main() -> None:
    asset_lib = unreal.EditorAssetLibrary
    if asset_lib.does_asset_exist(ASSET_PATH):
        blueprint = asset_lib.load_asset(ASSET_PATH)
        unreal.log(f"Updating existing Gaussian Splat asset: {ASSET_PATH}")
    else:
        parent_class = unreal.load_class(None, "/Script/MLSLabsRenderer.GaussianSplattingActor")
        if parent_class is None:
            raise RuntimeError("MLSLabsRenderer's GaussianSplattingActor class is unavailable.")
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", parent_class)
        blueprint = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            ASSET_NAME, DESTINATION, unreal.Blueprint, factory
        )
        if blueprint is None:
            raise RuntimeError("Failed to create the Gaussian Splat Blueprint asset.")
        unreal.log(f"Created Gaussian Splat asset: {ASSET_PATH}")

    generated_class = blueprint.generated_class()
    default_actor = unreal.get_default_object(generated_class)
    component = default_actor.get_editor_property("splatting_component")
    component.set_editor_property("splat_data_path", RELATIVE_PLY)
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    if not asset_lib.save_loaded_asset(blueprint, only_if_is_dirty=False):
        raise RuntimeError(f"Failed to save {ASSET_PATH}")
    unreal.log(f"UNREAL_SPLAT_ASSET_READY={ASSET_PATH}")


main()

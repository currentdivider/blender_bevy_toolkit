"""
Bevy is a game engine written in RUST, but it crrently lacks any sort of
scene editor. Blender is a 3D graphics program that seems like it would
be a good fit. This exporter converts from a blender file into a .scn file
that can be loaded into bevy.
"""
import os
import sys
import logging
import copy

import bpy
from bpy.app.handlers import persistent  # pylint: disable=E0401
from bpy.props import (BoolProperty,
                       IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       )
from bpy_extras.io_utils import ExportHelper

from .utils import jdict
from . import components
from . import operators
from . import component_base
from . import export

logger = logging.getLogger(__name__)

bl_info = {
    "name": "Bevy Game Engine Toolkit",
    "blender": (2, 90, 0),
    "category": "Game",
}


class BevyComponentsPanel(bpy.types.Panel):
    """The panel in which buttons that add/remove components are shown"""

    bl_idname = "OBJECT_PT_bevy_components_panel"
    bl_label = "Bevy Components"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    def draw(self, _context):
        """Create the UI for the panel"""
        row = self.layout.row()
        row.operator("object.add_bevy_component")
        row.operator("object.remove_bevy_component")


def register():
    """Blender needs to know about all our classes and UI panels
    so that it can draw/store things"""
    logger.info(jdict(event="registering_bevy_addon", state="start"))
    bpy.utils.register_class(BevyComponentsPanel)
    bpy.utils.register_class(operators.RemoveBevyComponent)
    bpy.utils.register_class(operators.AddBevyComponent)
    bpy.utils.register_class(ExportBevy)

    bpy.app.handlers.load_post.append(load_handler)

    bpy.types.TOPBAR_MT_file_export.append(menu_func)
    logger.info(jdict(event="registering_bevy_addon", state="end"))


def unregister():
    """When closing blender or uninstalling the addon we should leave
    things nice and clean...."""
    logger.info(jdict(event="unregistering_bevy_addon", state="start"))
    bpy.utils.unregister_class(BevyComponentsPanel)
    bpy.utils.unregister_class(operators.RemoveBevyComponent)
    bpy.utils.unregister_class(operators.AddBevyComponent)
    bpy.utils.unregister_class(ExportBevy)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    bpy.app.handlers.load_post.remove(load_handler)

    for component in component_base.COMPONENTS:
        logger.info(jdict(event="unregistering_component",
                    component=str(component)))
        component.unregister()
    logger.info(jdict(event="unregistering_bevy_addon", state="end"))


@persistent
def load_handler(_dummy):
    """Scan the folder of the blend file for components to add"""
    for component in component_base.COMPONENTS:
        component.unregister()

    components.generate_component_list()
    operators.update_all_component_list()

    for component in component_base.COMPONENTS:
        logger.info(jdict(event="registering_component",
                    component=str(component)))
        component.register()


def menu_func(self, _context):
    """Add export operation to the menu"""
    self.layout.operator(ExportBevy.bl_idname, text="Bevy Engine (.scn)")


class ExportBevy(bpy.types.Operator, ExportHelper):
    """Selection to Godot"""

    bl_idname = "export_bevy.scn"
    bl_label = "Export to Bevy"
    bl_options = {"PRESET"}

    filename_ext = ".scn"
    filter_glob: bpy.props.StringProperty(default="*.scn", options={"HIDDEN"})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator setting before calling.
    export_gltf: BoolProperty(
        name="Export GLTFs",
        description="Export GLTF file for each object",
        default=True,
    )

    batch_export_format: EnumProperty(
        name='Format',
        items=(('GLB', 'glTF Binary (.glb)',
                'Exports a single file, with all data packed in binary form. '
                'Most efficient and portable, but more difficult to edit later'),
               ('GLTF_EMBEDDED', 'glTF Embedded (.gltf)',
                'Exports a single file, with all data packed in JSON. '
                'Less efficient than binary, but easier to edit later'),
               ('GLTF_SEPARATE', 'glTF Separate (.gltf + .bin + textures)',
                'Exports multiple files, with separate JSON, binary and texture data. '
                'Easiest to edit later')),
        description=(
            'Output format and embedding options. Binary is most efficient, '
            'but JSON (embedded or separate) may be easier to edit later'
        ),
        default='GLB'
    )

    batch_export_copyright: StringProperty(
        name='Copyright',
        description='Legal rights and conditions for the model',
        default=''
    )

    batch_export_image_format: EnumProperty(
        name='Images',
        items=(('AUTO', 'Automatic',
                'Save PNGs as PNGs and JPEGs as JPEGs.\n'
                'If neither one, use PNG'),
               ('JPEG', 'JPEG Format (.jpg)',
                'Save images as JPEGs. (Images that need alpha are saved as PNGs though.)\n'
                'Be aware of a possible loss in quality'),
               ),
        description=(
            'Output format for images. PNG is lossless and generally preferred, but JPEG might be preferable for web '
            'applications due to the smaller file size'
        ),
        default='AUTO'
    )

    batch_export_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=True,
    )

    batch_export_levels: IntProperty(
        name='Collection Levels',
        description='Set the levels of collections',
        default=2
    )

    batch_export_materials: EnumProperty(
        name='Materials',
        items=(('EXPORT', 'Export',
                'Export all materials used by included objects'),
               ('PLACEHOLDER', 'Placeholder',
                'Do not export materials, but write multiple primitive groups per mesh, keeping material slot information'),
               ('NONE', 'No export',
                'Do not export materials, and combine mesh primitive groups, losing material slot information')),
        description='Export materials ',
        default='EXPORT'
    )

    batch_export_cameras: BoolProperty(
        name='Export Cameras',
        description='Export cameras',
        default=False
    )

    batch_export_extras: BoolProperty(
        name='Export Custom Properties',
        description='Export custom properties as glTF extras',
        default=False
    )

    batch_export_apply: BoolProperty(
        name='Export Apply Modifiers',
        description='Apply modifiers (excluding Armatures) to mesh objects -'
                    'WARNING: prevents exporting shape keys',
        default=False
    )

    batch_export_yup: BoolProperty(
        name='+Y Up',
        description='Export using glTF convention, +Y up',
        default=True
    )

    batch_export_texcoords: BoolProperty(
        name='UVs',
        description='Export UVs (texture coordinates) with meshes',
        default=True
    )

    batch_export_normals: BoolProperty(
        name='Normals',
        description='Export vertex normals with meshes',
        default=True
    )

    batch_export_tangents: BoolProperty(
        name='Tangents',
        description='Export vertex tangents with meshes',
        default=False
    )

    batch_export_colors: BoolProperty(
        name='Vertex Colors',
        description='Export vertex colors with meshes',
        default=True
    )

    batch_export_apply: BoolProperty(
        name='Apply Modifiers',
        description='Apply modifiers (excluding Armatures) to mesh objects -'
                    'WARNING: prevents exporting shape keys',
        default=False
    )

    def execute(self, context):
        """Begin the export"""

        if not self.filepath:
            raise Exception("filepath not set")

        do_export(
            {
                "output_filepath": self.filepath,
                "mesh_output_folder": "meshes",
                "material_output_folder": "materials",
                "texture_output_folder": "textures",
                "make_duplicates_real": False,
            }
        )

        # Blender GLTF Exporter
        if self.export_gltf:
            # get the folder
            folder_path = os.path.dirname(self.filepath)

            # get objects selected in the viewport
            viewport_selection = context.selected_objects
            obj_export_list = [i for i in context.scene.objects]

            # deselect all objects
            bpy.ops.object.select_all(action='DESELECT')

            for item in obj_export_list:
                item.select_set(True)
                # if item.type == 'MESH':
                file_path = os.path.join(folder_path, f"{item.name}")

                # Store original object transform
                store_location = copy.deepcopy(item.location)
                store_rotation = copy.deepcopy(item.rotation_quaternion)
                store_scale = copy.deepcopy(item.scale)

                item.location = [0.0, 0.0, 0.0]
                item.rotation_quaternion = [1.0, 0.0, 0.0, 0.0]
                item.scale = [1.0, 1.0, 1.0]

                bpy.ops.export_scene.gltf(
                    filepath=file_path,
                    use_selection=self.batch_export_selection,
                    export_format=self.batch_export_format,
                    export_copyright=self.batch_export_copyright,
                    export_image_format=self.batch_export_image_format,
                    export_materials=self.batch_export_materials,
                    export_colors=self.batch_export_colors,
                    export_cameras=self.batch_export_cameras,
                    export_extras=self.batch_export_extras,
                    export_yup=self.batch_export_yup,
                    export_apply=self.batch_export_apply,
                    export_texcoords=self.batch_export_texcoords,
                    export_normals=self.batch_export_normals,
                    export_tangents=self.batch_export_tangents,
                )

                item.select_set(False)

                # Restore object transform
                item.location = store_location
                item.rotation_quaternion = store_rotation
                item.scale = store_scale

            # restore viewport selection
            for ob in viewport_selection:
                ob.select_set(True)

        return {"FINISHED"}


def do_export(config):
    """Start the export. This is a global function to ensure it can be called
    both from the operator and from external scripts"""
    export.export_all(config)

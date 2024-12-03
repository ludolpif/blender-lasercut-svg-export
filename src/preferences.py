# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

if "bpy" in locals():
    import importlib
    importlib.reload(enums)
    importlib.reload(props)
else:
    from . import enums
    from . import props

import bpy

def update_defaults(prefs: "LasercutSvgExportPreferences", context: bpy.types.Context) -> None:
    props.unregister_scene_props()
    props.register_scene_props()


class LasercutSvgExportPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    laser_width: bpy.props.FloatProperty(  # type: ignore
        name="Laser Beam Width",
        description="Compensate for material removed by the laser. Edges marked as 'sharp' will be "
        "moved by half this amount before exporting to SVG. The actual setting is stored on the "
        "Scene; this is just the default",
        default=0.16,
        min=0.0,
        max=10.0,
        soft_max=1.0,
        subtype="DISTANCE",
        unit="LENGTH",
        update=update_defaults,
    )

    material_width: bpy.props.FloatProperty(  # type: ignore
        name="Material Width",
        description="The shape packing will attempt to fill the material width. The actual setting is stored on the "
        "Scene; this is just the default",
        default=300.0,
        min=0.0,
        soft_max=500.0,
        subtype="DISTANCE",
        unit="LENGTH",
        update=update_defaults,
    )

    material_length: bpy.props.FloatProperty(  # type: ignore
        name="Material Length",
        description="The shape packing will attempt to fill the material length. The actual setting is stored on the "
        "Scene; this is just the default",
        default=300.0,
        min=0.0,
        soft_max=500.0,
        subtype="DISTANCE",
        unit="LENGTH",
        update=update_defaults,
    )

    margin: bpy.props.FloatProperty(  # type: ignore
        name="Margin",
        description="The distance from the edge of the material to the closest shape. The actual setting is stored "
        "on the Scene; this is just the default",
        default=5.0,
        min=0.0,
        soft_max=50.0,
        subtype="DISTANCE",
        unit="LENGTH",
        update=update_defaults,
    )

    material_thickness: bpy.props.FloatProperty(  # type: ignore
        name="Mat. Thickness",
        description="The thickness of the to-be-cut material. The actual setting is stored on the "
        "Scene; this is just the default",
        default=3.0,
        min=0.0,
        soft_max=10.0,
        subtype="DISTANCE",
        unit="LENGTH",
        update=update_defaults,
    )

    shape_padding: bpy.props.FloatProperty(  # type: ignore
        name="Shape Padding",
        description="The shape packing will keep this distance as padding around each shape. The padding will be "
        "double between shapes, and single between the shape and the outer edge of the document. The actual setting "
        "is stored on the Scene; this is just the default",
        default=1.0,
        min=0.0,
        max=50.0,
        soft_max=5.0,
        subtype="DISTANCE",
        unit="LENGTH",
        update=update_defaults,
    )
    pack_sort: bpy.props.EnumProperty(  # type: ignore
        name="Pack Sorting",
        items=enums.pack_sort_items,
        description="The shape packing will sort the bounding boxes of the shapes before trying to pack them. "
        "Different sorting approaches will be useful for different situations (square shapes vs. longer shapes, etc.). "
        "The actual setting is stored on the Scene; this is just the default",
        default="SORT_PERI",
        update=update_defaults,
    )
    pack_may_rotate: bpy.props.BoolProperty(  # type: ignore
        name="Allow Rotation",
        description="Whether the shape packing algorithm is allowed to rotate shapes by 90 degrees or not. "
        "The actual setting is stored on the Scene; this is just the default",
        default=True,
        update=update_defaults,
    )
    open_dir_after_export: bpy.props.BoolProperty(  # type: ignore
        name="Open Directory After Export",
        description="Open a file manager / explorer after the export to SVG has finished",
        default=True,
    )

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.label(text="This add-on assumes that 1 Blender unit is 1 mm.")

        col = layout.column(align=True)
        col.label(text="Preferences:")
        col.use_property_split = True
        col.prop(self, "open_dir_after_export")

        col = layout.column(align=True)
        col.label(text="Default settings:")
        col.use_property_split = True
        col.prop(self, "laser_width")
        col.prop(self, "material_width")
        col.prop(self, "material_length")
        col.prop(self, "material_thickness")
        col.prop(self, "margin")
        col.prop(self, "shape_padding")
        col.prop(self, "pack_sort")
        col.prop(self, "pack_may_rotate")

        col = layout.column(align=True)
        col.label(
            text="The actual settings are stored on the Scene; these are just the defaults."
        )
        col.label(
            text="New defaults will be in effect after the next Blender restart or add-on reload."
        )

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
else:
    from . import enums

import bpy


def register_scene_props() -> None:
    prefs = bpy.context.preferences.addons[__package__].preferences
    bpy.types.Scene.lasercut_svg_export_laser_width = bpy.props.FloatProperty(
        name="Laser Width",
        description="Compensate for material removed by the laser. Edges marked as 'sharp' will be "
        "moved by half this amount before exporting to SVG",
        default=prefs.laser_width,
        min=0.0,
        max=10.0,
        soft_max=1.0,
        subtype="DISTANCE",
        unit="LENGTH",
    )
    bpy.types.Scene.lasercut_svg_export_material_width = bpy.props.FloatProperty(
        name="Material Width",
        description="The shape packing will attempt to fill the material width",
        default=prefs.material_width,
        min=0.0,
        max=100000.0,
        soft_max=500.0,
        subtype="DISTANCE",
        unit="LENGTH",
    )
    bpy.types.Scene.lasercut_svg_export_material_length = bpy.props.FloatProperty(
        name="Material Length",
        description="The shape packing will attempt to fill the material length",
        default=prefs.material_length,
        min=0.0,
        max=100000.0,
        soft_max=500.0,
        subtype="DISTANCE",
        unit="LENGTH",
    )
    bpy.types.Scene.lasercut_svg_export_material_thickness = bpy.props.FloatProperty(
        name="Mat. Thickness",
        description="The thickness of the to-be-cut material",
        default=prefs.material_thickness,
        min=0.0,
        soft_max=10.0,
        subtype="DISTANCE",
        unit="LENGTH",
    )
    bpy.types.Scene.lasercut_svg_export_margin = bpy.props.FloatProperty(
        name="Margin",
        description="The distance from the edge of the material to the closest shape",
        default=5.0,
        min=0.0,
        soft_max=50.0,
        subtype="DISTANCE",
        unit="LENGTH",
    )
    bpy.types.Scene.lasercut_svg_export_shape_padding = bpy.props.FloatProperty(
        name="Shape Padding",
        description="The shape packing will keep this distance as padding around each shape. The padding will be "
        "double between shapes, and single between the shape and the outer edge of the document",
        default=prefs.shape_padding,
        min=0.0,
        max=50.0,
        soft_max=5.0,
        subtype="DISTANCE",
        unit="LENGTH",
    )
    bpy.types.Scene.lasercut_svg_export_pack_sort = bpy.props.EnumProperty(
        name="Pack Sorting",
        items=enums.pack_sort_items,
        description="The shape packing will sort the bounding boxes of the shapes before trying to pack them. "
        "Different sorting approaches will be useful for different situations (square shapes vs. longer shapes, etc.)",
        default=prefs.pack_sort,
    )
    bpy.types.Scene.lasercut_svg_export_pack_may_rotate = bpy.props.BoolProperty(
        name="Allow Rotation",
        description="Whether the shape packing algorithm is allowed to rotate shapes by 90 degrees or not",
        default=prefs.pack_may_rotate,
    )


def unregister_scene_props() -> None:
    del bpy.types.Scene.lasercut_svg_export_laser_width
    del bpy.types.Scene.lasercut_svg_export_material_width
    del bpy.types.Scene.lasercut_svg_export_material_length
    del bpy.types.Scene.lasercut_svg_export_material_thickness
    del bpy.types.Scene.lasercut_svg_export_margin
    del bpy.types.Scene.lasercut_svg_export_shape_padding
    del bpy.types.Scene.lasercut_svg_export_pack_sort
    del bpy.types.Scene.lasercut_svg_export_pack_may_rotate


def register_object_props() -> None:
    bpy.types.Object.lasercut_svg_export_exclude = bpy.props.BoolProperty(
        name="Exclude from Export",
        description="This object will not be exported to SVG",
        default=False,
    )


def unregister_object_props() -> None:
    del bpy.types.Object.lasercut_svg_export_exclude

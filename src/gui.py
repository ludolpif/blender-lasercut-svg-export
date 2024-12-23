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

import bpy


class LasercutSvgExportPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Export"


class LASERCUTSVGEXPORT_PT_sidepanel(LasercutSvgExportPanel, bpy.types.Panel):
    bl_label = "Lasercut SVG Export"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(context.scene, "lasercut_svg_export_laser_width")
        col.prop(context.scene, "lasercut_svg_export_material_width")
        col.prop(context.scene, "lasercut_svg_export_material_length")
        col.prop(context.scene, "lasercut_svg_export_material_thickness")
        col.prop(context.scene, "lasercut_svg_export_margin")
        col.prop(context.scene, "lasercut_svg_export_shape_padding")
        col.operator("lasercut_svg_export.setup_scene", icon="TOOL_SETTINGS")
        col.operator("lasercut_svg_export.scale_scene", icon="ZOOM_IN")

        col = layout.column(align=True)
        col.use_property_split = False
        col.label(text="Packing Options:")
        col.prop(context.scene, "lasercut_svg_export_pack_may_rotate")
        col.prop(context.scene, "lasercut_svg_export_pack_sort", text="")

        layout.operator("export_mesh.lasercut_svg_export", icon="EXPORT")


class LASERCUTSVGEXPORT_PT_objects(LasercutSvgExportPanel, bpy.types.Panel):
    bl_label = "Object Mode meshes operations"
    bl_parent_id = "LASERCUTSVGEXPORT_PT_sidepanel"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        col = layout.column(align=True)
        # FIXME svg_export_exclude is only for active objects and not selected objets, not very intuitive and may be superseeded by face marking
        # col.prop(context.object, "lasercut_svg_export_exclude")
        col.operator("lasercut_svg_export.add_solidify", icon="MOD_SOLIDIFY")
        # TODO I have hopes to not flatten anything, just select faces to export, removing the axis-alignment constraint
        # col.operator("lasercut_svg_export.align_to_local_axis", icon="EMPTY_AXIS")
        op_props = col.operator("object.transform_apply",
                                text="Apply Global Scale to Local", translate=False, icon="EMPTY_AXIS")
        op_props.location = False
        op_props.rotation = False
        op_props.scale = True
        op_props.properties = False

        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        col.operator("lasercut_svg_export.boolean_cut", icon="MOD_BOOLEAN")
        col.enabled = bool(context.selected_objects)


class LASERCUTSVGEXPORT_PT_edit_ops(LasercutSvgExportPanel, bpy.types.Panel):
    bl_label = "Edit Mode operations"
    bl_parent_id = "LASERCUTSVGEXPORT_PT_sidepanel"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.enabled = bool(context.object and context.mode == "EDIT_MESH")

        col = layout.column(align=True)
        col.operator("lasercut_svg_export.select_export_edges")
        col.operator("lasercut_svg_export.separate_mesh")


class LASERCUTSVGEXPORT_PT_faces(LasercutSvgExportPanel, bpy.types.Panel):
    bl_label = "Edit Mode faces operations"
    bl_parent_id = "LASERCUTSVGEXPORT_PT_sidepanel"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.enabled = bool(context.object and context.mode == "EDIT_MESH")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.split(factor=0.8)
        row.label(text="Mark lasercut faces")
        row.operator("lasercut_svg_export.mark_faces",
                     text="", icon="X").mark = 0
        row.operator("lasercut_svg_export.mark_faces",
                     text="", icon="CHECKMARK").mark = 1


class LASERCUTSVGEXPORT_PT_edges(LasercutSvgExportPanel, bpy.types.Panel):
    bl_label = "Edit Mode edges operations"
    bl_parent_id = "LASERCUTSVGEXPORT_PT_sidepanel"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.enabled = bpy.ops.lasercut_svg_export.print_edges.poll()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.split(factor=0.8)
        row.label(text="Kerf Compensation")
        row.operator("mesh.mark_seam", text="", icon="X").clear = False
        row.operator("mesh.mark_seam", text="", icon="CHECKMARK").clear = True

        row = col.row(align=True)
        row.split(factor=0.8)
        row.label(text="Engrave")
        row.operator("mesh.mark_sharp", text="", icon="X").clear = True
        row.operator("mesh.mark_sharp", text="",
                     icon="CHECKMARK").clear = False

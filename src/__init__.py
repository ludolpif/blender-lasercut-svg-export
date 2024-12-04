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
    importlib.reload(gui)
    importlib.reload(operators)
    importlib.reload(preferences)
    importlib.reload(props)
else:
    from . import gui
    from . import operators
    from . import preferences
    from . import props

import bpy


classes = (
    preferences.LasercutSvgExportPreferences,
    gui.LASERCUTSVGEXPORT_PT_sidepanel,
    gui.LASERCUTSVGEXPORT_PT_objects,
    gui.LASERCUTSVGEXPORT_PT_faces,
    gui.LASERCUTSVGEXPORT_PT_edges,
    operators.EXPORT_MESH_OT_lasercut_svg_export,
    operators.LASERCUTSVGEXPORT_OT_setup_scene,
    operators.LASERCUTSVGEXPORT_OT_scale_scene,
    operators.LASERCUTSVGEXPORT_OT_add_solidify,
    operators.LASERCUTSVGEXPORT_OT_select_export_edges,
    operators.LASERCUTSVGEXPORT_OT_island_faces,
    # operators.LASERCUTSVGEXPORT_OT_straighten,
    # operators.LASERCUTSVGEXPORT_OT_extrude_finger,
    operators.LASERCUTSVGEXPORT_OT_separate_mesh,
    operators.LASERCUTSVGEXPORT_OT_boolean_cut,
    operators.LASERCUTSVGEXPORT_OT_mark_faces,
)

_register, _unregister = bpy.utils.register_classes_factory(classes)


def _export_menu(
    self: bpy.types.TOPBAR_MT_file_export, context: bpy.types.Context
) -> None:
    self.layout.operator("export_mesh.lasercut_svg_export")


def register() -> None:
    _register()
    props.register_scene_props()
    props.register_object_props()
    bpy.types.TOPBAR_MT_file_export.append(_export_menu)


def unregister() -> None:
    bpy.types.TOPBAR_MT_file_export.remove(_export_menu)
    props.unregister_object_props()
    props.unregister_scene_props()
    _unregister()

# XXX shown in tissue add-on, unknown purpose
# if __name__ == "__main__":
#    register()

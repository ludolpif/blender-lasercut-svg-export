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

from pathlib import Path
from collections import defaultdict

import bpy
import bmesh
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector


is_first_load = "svg_export" not in locals()
if is_first_load:
    from . import svg_export, mesh_analysis  # , straightener
else:
    import importlib

    svg_export = importlib.reload(svg_export)
    mesh_analysis = importlib.reload(mesh_analysis)
    # straightener = importlib.reload(straightener)


class EXPORT_MESH_OT_lasercut_svg_export(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.lasercut_svg_export"
    bl_label = "Lasercut SVG Export"
    bl_description = (
        "Export selected meshes to 2D SVG file."
        "Faces needs to be marked first, and must be planar, possibly with holes"
    )
    bl_options = {"REGISTER"}  # No UNDO

    filename_ext = ".svg"

    export_shape_table: bpy.props.BoolProperty(  # type:ignore
        name="Shape Table",
        description="Include a table listing the shapes and their sizes",
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return len(cls._exportable_objects(context)) > 0

    def execute(self, context: bpy.types.Context) -> set[str]:
        depsgraph = context.view_layer.depsgraph
        to_export = self._exportable_objects(context)

        scene = context.scene
        options = mesh_analysis.Options(
            laser_width=scene.lasercut_svg_export_laser_width,
            material_width=scene.lasercut_svg_export_material_width,
            material_length=scene.lasercut_svg_export_material_length,
            margin=scene.lasercut_svg_export_margin,
            shape_padding=scene.lasercut_svg_export_shape_padding,
            pack_sort=scene.lasercut_svg_export_pack_sort,
            pack_may_rotate=scene.lasercut_svg_export_pack_may_rotate,
            shape_table=self.export_shape_table,
        )
        filepath = Path(self.filepath)
        try:
            canvas_size = svg_export.write(
                depsgraph, filepath, to_export, options)
        except svg_export.NoShapes:
            self.report({"ERROR"}, "No shapes to export, aborting.")
            return {"CANCELLED"}

        self.report(
            {"INFO"}, f"Created {canvas_size[0]} x {
                canvas_size[1]} mm SVG file"
        )

        prefs = context.preferences.addons[__package__].preferences
        if prefs.open_dir_after_export:
            bpy.ops.wm.path_open(filepath=str(filepath.parent))

        return {"FINISHED"}

    @staticmethod
    def _exportable_objects(context: bpy.types.Context) -> list[bpy.types.Object]:
        return [
            ob
            for ob in context.selected_objects
            if ob.type == "MESH" and not ob.lasercut_svg_export_exclude
        ]


class LASERCUTSVGEXPORT_OT_setup_scene(bpy.types.Operator):
    bl_idname = "lasercut_svg_export.setup_scene"
    bl_label = "Setup Scene for mm"
    bl_description = "Configure the Scene and 3D Viewport for mm units"

    def execute(self, context: bpy.types.Context) -> set[str]:
        # Configure the scene:
        s = context.scene
        s.unit_settings.scale_length = 0.001
        s.unit_settings.length_unit = "MILLIMETERS"

        # Configure the grid in 3D viewports:
        for win in context.window_manager.windows:
            for area in win.screen.areas:
                if area.type != "VIEW_3D":
                    continue
                space_data = area.spaces.active
                space_data.overlay.grid_scale = 0.001

        return {"FINISHED"}


class LASERCUTSVGEXPORT_OT_scale_scene(bpy.types.Operator):
    bl_idname = "lasercut_svg_export.scale_scene"
    bl_label = "Scale default scene items"
    bl_description = "Remove default Cube, scale default light and camera for objects in 10cm sine range"

    def execute(self, context: bpy.types.Context) -> set[str]:
        old_pivot_point = bpy.context.scene.tool_settings.transform_pivot_point

        # Replace default Cube if exists by a 100*100mm plane
        if 'Cube' in bpy.data.objects:
            default_cube = bpy.data.objects['Cube']
            bpy.ops.object.select_all(action='DESELECT')
            default_cube.select_set(True)
            bpy.ops.object.delete(use_global=False)
            if not 'Plane' in bpy.data.objects:
                bpy.ops.mesh.primitive_plane_add(
                    size=100, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.context.view_layer.objects.active = bpy.data.objects['Plane']
                bpy.ops.lasercut_svg_export.add_solidify()

        # Note: mode_set() can fail if active element was removed (this is why 'Plane' is made active)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Select and configure default Camera to not clip before 2 meters far
        if 'Camera' in bpy.data.objects:
            default_camera = bpy.data.objects['Camera']
            default_camera.select_set(True)
            bpy.context.view_layer.objects.active = default_camera
            bpy.context.object.data.clip_start = 20
            bpy.context.object.data.clip_end = 2000
            if bpy.context.object.scale.length > 2:
                # Don't scale more than once (initial is srqt(3) ~= 1.71)
                default_camera.select_set(False)

        # Select and configure default Light to 1 Watt
        if 'Light' in bpy.data.objects:
            default_light = bpy.data.objects['Light']
            default_light.select_set(True)
            bpy.context.view_layer.objects.active = default_light
            bpy.context.object.data.energy = 1e+06
            if bpy.context.object.scale.length > 2:
                # Don't scale more than once (initial is srqt(3) ~= 1.71)
                default_light.select_set(False)

        # Scale by 50 from Global center select objects (maybe Camera and Light)
        if bpy.context.selected_objects:
            bpy.ops.view3d.snap_cursor_to_center()
            bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
            bpy.ops.transform.resize(value=(50, 50, 50), orient_type='GLOBAL')
            bpy.ops.object.select_all(action='DESELECT')

            # Unzoom all 3D views
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            # XXX can't make it unzoom more than one step, even with delta=-1000
                            for i in range(20):
                                bpy.ops.view3d.zoom(delta=-1)

        bpy.context.scene.tool_settings.transform_pivot_point = old_pivot_point

        return {"FINISHED"}


class LASERCUTSVGEXPORT_OT_add_solidify(bpy.types.Operator):
    bl_idname = "lasercut_svg_export.add_solidify"
    bl_label = "Add Solidify Modifier"
    bl_description = "Add a solidify modifier to the selected mesh objects"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return any(
            ob.type == "MESH" and ob.mode == "OBJECT" for ob in context.selected_objects
        )

    def execute(self, context: bpy.types.Context) -> set[str]:
        for ob in context.selected_objects:
            if ob.type != "MESH":
                continue
            if ob.mode != "OBJECT":
                continue
            self.add_modifier(context, ob)
        return {"FINISHED"}

    def add_modifier(self, context: bpy.types.Context, ob: bpy.types.Object) -> None:
        mod = ob.modifiers.new("Solidify", "SOLIDIFY")
        mod.thickness = 0.001
        mod.offset = 1.0
        mod.use_even_offset = True
        mod.use_quality_normals = True
        mod.use_rim = True
        mod.use_rim_only = False
        mod.show_expanded = False
        mod.material_offset = 1
        mod.material_offset_rim = 1
        mod.show_in_editmode = False

        driver_rna_path = f'modifiers["{mod.name}"].thickness'
        ob.driver_remove(driver_rna_path)  # prevent double drivers
        fcurve = ob.driver_add(driver_rna_path)
        driver = fcurve.driver
        driver.expression = "thickness"
        dvar = driver.variables.new()
        dvar.name = "thickness"
        dvar.type = "SINGLE_PROP"
        dvar.targets[0].id_type = "SCENE"
        dvar.targets[0].id = context.scene
        dvar.targets[0].data_path = f"lasercut_svg_export_material_thickness"


class LASERCUTSVGEXPORT_OT_select_export_edges(bpy.types.Operator):
    bl_idname = "lasercut_svg_export.select_export_edges"
    bl_label = "Select Export Edges"
    bl_description = "Select all edges that will be exported to SVG"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return any(
            ob.type == "MESH" and ob.mode == "EDIT" for ob in context.selected_objects
        )

    def execute(self, context: bpy.types.Context) -> set[str]:
        for ob in context.selected_objects:
            if ob.type != "MESH":
                continue
            if ob.mode != "EDIT":
                continue
            mesh_analysis.select_export_edges(ob)
        return {"FINISHED"}


class LASERCUTSVGEXPORT_OT_island_faces(bpy.types.Operator):
    bl_idname = "lasercut_svg_export.island_faces"
    bl_label = "Add Faces to Islands"
    bl_description = ""

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return any(
            ob.type == "MESH" and ob.mode == "EDIT" for ob in context.selected_objects
        )

    def execute(self, context: bpy.types.Context) -> set[str]:
        for ob in context.selected_objects:
            if ob.type != "MESH":
                continue
            if ob.mode != "EDIT":
                continue

            self.make_islands(ob.data)
        return {"FINISHED"}

    def make_islands(self, mesh: bpy.types.Mesh) -> None:
        vertex_indices = set(range(0, len(mesh.vertices)))

        while vertex_indices:
            bpy.ops.mesh.select_mode(type="VERT")
            bpy.ops.mesh.select_all(action="DESELECT")

            bpy.ops.object.mode_set(mode="OBJECT")
            for loop in mesh.loops:
                vertex_indices.discard(loop.vertex_index)

            if not vertex_indices:
                break

            unconnected_idx = vertex_indices.pop()
            mesh.vertices[unconnected_idx].select = True

            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_linked()
            bpy.ops.mesh.edge_face_add()


class LASERCUTSVGEXPORT_OT_separate_mesh(bpy.types.Operator):
    bl_idname = "lasercut_svg_export.separate_mesh"
    bl_label = "Separate Mesh into Faces"
    bl_description = "Split up the mesh into an object per face"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        ob = context.edit_object
        in_edit_mode = ob and ob.type == "MESH" and ob.mode == "EDIT"
        return bool(in_edit_mode and bpy.ops.mesh.separate.poll())

    def execute(self, context: bpy.types.Context) -> set[str]:
        mesh = context.edit_object.data
        print("Splitting mesh:")
        while self.split_step(mesh):
            pass
        return {"FINISHED"}

    def split_step(self, mesh: bpy.types.Mesh) -> bool:
        face_indices_per_normal = defaultdict(set)

        # Group faces by their normal.
        for idx, normal in enumerate(mesh.polygon_normals):
            vec = Vector(
                (
                    round(normal.vector.x, 4),
                    round(normal.vector.y, 4),
                    round(normal.vector.z, 4),
                )
            ).freeze()

            face_indices_per_normal[vec].add(idx)

        if len(face_indices_per_normal) < 2:
            # Let's not split off the final group.
            return False

        # Split off the first group. After this, the face indices are all
        # changed anyway, so the entire analysis has to be done from scratch.
        vec, face_indices = face_indices_per_normal.popitem()

        # Select the faces in the group:
        bpy.ops.mesh.select_all(action="DESELECT")
        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.ensure_lookup_table()  # Necessary after the first split.
        for idx in face_indices:
            face = bm.faces[idx]
            face.select = True
        bm.select_flush(True)
        bmesh.update_edit_mesh(mesh)

        bpy.ops.mesh.separate(type="SELECTED")

        # Toggle edit mode back & forth to ensure edit data is up to date.
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        return True


class LASERCUTSVGEXPORT_OT_boolean_cut(bpy.types.Operator):
    bl_idname = "lasercut_svg_export.boolean_cut"
    bl_label = "Add Boolean Cut Modifier"
    bl_description = (
        "Add Boolean modifiers to selected mesh objects to cut out the active object"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if not cls._others(context):
            return False

        ob = context.object
        return bool(context.mode == "OBJECT" and ob and ob.type == "MESH")

    def execute(self, context: bpy.types.Context) -> set[str]:
        target = context.object

        for ob in self._others(context):
            mod = ob.modifiers.new("Bool Cut", "BOOLEAN")
            mod.object = target
            mod.operation = "DIFFERENCE"

            # Move the operator to before any Solidify modifier.
            with context.temp_override(object=ob):
                bpy.ops.object.modifier_move_to_index(
                    modifier=mod.name, index=0)

        return {"FINISHED"}

    @staticmethod
    def _others(context: bpy.types.Context) -> list[bpy.types.Object]:
        ob = context.object
        return [
            other_ob
            for other_ob in context.selected_objects
            if other_ob.type == "MESH" and ob != other_ob
        ]

class LASERCUTSVGEXPORT_OT_mark_faces(bpy.types.Operator):
    bl_idname = "lasercut_svg_export.mark_faces"
    bl_label = "Mark lasercut faces"
    bl_description = "Mark selected faces to be exported to 2D SVG"
    bl_options = {"REGISTER", "UNDO"}
    
    mark: bpy.props.BoolProperty(name="Mark face to export")

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        ob = context.edit_object
        in_edit_mode = ob and ob.type == "MESH" and ob.mode == "EDIT"
        return bool(in_edit_mode and bpy.ops.mesh.separate.poll())

    def execute(self, context: bpy.types.Context) -> set[str]:
        mesh = context.edit_object.data
        
        # Get a BMesh representation
        bm = bmesh.new()   # create an empty BMesh
        bm.from_mesh(mesh) # fill it in from a Mesh

        # XXX ensure taht active int layer is the right one, or select it ?
        lasercut_layer = bm.faces.layers.int.active
        if not lasercut_layer:
            lasercut_layer = bm.faces.layers.int.new("lasercut")
        
        for face in bm.faces:
            # XXX filter only on selected faces
            if self.mark:
                print(f"mark_face on {face}")
                face[lasercut_layer] = 1
            else:
                print(f"unmark_face on {face}")
                face[lasercut_layer] = 0
        
        # Finish up, write the bmesh back to the mesh
        bpy.ops.object.mode_set(mode="OBJECT")
        bm.to_mesh(mesh)
        bm.free()  # free and prevent further access

        # as per https://docs.blender.org/api/current/bmesh.html#edit-mode-tessellation
        mesh.calc_loop_triangles()

        # Toggle edit mode back & forth to ensure edit data is up to date.
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}

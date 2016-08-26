# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from bpy.types import Panel
from bl_ui import properties_data_camera #import CameraButtonsPanel

class CameraButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.camera and (engine in cls.COMPAT_ENGINES)


class THEBOUNTY_PT_lens(CameraButtonsPanel, Panel):
    bl_label = "Lens"
    #povman add
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return context.camera and CameraButtonsPanel.poll(context)
    #end
    
    def draw(self, context):
        layout = self.layout

        cam = context.camera
        # exporter camera subclass
        camera = context.camera.bounty

        layout.prop(cam.bounty, "camera_type", expand=True)

        layout.separator()

        if cam.bounty.camera_type == 'angular':
            layout.prop(cam.bounty, "angular_angle")
            layout.prop(cam.bounty, "max_angle")
            layout.prop(cam.bounty, "mirrored")
            layout.prop(cam.bounty, "circular")

        elif cam.bounty.camera_type == 'orthographic':
            layout.prop(cam, "ortho_scale")

        elif cam.bounty.camera_type in {'perspective', 'architect'}:
            layout.prop(cam, "lens")

            layout.separator()

            layout.label("Depth of Field:")
            layout.prop(cam.bounty, "aperture")
            split = layout.split()
            split.prop(cam, "dof_object", text="")
            col = split.column()
            if cam.dof_object is not None:
                col.enabled = False
            col.prop(cam, "dof_distance", text="Distance")

            layout.prop(cam.bounty, "bokeh_type")
            layout.prop(cam.bounty, "bokeh_bias")
            layout.prop(cam.bounty, "bokeh_rotation")

        layout.separator()
        split = layout.split()
        col = split.column(align=True)
        col.label(text="Shift:")
        col.prop(cam, "shift_x", text="X")
        col.prop(cam, "shift_y", text="Y")

        col = split.column(align=True)
        col.prop(cam.bounty, "use_clipping")
        sub = col.column()
        sub.active = cam.bounty.use_clipping
        sub.prop(cam, "clip_start", text="Start")
        sub.prop(cam, "clip_end", text="End")


class THEBOUNTY_PT_camera(CameraButtonsPanel, Panel):
    bl_label = "Camera"
    #povman add
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return context.camera and CameraButtonsPanel.poll(context)
    #end

    def draw(self, context):
        layout = self.layout

        camera = context.camera

        row = layout.row(align=True)

        row.menu("CAMERA_MT_presets", text=bpy.types.CAMERA_MT_presets.bl_label)
        row.operator("camera.preset_add", text="", icon="ZOOMIN")
        row.operator("camera.preset_add", text="", icon="ZOOMOUT").remove_active = True

        layout.label(text="Sensor:")

        split = layout.split()

        col = split.column(align=True)
        if camera.sensor_fit == 'AUTO':
            col.prop(camera, "sensor_width", text="Size")
        else:
            col.prop(camera, "sensor_width", text="Width")
            col.prop(camera, "sensor_height", text="Height")

        col = split.column(align=True)
        col.prop(camera, "sensor_fit", text="")


class THEBOUNTY_PT_camera_display(CameraButtonsPanel, Panel):
    bl_label = "Display"
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return context.camera and CameraButtonsPanel.poll(context)
    
    def draw(self, context):
        properties_data_camera.DATA_PT_camera_display.draw(self, context)


if __name__ == "__main__":  # only for live edit.
    #import bpy
    bpy.utils.register_module(__name__)

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
from ..ot import bounty_presets
from . prop_render import RenderButtonsPanel
from bpy.types import Panel, Menu

RenderButtonsPanel.COMPAT_ENGINES = {'THEBOUNTY'}

   
class THEBOUNTY_MT_render_presets(Menu):
    bl_label = "Settings Presets"
    preset_subdir = "thebounty/render"
    preset_operator = "script.execute_preset"
    COMPAT_ENGINES = {'THEBOUNTY'}
    draw = Menu.draw_preset

# povman: test for next panel distribution
class THEBOUNTY_PT_pass_settings(RenderButtonsPanel, Panel):
    bl_label = "Render Passes"

    def draw(self, context):
        layout = self.layout
        scene = context.scene.bounty
        #render = scene.render
        #
        split = layout.split()
        col = split.column()
        col.prop(scene, "gs_transp_shad", toggle=True)
        col.prop(scene, "gs_clay_render", toggle=True)
        col.prop(scene, "gs_z_channel", toggle=True)
        col = split.column()
        sub = col.column()
        sub.enabled = scene.gs_transp_shad
        sub.prop(scene, "gs_shadow_depth")
        sub = col.column()
        sub.enabled = scene.gs_clay_render
        sub.prop(scene, "gs_clay_col", text="")

class THEBOUNTY_PT_general_settings(RenderButtonsPanel, Panel):
    bl_label = "General Settings"

    def draw(self, context):
        layout = self.layout
        render = context.scene.render
        scene = context.scene.bounty        

        row = layout.row(align=True)
        row.menu("THEBOUNTY_MT_render_presets", text=bpy.types.THEBOUNTY_MT_render_presets.bl_label)
        row.operator("bounty.render_preset_add", text="", icon='ZOOMIN')
        row.operator("bounty.render_preset_add", text="", icon='ZOOMOUT').remove_active = True

        layout.separator()
        split = layout.split()
        col = split.column()
        col.prop(scene, "gs_type_render", text="")
        sub = col.column()
        sub.enabled = scene.gs_type_render == "into_blender"
        sub.prop(scene, "gs_tile_order", text="")

        col = split.column()
        sub = col.column()
        sub.enabled = scene.gs_transp_shad
        sub = col.column()
        #
        threadMode ="Threads (Auto)" if scene.gs_threads == 0 else "Threads used"
        col.prop(scene, "gs_threads", text= threadMode)
        sub = col.column()
        sub.enabled = scene.gs_type_render == "into_blender"
        sub.prop(scene, "gs_tile_size")

        split = layout.split()
        col = split.column()
        col.prop(scene, "gs_clamp_rgb", toggle=True)

        col = split.column()
        col.prop(render, "use_instances", text="Use instances", toggle=True)
        
        split = layout.split(percentage=0.5)
        col = split.column()
        col.prop(scene, "bg_transp", toggle=True)
        col = split.column()
        sub = col.column()
        sub.enabled = scene.bg_transp
        sub.prop(scene, "bg_transp_refract", toggle=True)
        
        split = layout.split(percentage=0.58)
        col = layout.row()
        col.prop(scene, "gs_draw_params", expand=True)
        col.prop(scene, "gs_verbosity_level", text="")
        
        col = layout.column()
        col.enabled = scene.gs_draw_params
        col.prop(scene, "gs_custom_string", text="")        


if __name__ == "__main__":  # only for live edit.
    #import bpy
    bpy.utils.register_module(__name__)

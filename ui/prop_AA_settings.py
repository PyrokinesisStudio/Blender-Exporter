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

from . prop_render import RenderButtonsPanel
from bpy.types import Panel

RenderButtonsPanel.COMPAT_ENGINES = {'THEBOUNTY'}


class TheBounty_PT_AA_settings(RenderButtonsPanel, Panel):
    bl_label = "Anti-Aliasing"

    def draw(self, context):

        scene = context.scene.bounty
        layout = self.layout

        split = layout.split()
        col = split.column()
        
        col.prop(scene, "AA_filter_type", text="")
        col.prop(scene, "AA_min_samples")
        col.prop(scene, "AA_pixelwidth")
        # 
        col = split.column()
        spp = col.column()
        sub = col.column()
        spp.enabled = False
        if scene.intg_light_method != "SPPM":
            sub.enabled = scene.AA_passes > 1
            spp.enabled = True
        #
        spp.prop(scene, "AA_passes")
        sub.prop(scene, "AA_inc_samples")
        sub.prop(scene, "AA_threshold")
        #
        sub=layout.row()
        sub.enabled = scene.AA_passes > 1
        sub.prop(scene, "gs_show_sam_pix", toggle=True)
        
        
if __name__ == "__main__":  # only for live edit.
    import bpy
    bpy.utils.register_module(__name__)

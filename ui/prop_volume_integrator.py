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
from . prop_world import TheBountyWorldButtonsPanel

TheBountyWorldButtonsPanel.COMPAT_ENGINES = {'THEBOUNTY'}


class TheBounty_PT_vol_integrator(TheBountyWorldButtonsPanel, Panel):
    bl_label = "Volume Integrator"
    
    @classmethod
    def poll(cls, context):
        return context.world and TheBountyWorldButtonsPanel.poll(context)

    def draw(self, context):
        layout = self.layout
        world = context.world.bounty

        layout.prop(world, "v_int_type")
        layout.separator()

        if world.v_int_type == "SingleScatterIntegrator":
            layout.prop(world, "v_int_step_size")
            row = layout.row()
            row.prop(world, "v_int_adaptive", toggle=True)
            row.prop(world, "v_int_optimize", toggle=True)
            sub = layout.row()
            sub.enabled = world.v_int_optimize
            sub.prop(world, "v_int_attgridres")

        if world.v_int_type == "SkyIntegrator":
            layout.prop(world, "v_int_step_size")
            layout.prop(world, "v_int_dsturbidity")
            split = layout.split()
            split.prop(world, "v_int_scale")
            split.prop(world, "v_int_alpha")


if __name__ == "__main__":  # only for live edit.
    import bpy
    bpy.utils.register_module(__name__)

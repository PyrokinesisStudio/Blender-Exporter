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

class TheBountyStrandPanel( bpy.types.Panel):
    bl_label = "TheBounty Strand Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "particle"
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll( cls, context):
        engine = context.scene.render.engine
        if engine not in cls.COMPAT_ENGINES:
            return False
        psys = context.particle_system
        return (psys and psys.settings.type == 'HAIR')

    def draw_header( self, context):
        pass

    def draw( self, context):
        layout = self.layout
        bounty = context.particle_system.settings.bounty
        
        layout.prop( bounty, "strand_shape", text="Primitive")
        split = layout.split()
        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Thickness:")
        sub.prop( bounty, "root_size")
        sub.prop( bounty, "tip_size")
        sh = col.column()
        sh.enabled = (bounty.root_size != bounty.tip_size)
        sh.prop( bounty, "shape")
        #
        col.prop( bounty, "bake_hair")      
        
        col = split.column()        
        col.label(text="")
        cc = col.column()
        cc.enabled = bounty.strand_shape == "cylinder"
        cc.prop( bounty, "scaling")
        cc.prop(bounty, "thick")
        cb = col.column()
        cb.enabled = (bounty.thick and bounty.strand_shape == "cylinder")
        cb.prop( bounty, "resolution")
        
        col.prop( bounty, "close_tip")  
        
        #layout.prop( bounty, "export_color")

if __name__ == "__main__":  # only for live edit.
    import bpy
    bpy.utils.register_module(__name__)

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

from bpy.types import Panel


class TheBountyGeometryTypes(Panel):
    bl_label = "TheBounty Special Geometry"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(cls, context):

        engine = context.scene.render.engine
        return (context.object.type == "MESH" and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        layout = self.layout
        ob = context.object.bounty
        
        # geometry types..
        layout.prop(ob,"geometry_type", text="", toggle=True)
        
        if ob.geometry_type == "mesh_light":

            col = layout.column(align=True)
            col.prop(ob, "ml_color")
            col.prop(ob, "ml_power")
            col.prop(ob, "ml_samples")
            col.prop(ob, "ml_double_sided")
    
        elif ob.geometry_type == "portal_light":
    
            layout.prop(ob, "bgp_power")
            layout.prop(ob, "bgp_samples")
            split = layout.split()
            split.prop(ob, "bgp_with_diffuse")
            split.prop(ob, "bgp_with_caustic")
            layout.prop(ob, "bgp_photon_only")
    
        elif ob.geometry_type == "volume_region":
    
            layout.separator()
            layout.prop(ob, "vol_region")
            layout.separator()
            col = layout.column(align=True)
            col.prop(ob, "vol_absorp", text="Absorption")
            col.prop(ob, "vol_scatter", text="Scatter")
    
            if ob.vol_region == "ExpDensity Volume":
                col = layout.column(align=True)
                col.prop(ob, "vol_height")
                col.prop(ob, "vol_steepness")
    
            if ob.vol_region == "Noise Volume":
                col = layout.column(align=True)
                col.prop(ob, "vol_sharpness")
                col.prop(ob, "vol_cover")
                col.prop(ob, "vol_density")


if __name__ == "__main__":  # only for live edit.
    import bpy
    bpy.utils.register_module(__name__)

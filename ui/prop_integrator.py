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

# sss mat check
def haveSSS():
    for mat in bpy.data.materials:
        if mat.bounty.mat_type == "translucent":
            return True
    return False


from . prop_render import RenderButtonsPanel
RenderButtonsPanel.COMPAT_ENGINES = {'THEBOUNTY'}

class THEBOUNTY_PT_integrator(RenderButtonsPanel, Panel):
    bl_label = "Lighting Integrator Method"

    def draw(self, context):
        layout = self.layout
        scene = context.scene.bounty

        #----------------------------------------------------------------------------------
        # povman: sync integrator names in core 'registerFactory' functions
        # directlighting, photonmapping, pathtracing, DebugIntegrator, bidirectional, SPPM
        #----------------------------------------------------------------------------------
        integrator = scene.intg_light_method
        layout.prop(scene, "intg_light_method", text="")
        # for recursive raytracing..
        row = layout.row()
        row.enabled = integrator not in {"bidirectional"}
        row.prop(scene, "gs_ray_depth")
        #
        if integrator == "directlighting":
            row = layout.row()
            col = row.column(align=True)
            col.prop(scene, "intg_use_caustics", toggle=True)
            if scene.intg_use_caustics:
                col.prop(scene, "intg_caustic_depth")
                col.prop(scene, "intg_photons")
                col.prop(scene, "intg_caustic_radius")
                col.prop(scene, "intg_caustic_mix")

            col = row.column(align=True)
            col.prop(scene, "intg_use_AO", toggle=True)
            if scene.intg_use_AO:
                col.prop(scene, "intg_AO_color")
                col.prop(scene, "intg_AO_samples")
                col.prop(scene, "intg_AO_distance")

        elif integrator == "photonmapping":
            row = layout.row()

            row.prop(scene, "intg_bounces", text="Photons bounces depth")

            row = layout.row()
            col = row.column(align=True)
            col.label(" Diffuse Photons:", icon='MOD_PHYSICS')
            col.prop(scene, "intg_photons")
            col.prop(scene, "intg_diffuse_radius")
            col.prop(scene, "intg_search")

            col = row.column(align=True)
            col.label(" Caustic Photons:", icon='MOD_PARTICLES')
            col.prop(scene, "intg_cPhotons")
            col.prop(scene, "intg_caustic_radius")
            col.prop(scene, "intg_caustic_mix")

            row = layout.row()
            row.prop(scene, "intg_final_gather", toggle=True, icon='FORCE_FORCE')
            
            if scene.intg_final_gather:
                # Show UI options for Final Gathering.
                col = layout.row()
                col.prop(scene, "intg_fg_bounces")
                col.prop(scene, "intg_fg_samples")
                col = layout.row()
                col.prop(scene, "intg_show_map", toggle=True)
                
        elif integrator == "pathtracing":
            col = layout.row()
            col.prop(scene, "intg_caustic_method")

            if scene.intg_caustic_method in {"both", "photon"}:
                col = layout.row(align=True)
                col.prop(scene, "intg_photons", text="Photons")
                col.prop(scene, "intg_caustic_mix", text="Caus. Mix")
                col = layout.row(align=True)
                col.prop(scene, "intg_caustic_depth", text="Caus. Depth")
                col.prop(scene, "intg_caustic_radius", text="Caus. Radius")
            #
            col = layout.row(align=True)
            col.prop(scene, "intg_path_samples")
            col.prop(scene, "intg_bounces")
            col = layout.row()
            col.prop(scene, "intg_no_recursion")       

        elif integrator == "DebugIntegrator":
            layout.row().prop(scene, "intg_debug_type")
            layout.row().prop(scene, "intg_show_perturbed_normals")
            
        elif integrator == "bidirectional":
            #layout.row().prop(scene, "intg_do_lightImage")
            layout.label("Use a high number of AA samples to reduce render noise")

        elif integrator == "SPPM":
            col = layout.column(align=True)
            col.prop(scene, "intg_photons", text="Photons per pass")
            col.prop(scene, "intg_pass_num")
            col.prop(scene, "intg_bounces", text="Photon bounces depth")
            col.prop(scene, "intg_search")
            col = layout.column(align=True)
            col.prop(scene, "intg_pm_ire", toggle=True)
            if not scene.intg_pm_ire:
                col.prop(scene, "intg_times")
            else:
                col.prop(scene, "intg_accurate_radius")
        
        #----------------------------
        # SubSurface integrator
        #----------------------------
        if integrator in {'directlighting', 'photonmapping', 'pathtracing'} and haveSSS():
            col = layout.column(align=True)
            col.prop(scene, "intg_useSSS", toggle=True)
            if scene.intg_useSSS:
                col.prop(scene, "intg_sssPhotons")
                col.prop(scene, "intg_sssDepth")
                col.prop(scene, "intg_singleScatterSamples")
                col.prop(scene, "intg_sssScale")


if __name__ == "__main__":  # only for live edit.
    #import bpy
    bpy.utils.register_module(__name__)

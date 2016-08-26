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

switchDebugType = {
    'N': 1,
    'dPdU': 2,
    'dPdV': 3,
    'NU': 4,
    'NV': 5,
    'dSdU': 6,
    'dSdV': 7,
}
def haveLights():
    scene = bpy.context.scene
    world = scene.world.bounty
    
    # expand function for include light created from 'add sun' or 'add skylight' in sunsky or sunsky2 mode    
    if world.bg_type in {'sunsky','darksky'} and world.bg_add_sun or world.bg_background_light:
        return True
    # use light created when use ibl is 'ON'
    if world.bg_type in {'constant','textureback', 'gradientback'} and world.bg_use_ibl:
        return True

    # check for lamp, meshlight or portal light object in scene
    for sceneObj in scene.objects:
        if not sceneObj.hide_render and sceneObj.is_visible(scene):
            if sceneObj.type == "LAMP" or sceneObj.bounty.geometry_type in {'mesh_light', 'portal_light'}:
                return True
                #break
    #
    return False

# sss material check
def haveSSS():
    #
    for mat in bpy.data.materials:
        if mat.bounty.mat_type == "translucent":
            return True
    return False

class exportIntegrator:
    def __init__(self, interface, preview):
        self.yi = interface
        self.preview = preview

    def exportIntegrator(self, scene):
        yi = self.yi

        yi.paramsClearAll()

        yi.paramsSetBool("bg_transp", scene.bg_transp)
        transp_refract = False
        if scene.bg_transp:
            transp_refract = scene.bg_transp_refract
        #
        yi.paramsSetBool("bg_transp_refract", transp_refract)

        yi.paramsSetInt("raydepth", scene.gs_ray_depth)
        yi.paramsSetInt("shadowDepth", scene.gs_shadow_depth)
        yi.paramsSetBool("transpShad", scene.gs_transp_shad)

        lightIntegrator = scene.intg_light_method
        yi.printInfo("Exporting Integrator: {0}".format(lightIntegrator))

        if lightIntegrator == "directlighting":
            yi.paramsSetBool("caustics", scene.intg_use_caustics)

            if scene.intg_use_caustics:
                yi.paramsSetInt("photons", scene.intg_photons)
                yi.paramsSetInt("caustic_mix", scene.intg_caustic_mix)
                yi.paramsSetInt("caustic_depth", scene.intg_caustic_depth)
                yi.paramsSetFloat("caustic_radius", scene.intg_caustic_radius)

            yi.paramsSetBool("do_AO", scene.intg_use_AO)
                
            if scene.intg_use_AO:
                yi.paramsSetInt("AO_samples", scene.intg_AO_samples)
                yi.paramsSetFloat("AO_distance", scene.intg_AO_distance)
                c = scene.intg_AO_color
                yi.paramsSetColor("AO_color", c[0], c[1], c[2])

        elif lightIntegrator == "photonmapping":
            yi.paramsSetInt("photons", scene.intg_photons)
            yi.paramsSetInt("cPhotons", scene.intg_cPhotons)
            yi.paramsSetFloat("diffuseRadius", scene.intg_diffuse_radius)
            yi.paramsSetFloat("causticRadius", scene.intg_caustic_radius)
            yi.paramsSetInt("bounces", scene.intg_bounces)
            yi.paramsSetInt("search", scene.intg_search)
            yi.paramsSetInt("caustic_mix", scene.intg_caustic_mix)
            yi.paramsSetBool("finalGather", scene.intg_final_gather)
            #
            if scene.intg_final_gather:
                yi.paramsSetInt("fg_bounces", scene.intg_fg_bounces)
                yi.paramsSetInt("fg_samples", scene.intg_fg_samples)
                yi.paramsSetBool("show_map", scene.intg_show_map)

        elif lightIntegrator == "pathtracing":
            yi.paramsSetInt("path_samples", scene.intg_path_samples)
            yi.paramsSetInt("bounces", scene.intg_bounces)
            yi.paramsSetBool("no_recursive", scene.intg_no_recursion)

            causticType = scene.intg_caustic_method
            yi.paramsSetString("caustic_type", causticType)
            
            if causticType in {'photon','both'}:
                yi.paramsSetInt("photons", scene.intg_photons)
                yi.paramsSetInt("caustic_mix", scene.intg_caustic_mix)
                yi.paramsSetInt("caustic_depth", scene.intg_caustic_depth)
                yi.paramsSetFloat("caustic_radius", scene.intg_caustic_radius)

        elif lightIntegrator == "bidirectional":
            yi.paramsSetBool("do_LightImage", scene.intg_do_lightImage)
            if not haveLights():
                yi.printWarning('Bidirectional Integrator need a lights on scene for work')
                return False

        elif lightIntegrator == "DebugIntegrator":
            #
            debugTypeStr = scene.intg_debug_type            
            yi.paramsSetInt("debugType", switchDebugType.get(debugTypeStr, 1))
            yi.paramsSetBool("showPN", scene.intg_show_perturbed_normals)
        #----------------------------------
        # SPPM integrator
        #----------------------------------
        elif lightIntegrator == "SPPM":
            yi.paramsSetInt("photons", scene.intg_photons)
            yi.paramsSetFloat("photonRadius", scene.intg_accurate_radius)
            yi.paramsSetInt("searchNum", scene.intg_search)
            yi.paramsSetInt("bounces", scene.intg_bounces)
            yi.paramsSetInt("passNums", scene.intg_pass_num)
            yi.paramsSetBool("pmIRE", scene.intg_pm_ire)
            yi.paramsSetFloat("times", scene.intg_times)             
        
        #----------------------------------
        # Sub-Surface Scattering integrator
        #----------------------------------
        if lightIntegrator in {'directlighting', 'photonmapping', 'pathtracing'} and haveSSS():
            yi.paramsSetBool("useSSS", scene.intg_useSSS)
            if scene.intg_useSSS:
                yi.paramsSetInt("sssPhotons", scene.intg_sssPhotons)
                yi.paramsSetInt("sssDepth", scene.intg_sssDepth)
                yi.paramsSetInt("singleScatterSamples", scene.intg_singleScatterSamples)
                yi.paramsSetFloat("sssScale", scene.intg_sssScale)
        
        yi.paramsSetString("type", lightIntegrator)
        yi.createIntegrator("default")
        return True

    def exportVolumeIntegrator(self, scene):
        yi = self.yi
        yi.paramsClearAll()

        scn_world = scene.world        

        if scn_world:
            # use bounty sub-class
            world = scene.world.bounty
            yi.printInfo("Exporting Volume Integrator: {0}".format(world.v_int_type))

            if world.v_int_type == 'SingleScatterIntegrator':
                # Single Scatter mode
                yi.paramsSetFloat("stepSize", world.v_int_step_size)
                yi.paramsSetBool("adaptive", world.v_int_adaptive)
                yi.paramsSetBool("optimize", world.v_int_optimize)

            elif world.v_int_type == 'SkyIntegrator':
                yi.paramsSetFloat("turbidity", world.v_int_dsturbidity)
                yi.paramsSetFloat("stepSize", world.v_int_step_size)
                yi.paramsSetFloat("alpha", world.v_int_alpha)
                yi.paramsSetFloat("sigma_t", world.v_int_scale)

            #
            yi.paramsSetString("type", world.v_int_type)
        #
        else:
            yi.paramsSetString("type", "none")

        yi.createIntegrator("volintegr")
        return True

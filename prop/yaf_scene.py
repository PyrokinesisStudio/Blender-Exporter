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
#from sys import platform
from bpy.props import (IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       BoolProperty,
                       PointerProperty,
                       StringProperty)
#
enum_render_output_mode =(
    ('file', "Render to Image file", "Render the Scene and write it to an Image File when finished"),
    ('into_blender', "Render Into Blender", "Render the Scene into Blender Renderbuffer"),
    ('xml', "Write to XML file", "Export scene to a XML File"),
)

enum_render_output_format =(
    ('PNG', " PNG (Portable Network Graphics)", ""),
    ('TARGA', " TGA (Truevision TARGA)", ""),
    ('JPEG', " JPEG (Joint Photographic Experts Group)", ""),
    ('TIFF', " TIFF (Tag Image File Format)", ""),
    ('OPEN_EXR', " EXR (IL&M OpenEXR)", ""),
    ('HDR', " HDR (Radiance RGBE)", ""),
)

enum_lighting_integrator_method =(
    ('directlighting', "Direct Lighting", ""),
    ('photonmapping', "Photon Mapping", ""),
    ('pathtracing', "Pathtracing", ""),
    ('DebugIntegrator', "Debug Integrator", ""),
    ('bidirectional', "Bidirectional PathTracing (WIP)", ""),
    ('SPPM', "Stochastic Progressive Photon Mapping", ""),
)

enum_caustic_method =(
    ('none', "None", ""),
    ('path', "Path", ""),
    ('both', "Path + Photon", ""),
    ('photon', "Photon", ""),
)

enum_debug_integrator_type =(
    ("N", "N", ""),
    ("dPdU", "dPdU", ""),
    ("dPdV", "dPdV", ""),
    ("NU", "NU", ""),
    ("NV", "NV", ""),
    ("dSdU", "dSdU", ""),
    ("dSdV", "dSdV", ""),
)

enum_filter_type =(
    ('box',      "AA Filter Box",      "Anti-Aliasing filter type Box"),
    ('mitchell', "AA Filter Mitchell", "Anti-Aliasing filter type Michel-Netravali"),
    ('gauss',    "AA Filter Gauss",    "Anti-Aliasing filter type Gaussian"),
    ('lanczos',  "AA Filter Lanczos",  "Anti-Aliasing filter type Lanczos"),
)

enum_tile_order = (
    ('linear', "Linear Tiles", "Linear buckets ( by a set size) from to  top-left image to bottom-right"),
    ('random', "Random Tiles", "Random buckets by arbitray order"),
)

enum_verbosity_level = (
    ('info', "Console Info", "Show all general info messages on console"),
    ('warning', "Console Warning", "Show only warning messages on console"),
    ('error', "Console Error", "Show only error messages on console"),
    ('mute', "Console Mute", "Mute all messages on console"),
)

# set fileformat for image saving on same format as in the exporter, both have default PNG
# TODO: need review
def call_update_fileformat(self, context):
    render = context.scene.render
    scene = context.scene.bounty
    
    if scene.img_output is not render.image_settings.file_format:
        render.image_settings.file_format = scene.img_output

class TheBountySceneSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        # add subclasse to scene class
        bpy.types.Scene.bounty = PointerProperty(
            name="TheBounty Scene settings",
            description="",
            type=cls,
        )
        #-----------------------------
        # General settings properties 
        #-----------------------------
        cls.gs_ray_depth = IntProperty(
            name="Recursive Raytracing depth",
            description="Maximum depth for recursive raytracing",
            min=0, max=64, default=2
        )    
        cls.gs_shadow_depth = IntProperty(
            name="Shadow depth",
            description="Max. depth for transparent shadows calculation (if enabled)",
            min=0, max=64, default=2
        )    
        cls.gs_threads = IntProperty(
            name="Threads",
            description="Number of threads to use, try '0' for use all threads",
            min=0, default=0
        )        
        cls.gs_gamma = FloatProperty(
            name="Gamma",
            description="Gamma correction applied to final output,"
                        " inverse correction of textures and colors is performed",
            min=1.0, max=5.0, 
            default= 2.2
        )    
        cls.gs_gamma_input = FloatProperty(
            name="Gamma input",
            description="Gamma correction applied to input images",
            min=0, max=5, default=2.2 # 1.0 for linear mode ??
        )
        cls.sc_apply_gammaInput = BoolProperty(
            name="Use Gamma",
            description="Apply gamma correction to image input file",
            default=True
        )    
        cls.gs_tile_size = IntProperty(
            name="Tile size",
            description="Size of the render buckets (tiles)",
            min=4, max=1024, default=32
        )    
        cls.gs_tile_order = EnumProperty(
            name="Tile order",
            description="Selects tiles order render type",
            items=enum_tile_order,
            default='random'
        )# TODO: Review auto threads, atm seems unused   
        cls.gs_auto_threads = BoolProperty(
            name="Auto threads",
            description="Activate thread number auto detection",
            default=True
        )    
        cls.gs_clay_render = BoolProperty(
            name="Render clay",
            description="Override all materials with a white diffuse material",
            default=False
        )    
        cls.gs_clay_col = FloatVectorProperty(
            name="Clay color",
            description="Color of clay render material",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(0.8, 0.8, 0.8)
        )    
        cls.gs_mask_render = BoolProperty(
            name="Render mask",
            description="Renders an object mask pass with different colors",
            default=False
        )    
        cls.gs_draw_params = BoolProperty(
            name="Draw parameters",
            description="Draw params and custom string on image",
            default=False
        )    
        cls.bg_transp = BoolProperty(
            name="Transp.background",
            description="Render the background as transparent",
            default=False
        )    
        cls.bg_transp_refract = BoolProperty(
            name="Materials transp. refraction",
            description="Materials refract the background as transparent",
            default=False
        )    
        cls.gs_custom_string = StringProperty(
            name="Custom string",
            description="Custom string will be added to the info bar, use it for CPU, RAM etc",
            default=""
        )# TODO: Atm, is unused. Review!!    
        cls.gs_premult = BoolProperty(
            name="Premultiply",
            description="Premultipy Alpha channel for renders with transparent background",
            default=True
        )    
        cls.gs_transp_shad = BoolProperty(
            name="Transparent shadows",
            description="Compute transparent shadows",
            default=False
        )    
        cls.gs_clamp_rgb = BoolProperty(
            name="Clamp RGB",
            description="Reduce the color's brightness to a low dynamic range",
            default=False
        )    
        cls.gs_z_channel = BoolProperty(
            name="Render Z-depth map",
            description="Render depth map (Z-Buffer)",
            default=False
        )    
        cls.gs_verbose = BoolProperty(
            name="Log info to console",
            description="Print engine log messages in console window",
            default=True
        )
        cls.gs_verbosity_level = EnumProperty(
            name="Verbosity level",
            description="Choose log messages level in console",
            items=enum_verbosity_level,
            default='info'
        )    
        cls.gs_type_render = EnumProperty(
            name="Render",
            description="Choose the render output method",
            items=enum_render_output_mode,
            default='into_blender'
        )    
        cls.img_output = EnumProperty(
            name="Image File Type",
            description="Image will be saved in this file format",
            items=enum_render_output_format,
            default='PNG', 
            update=call_update_fileformat
        )    
        #--------------------------
        # Integrator properties 
        #--------------------------
        cls.intg_light_method = EnumProperty(
            name="Lighting Method",
            items=enum_lighting_integrator_method,
            default='directlighting'
        )    
        cls.intg_use_caustics = BoolProperty(
            name="Caustic Photons",
            description="Enable photon map for caustics only",
            default=False
        )    
        cls.intg_photons = IntProperty(
            name="Photons",
            description="Number of photons to be shot",
            min=1, max=100000000,
            default=500000
        )    
        cls.intg_caustic_mix = IntProperty(
            name="Caustic Mix",
            description="Max. number of photons to mix (blur)",
            min=1, max=10000,
            default=100
        )    
        cls.intg_caustic_depth = IntProperty(
            name="Caustic Depth",
            description="Max. number of scatter events for photons",
            min=0, max=50,
            default=10
        )    
        cls.intg_caustic_radius = FloatProperty(
            name="Caustic Radius",
            description="Max. radius to search for photons",
            min=0.0001, max=100.0,
            default=1.0
        )    
        cls.intg_use_AO = BoolProperty(
            name="Ambient Occlusion",
            description="Enable ambient occlusion",
            default=False
        )    
        cls.intg_AO_samples = IntProperty(
            name="Samples",
            description="Number of samples for ambient occlusion",
            min=1, max=1000,
            default=32
        )    
        cls.intg_AO_distance = FloatProperty(
            name="Distance",
            description=("Max. occlusion distance, Surfaces further away do not occlude ambient light"),
            min=0.0, max=10000.0,
            default=1.0
        )    
        cls.intg_AO_color = FloatVectorProperty(
            name="AO Color",
            description="Color Settings", subtype='COLOR',
            min=0.0, max=1.0,
            default=(0.9, 0.9, 0.9)
        )    
        cls.intg_bounces = IntProperty(
            name="Depth",
            description="",
            min=1,
            default=4
        )    
        cls.intg_diffuse_radius = FloatProperty(
            name="Search radius",
            description="Radius to search for diffuse photons",
            min=0.001,
            default=1.0
        )    
        cls.intg_cPhotons = IntProperty(
            name="Count",
            description="Number of caustic photons to be shot",
            min=2, default=500000
        )    
        cls.intg_search = IntProperty(
            name="Search count",
            description="Maximum number of diffuse photons to be filtered",
            min=1, max=10000,
            default=100
        )    
        cls.intg_final_gather = BoolProperty(
            name="Final Gather",
            description="Use final gathering (recommended)",
            default=True
        )    
        cls.intg_fg_bounces = IntProperty(
            name="Bounces",
            description="Allow gather rays to extend to paths of this length",
            min=1, max=20,
            default=3
        )    
        cls.intg_fg_samples = IntProperty(
            name="Samples",
            description="Number of samples for final gathering",
            min=1,
            default=16
        )    
        cls.intg_show_map = BoolProperty(
            name="Show radiance map",
            description="Show radiance map, useful to calibrate the photon map (disables final gathering step)",
            default=False
        )    
        cls.intg_caustic_method = EnumProperty(
            name="Caustic Method",
            items=enum_caustic_method,
            description="Choose caustic rendering method",
            default='none'
        )        
        cls.intg_path_samples = IntProperty(
            name="Path Samples",
            description="Number of path samples per pixel sample",
            min=1,
            default=32
        )    
        cls.intg_no_recursion = BoolProperty(
            name="No Recursion",
            description="No recursive raytracing, only pure path tracing",
            default=False
        )
        #------------------------------
        # SSS settings
        #------------------------------
        cls.intg_useSSS = BoolProperty(
            name="SubSurface Scattering Integrator",
            description="Enable photonmapping for SSS materials",
            default=False
        )    
        cls.intg_sssPhotons = IntProperty(
            name="Amount of SSS Photons Search",
            description="Amount of SSS photons search for unit (10000 x 1 BU)",
            min=1, max=10000000,
            default=100000
        )    
        cls.intg_sssDepth = IntProperty(
            name="SSS Depth",
            description="Max. number of photon scattering events",
            min=1, max=64,
            default=5
        )    
        cls.intg_singleScatterSamples = IntProperty(
            name="Single Scattering Samples",
            description="Number of samples for single scattering estimation",
            min=0, max=256,
            default=32
        )    
        cls.intg_sssScale = FloatProperty(
            name="Scale",
            description="Scale factor that helps fixing the unit scale, in case 1 blender is not equal to 1 meter",
            min=0.0001, max=1000.0,
            default=10.0
        )
        cls.intg_debug_type = EnumProperty(
            name="Debug type",
            items=enum_debug_integrator_type,
            default="N"
        )    
        cls.intg_show_perturbed_normals = BoolProperty(
            name="Show perturbed normals",
            description="Show the normals perturbed by bump and normal maps",
            default=False
        )
        #-------------------------
        # SPPM properties
        #-------------------------    
        cls.intg_pm_ire = BoolProperty(
            name="PhotonMap Initial Radius Estimate (IRE)",
            description="Automatic Initial Radius Estimate for PhotonMap",
            default=False
        )    
        cls.intg_pass_num = IntProperty(
            name="Render Passes",
            description= "Progressive rendering passes",
            min=1,
            default=100
        )    
        cls.intg_times = FloatProperty(
            name="Initial Radius factor",
            min=0.0,
            description= "Size of the initial radius for photon map (when IRE is OFF)",
            default=1.0
        )    
        cls.intg_photon_radius = FloatProperty(
            name="Search radius",
            min=0.0,
            default=1.0
        )        
        cls.intg_accurate_radius = FloatProperty(
            name="Accurate caustic radius",
            description="Accurate radius for search caustic photons",
            min=0.0,
            default=1.0
        )
        # Bidirectional test
        cls.intg_do_lightImage = BoolProperty(
            name="Do light image",
            description="Enable do light image for bidir",
            default=False
        )        
        #--------------------------
        # Anti-aliasing properties
        #--------------------------
        cls.AA_min_samples = IntProperty(
            name="Samples",
            description="Number of samples for first AA pass",
            min=1,
            default=1
        )    
        cls.AA_inc_samples = IntProperty(
            name="Additional Samples",
            description="Number of samples for additional AA passes",
            min=1,
            default=1
        )    
        cls.AA_passes = IntProperty(
            name="Passes",
            description=("Number of anti-aliasing passes, Adaptive sampling (passes > 1) uses different pattern"),
            min=1,
            default=1
        )    
        cls.AA_threshold = FloatProperty(
            name="Threshold",
            description="Color threshold for additional AA samples in next pass",
            min=0.0, max=1.0, precision=4,
            default=0.05
        )    
        cls.AA_pixelwidth = FloatProperty(
            name="Pixelwidth",
            description="AA filter size",
            min=1.0, max=20.0, precision=3,
            default=1.5
        )    
        cls.AA_filter_type = EnumProperty(
            name="Filter",
            description="Antialising filter type",
            items=enum_filter_type,
            default="gauss"
        )
        cls.gs_show_sam_pix = BoolProperty(
            name="Show sampled pixels",
            description="Masks pixels marked for resampling during adaptive passes",
            default=True
        )    
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.bounty
        
def register():
    bpy.utils.register_class(TheBountySceneSettings)
    
def unregister():
    bpy.utils.unregister_class(TheBountySceneSettings)

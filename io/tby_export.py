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
import os
import threading
import time
import yafrayinterface
from .. import PLUGIN_PATH
from .tby_object import exportObject
from .tby_light  import exportLight
from .tby_world  import exportWorld
from .tby_integrator import exportIntegrator
from . import tby_scene
from .tby_texture import exportTexture
from .tby_material import TheBountyMaterialWrite
from bpy import context

switchFileType = {
    'PNG': 'png',
    'TARGA': 'tga',
    'TIFF': 'tif',
    'JPEG': 'jpg',
    'HDR': 'hdr',
    'OPEN_EXR': 'exr',
    'XML': 'xml',
}

class TheBountyRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'THEBOUNTY'
    bl_use_preview = True
    bl_label = "TheBounty Render"
    prog = 0.0
    tag = ""
    #useViewToRender = False
    #viewMatrix = None
    sceneMat = []
    
    #--------------------------------
    # set console  verbosity levels
    #--------------------------------
    def verbositylevel(self, level):
        if level == 'info':
            self.yi.setVerbosityInfo()
        elif level == 'error':
            self.yi.setVerbosityError()
        elif level == 'warning':
            self.yi.setVerbosityWarning()
        else:
            self.yi.setVerbosityMute()
    
    ##-----------------------------------------------------     

    def setInterface(self, yi):
        self.materialMap = {}
        self.exportedMaterials = set()
        self.yi = yi
        # setup specific values for render preview mode
        if self.is_preview:
            self.yi.setVerbosityWarning()
            #to correct alpha problems in preview roughglass
            self.scene.bounty.bg_transp = False
            self.scene.bounty.bg_transp_refract = False
        else:
            #
            self.verbositylevel(self.scene.bounty.gs_verbosity_level)
        
        # export go.. load plugins
        self.yi.loadPlugins(PLUGIN_PATH)
                
        # process geometry
        self.geometry = exportObject(self.yi, self.materialMap, self.is_preview)
             
        # process lights
        self.lights = exportLight(self.yi, self.is_preview)
              
        # process environment world
        self.environment = exportWorld(self.yi)
              
        # process lighting integrators..
        self.lightIntegrator = exportIntegrator(self.yi, self.is_preview)
              
        # textures before materials
        self.textures = exportTexture(self.yi)
             
        # and materials
        self.setMaterial = TheBountyMaterialWrite(self.yi, self.materialMap, self.textures.loadedTextures)

    def exportScene(self):
        #
        self.exportTextures()
        #for obj in self.scene.objects:
        #    self.exportTexture(obj)
            
        self.exportMaterials()
        self.geometry.setScene(self.scene)
        self.exportObjects()
        self.geometry.createCamera()
        self.environment.setEnvironment(self.scene)
    
    def exportTextures(self):
        # find all used scene textures
        #textureScene=[]
        self.createDefaultBlends()
        for tex in bpy.data.textures:
            # skip 'preview' and 'world environment' textures
            if (self.is_preview and tex.name == "fakeshadow") or not tex.users_material:
                continue
            self.textures.writeTexture(self.scene, tex)
    
   
    def object_on_visible_layer(self, obj):
        obj_visible = False
        for layer_visible in [object_layers and scene_layers for object_layers, scene_layers in zip(obj.layers, self.scene.layers)]:
            obj_visible |= layer_visible
        return obj_visible

    def exportObjects(self):
        self.yi.printInfo("Exporter: Processing Lamps...")

        #---------------------------
        # export only visible lamps
        #---------------------------
        for obj in [o for o in self.scene.objects if not o.hide_render and o.is_visible(self.scene) and o.type == 'LAMP']:
            if obj.is_duplicator:
                obj.create_dupli_list(self.scene)
                for obj_dupli in obj.dupli_list:
                    matrix = obj_dupli.matrix.copy()
                    self.lights.createLight(self.yi, obj_dupli.object, matrix)

                if obj.dupli_list:
                    obj.free_dupli_list()
            else:
                if obj.parent and obj.parent.is_duplicator:
                    continue
                self.lights.createLight(self.yi, obj, obj.matrix_world)

        self.yi.printInfo("Exporter: Processing Geometry...")

        #-----------------------------
        # export only visible objects
        #-----------------------------
        baseIds = {}
        dupBaseIds = {}

        for obj in [o for o in self.scene.objects if not o.hide_render and (o.is_visible(self.scene) or o.hide) \
        and self.object_on_visible_layer(o) and (o.type in {'MESH', 'SURFACE', 'CURVE', 'FONT', 'EMPTY'})]:
            # Exporting dupliObjects as instances, also check for dupliObject type 'EMPTY' and don't export them as geometry
            if obj.is_duplicator:
                self.yi.printInfo("Processing duplis for: {0}".format(obj.name))
                obj.dupli_list_create(self.scene)

                for obj_dupli in [od for od in obj.dupli_list if not od.object.type == 'EMPTY']:
                    #self.exportTexture(obj_dupli.object)
                    for mat_slot in obj_dupli.object.material_slots:
                        if mat_slot.material not in self.exportedMaterials: #materials:
                            self.exportMaterial(mat_slot.material)

                    if not self.scene.render.use_instances:
                        matrix = obj_dupli.matrix.copy()
                        self.geometry.writeMesh(obj_dupli.object, matrix)
                    else:
                        if obj_dupli.object.name not in dupBaseIds:
                            dupBaseIds[obj_dupli.object.name] = self.geometry.writeInstanceBase(obj_dupli.object)
                        matrix = obj_dupli.matrix.copy()
                        self.geometry.writeInstance(dupBaseIds[obj_dupli.object.name], matrix, obj_dupli.object.name)

                if obj.dupli_list is not None:
                    obj.dupli_list_clear()

                # check if object has particle system and uses the option for 'render emitter'
                if hasattr(obj, 'particle_systems'):
                    for pSys in obj.particle_systems:
                        check_rendertype = pSys.settings.render_type in {'OBJECT', 'GROUP'}
                        if check_rendertype and pSys.settings.use_render_emitter:
                            matrix = obj.matrix_world.copy()
                            self.geometry.writeMesh(obj, matrix)

            # no need to write empty object from here on, so continue with next object in loop
            elif obj.type == 'EMPTY':
                continue

            # Exporting objects with shared mesh data blocks as instances
            elif obj.data.users > 1 and self.scene.render.use_instances:
                self.yi.printInfo("Processing shared mesh data node object: {0}".format(obj.name))
                if obj.data.name not in baseIds:
                    baseIds[obj.data.name] = self.geometry.writeInstanceBase(obj)

                if obj.name not in dupBaseIds:
                    matrix = obj.matrix_world.copy()
                    self.geometry.writeInstance(baseIds[obj.data.name], matrix, obj.data.name)

            elif obj.data.name not in baseIds and obj.name not in dupBaseIds:
                self.geometry.writeObject(obj)

    #
    def createDefaultBlends(self):
        #
        if 'blendone' not in bpy.data.materials:
            m1 = bpy.data.materials.new('blendone')
            m1.diffuse_color = (0.0, 0.0, 1.0)
            m1.bounty.mat_type = 'shinydiffusemat'
                        
        if 'blendtwo' not in bpy.data.materials:
            m2 = bpy.data.materials.new('blendtwo')
            m1.diffuse_color =(1.0, 0.0, 0.0)
            m2.bounty.mat_type = 'glossy'
    
    
    def handleBlendMat(self, mat):
        #-------------------------
        # blend material one
        #-------------------------
        if mat.bounty.blendOne in {"", mat.name}:
            self.yi.printWarning("Not valid material for blend component. Using default 'blendone'")
            mat.bounty.blendOne = "blendone"       
        mat1 = bpy.data.materials[mat.bounty.blendOne]
        
        # not recursive blend        
        if mat1.bounty.mat_type == 'blend':
            self.yi.printWarning("Exporter: Recursive Blend material not allowed. Changed type to shinydiffusemat")
            mat1.bounty.mat_type = 'shinydiffusemat'
            
        # write blend material one
        if mat1 not in self.exportedMaterials:
            self.exportedMaterials.add(mat1)
            self.setMaterial.writeMaterial(mat1)
            
        #-------------------------
        # blend material two
        #-------------------------
        if mat.bounty.blendTwo in {"", mat.name, mat1.name}:
            self.yi.printWarning("Not valid material for blend component. Using default 'blendtwo'")
            mat.bounty.blendTwo = "blendtwo"
        mat2 = bpy.data.materials[mat.bounty.blendTwo]
            
        # not recursive 'blend'
        if mat2.bounty.mat_type == 'blend':
            self.yi.printWarning("Exporter: Recursive Blend material not allowed. Change type to glossy")
            mat2.bounty.mat_type = 'glossy'
            
        # write blend material two    
        if mat2 not in self.exportedMaterials:
            self.exportedMaterials.add(mat2)
            self.setMaterial.writeMaterial(mat2)
            
        if mat1.name == mat2.name:
            self.yi.printWarning("Exporter: Problem with blend material {0}."
                                 " {1} and {2} to blend are the same materials".format(mat.name, mat1.name, mat2.name))        
        
        if mat not in self.exportedMaterials:
            self.exportedMaterials.add(mat)
            self.setMaterial.writeMaterial(mat)

    def exportMaterials(self):
        self.yi.printInfo("Exporter: Processing Materials...")
        self.exportedMaterials = set()
        
        #---------------------------------------------------
        # create shiny diffuse material for use by default
        # it will be assigned, if object has no material(s)
        #---------------------------------------------------
        self.yi.paramsClearAll()
        self.yi.paramsSetString("type", "shinydiffusemat")
        self.yi.paramsSetColor("color", 0.8, 0.8, 0.8)
        self.yi.printInfo("Exporter: Creating Material \"defaultMat\"")
        ymat = self.yi.createMaterial("defaultMat")
        self.materialMap["default"] = ymat
        #---------------------------------------------------
        # create a shinydiffuse material for "Clay Render"
        # exception: don't create for material preview mode
        #---------------------------------------------------
        if not self.is_preview:
            self.yi.paramsClearAll()
            self.yi.paramsSetString("type", "shinydiffusemat")
            cCol = self.scene.bounty.gs_clay_col
            self.yi.paramsSetColor("color", cCol[0], cCol[1], cCol[2])
            self.yi.printInfo("Exporter: Creating Material \"clayMat\"")
            cmat = self.yi.createMaterial("clayMat")
            self.materialMap["clay"] = cmat
        #----------------------------------------------
        # override all materials in 'clay render' mode
        #----------------------------------------------
        for obj in [o for o in self.scene.objects if not self.scene.bounty.gs_clay_render]:
            for mat_slot in obj.material_slots:
                if mat_slot.material not in self.exportedMaterials:
                    self.exportMaterial(mat_slot.material)

    def exportMaterial(self, material):
        if material:
            # must make sure all materials used by a blend mat
            # are written before the blend mat itself                
            if material.bounty.mat_type == 'blend':
                self.handleBlendMat(material)
            else:
                self.exportedMaterials.add(material)
                self.setMaterial.writeMaterial(material, self.is_preview)

    def decideOutputFileName(self, output_path, filetype):
                
        filetype = switchFileType.get(filetype, 'png')
        # write image or XML-File with filename from framenumber
        frame_numb_str = "{:0" + str(len(str(self.scene.frame_end))) + "d}"
        output = os.path.join(output_path, frame_numb_str.format(self.scene.frame_current))
        # try to create dir if it not exists...
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except:
                print("Unable to create directory...")
                import traceback
                traceback.print_exc()
                output = ""
        outputFile = output + "." + filetype

        return outputFile, output, filetype

    
    def update(self, data, scene):
        # callback to export the scene
        self.update_stats("", "Setting up render")
        if not self.is_preview:
            scene.frame_set(scene.frame_current)

        self.scene = scene
        render = scene.render

        filePath = bpy.path.abspath(render.filepath)
        filePath = os.path.realpath(filePath)
        filePath = os.path.normpath(filePath)

        [self.sizeX, self.sizeY, self.bStartX, self.bStartY, self.bsizeX, self.bsizeY, camDummy] = tby_scene.getRenderCoords(scene)

        if render.use_border:
            self.resX = self.bsizeX
            self.resY = self.bsizeY
        else:
            self.resX = self.sizeX
            self.resY = self.sizeY
        # render type setup
        if scene.bounty.gs_type_render == "file":
            self.setInterface(yafrayinterface.yafrayInterface_t())
            self.yi.setInputGamma(scene.bounty.gs_gamma_input, scene.bounty.sc_apply_gammaInput)
            self.outputFile, self.output, self.file_type = self.decideOutputFileName(filePath, scene.bounty.img_output)
            self.yi.paramsClearAll()
            self.yi.paramsSetString("type", self.file_type)
            self.yi.paramsSetBool("alpha_channel", render.image_settings.color_mode == "RGBA")
            self.yi.paramsSetBool("z_channel", scene.bounty.gs_z_channel)
            self.yi.paramsSetInt("width", self.resX)
            self.yi.paramsSetInt("height", self.resY)
            self.ih = self.yi.createImageHandler("outFile")
            self.co = yafrayinterface.imageOutput_t(self.ih, str(self.outputFile), 0, 0)

        elif scene.bounty.gs_type_render == "xml":
            self.setInterface(yafrayinterface.xmlInterface_t())
            self.yi.setInputGamma(scene.bounty.gs_gamma_input, scene.bounty.sc_apply_gammaInput)
            self.outputFile, self.output, self.file_type = self.decideOutputFileName(filePath, 'XML')
            self.yi.paramsClearAll()
            self.co = yafrayinterface.imageOutput_t()
            self.yi.setOutfile(self.outputFile)

        else:
            self.setInterface(yafrayinterface.yafrayInterface_t())
            self.yi.setInputGamma(scene.bounty.gs_gamma_input, scene.bounty.sc_apply_gammaInput)

        self.yi.startScene()
        self.exportScene()
        self.lightIntegrator.exportIntegrator(self.scene.bounty)
        self.lightIntegrator.exportVolumeIntegrator(self.scene)

        # must be called last as the params from here will be used by render()
        tby_scene.exportRenderSettings(self.yi, self.scene)

    def render(self, scene):
        #--------------------------------------------
        # povman: fix issue when freestyle is active
        # result: doble render pass and black screen
        #-------------------------------------------
        bpy.context.scene.render.use_freestyle = False
        
        # callback to render scene if not scene.name == 'preview':
        if scene.name == 'preview':
            self.is_preview = True
        scene = scene.bounty
        # test for keep postprocess state
        postprocess = self.bl_use_postprocess
        #
        self.bl_use_postprocess = False   

        if scene.gs_type_render == "file" and not self.is_preview:
            self.yi.printInfo("Exporter: Rendering to file {0}".format(self.outputFile))
            
            self.yi.render(self.co)
            result = self.begin_result(0, 0, self.resX, self.resY)
            lay = result.layers[0]

            # exr format has z-buffer included, so no need to load '_zbuffer' - file
            if scene.gs_z_channel and not scene.img_output == 'OPEN_EXR':
                # TODO: need review that option for load both files when z-depth is rendered
                # except when use exr format
                #lay.load_from_file("{0}.{1}".format(self.output, self.file_type))
                lay.load_from_file("{0}_zbuffer.{1}".format(self.output, self.file_type))
                
            else:
                lay.load_from_file(self.outputFile)
            self.end_result(result)

        elif scene.gs_type_render == "xml" and not self.is_preview:
            self.yi.printInfo("Exporter: Writing XML to file {0}".format(self.outputFile))
            self.yi.render(self.co)

        else:# into blender

            def progressCallback(command, *args):
                if not self.test_break():
                    if command == "tag":
                        self.tag = args[0]
                    elif command == "progress":
                        self.prog = args[0]
                    # test for add more into to 'tag'
                    integrator = bpy.context.scene.bounty.intg_light_method
                    self.update_stats("TheBounty Render: ", "{0}: {1}".format(integrator, self.tag))
                    #
                    self.update_progress(self.prog)
                    
            def drawAreaCallback(*args):
                x, y, w, h, tile = args
                result = self.begin_result(x, y, w, h)
                lay = result.layers[0]
                try:
                    if bpy.app.version < (2, 74, 4 ):
                        lay.rect, lay.passes[0].rect = tile 
                    else:
                        lay.passes[0].rect, lay.passes[1].rect = tile
                except:
                    pass

                self.end_result(result)

            def flushCallback(*args):
                w, h, tile = args
                result = self.begin_result(0, 0, w, h)
                lay = result.layers[0]
                try:
                    if bpy.app.version < (2, 74, 4 ):
                        lay.rect, lay.passes[0].rect = tile 
                    else:
                        lay.passes[0].rect, lay.passes[1].rect = tile
                except BaseException as e:
                    pass

                self.end_result(result)
                
            # define thread
            thread = threading.Thread(target=self.yi.render,
                                 args=(self.resX, self.resY,
                                       self.bStartX, self.bStartY,
                                       self.is_preview,
                                       drawAreaCallback,
                                       flushCallback,
                                       progressCallback)
                                 )
            # run..
            thread.start()

            while thread.isAlive() and not self.test_break():
                time.sleep(0.2)

            if thread.isAlive():
                self.update_stats("", "Aborting...")
                self.yi.abort()
                thread.join()
        #
        self.yi.clearAll()
        del self.yi
        self.update_stats("", "Done!")
        self.bl_use_postprocess = postprocess

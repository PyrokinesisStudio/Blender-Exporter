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

import os, struct
import bpy
import time
import math
import mathutils
import yafrayinterface


def multiplyMatrix4x4Vector4(matrix, vector):
    result = mathutils.Vector((0.0, 0.0, 0.0, 0.0))
    for i in range(4):
        result[i] = vector * matrix[i]  # use reverse vector multiply order, API changed with rev. 38674
        
    return result


class exportObject(object):
    def __init__(self, yi, mMap, preview):
        self.yi = yi
        self.materialMap = mMap
        self.is_preview = preview

    def setScene(self, scene):

        self.scene = scene

    def createCamera(self):

        yi = self.yi
        yi.printInfo("Exporting Camera")

        camera = self.scene.camera
        render = self.scene.render
        
        # get cam worldspace transformation matrix, e.g. if cam is parented matrix_local does not work
        matrix = camera.matrix_world.copy()
        # matrix indexing (row, colums) changed in Blender rev.42816, for explanation see also:
        # http://wiki.blender.org/index.php/User:TrumanBlending/Matrix_Indexing
        pos = matrix.col[3]
        direction = matrix.col[2]
        up = pos + matrix.col[1]

        to = pos - direction

        x = int(render.resolution_x * render.resolution_percentage * 0.01)
        y = int(render.resolution_y * render.resolution_percentage * 0.01)
        #
        cam = camera.data
        #
        yi.paramsClearAll() 

        yi.paramsSetString("type", cam.bounty.camera_type)

        if cam.bounty.use_clipping:
            yi.paramsSetFloat("nearClip", cam.clip_start)
            yi.paramsSetFloat("farClip", cam.clip_end)

        if cam.bounty.camera_type == "orthographic":
            yi.paramsSetFloat("scale", cam.ortho_scale)

        elif cam.bounty.camera_type in {"perspective", "architect"}:
            # Blenders GSOC 2011 project "tomato branch" merged into trunk.
            # Check for sensor settings and use them in yafaray exporter also.
            if cam.sensor_fit == 'AUTO':
                horizontal_fit = (x > y)
                sensor_size = cam.sensor_width
            elif cam.sensor_fit == 'HORIZONTAL':
                horizontal_fit = True
                sensor_size = cam.sensor_width
            else:
                horizontal_fit = False
                sensor_size = cam.sensor_height

            if horizontal_fit:
                f_aspect = 1.0
            else:
                f_aspect = x / y

            yi.paramsSetFloat("focal", cam.lens / (f_aspect * sensor_size))

            # DOF params, only valid for real camera
            # use DOF object distance if present or fixed DOF
            if cam.dof_object is not None:
                # use DOF object distance
                #dist = (pos.xyz - cam.dof_object.location.xyz).length
                dof_distance = (pos.xyz - cam.dof_object.location.xyz).length #dist
            else:
                # use fixed DOF distance
                dof_distance = cam.dof_distance

            yi.paramsSetFloat("dof_distance", dof_distance)
            yi.paramsSetFloat("aperture", cam.bounty.aperture)
            # bokeh params
            yi.paramsSetString("bokeh_type", cam.bounty.bokeh_type)
            yi.paramsSetString("bokeh_bias", cam.bounty.bokeh_bias)
            yi.paramsSetFloat("bokeh_rotation", cam.bounty.bokeh_rotation)

        elif cam.bounty.camera_type == "angular":
            yi.paramsSetBool("circular", cam.bounty.circular)
            yi.paramsSetBool("mirrored", cam.bounty.mirrored)
            yi.paramsSetFloat("max_angle", cam.bounty.max_angle)
            yi.paramsSetFloat("angle", cam.bounty.angular_angle)

        yi.paramsSetInt("resx", x)
        yi.paramsSetInt("resy", y)

        yi.paramsSetPoint("from", pos[0], pos[1], pos[2])
        yi.paramsSetPoint("up", up[0], up[1], up[2])
        yi.paramsSetPoint("to", to[0], to[1], to[2])
        yi.createCamera("cam")

    def getBBCorners(self, obj):
        bb = obj.bound_box   # look bpy.types.Object if there is any problem

        bbmin = [1e10, 1e10, 1e10]
        bbmax = [-1e10, -1e10, -1e10]

        for corner in bb:
            for i in range(3):
                if corner[i] < bbmin[i]:
                    bbmin[i] = corner[i]
                if corner[i] > bbmax[i]:
                    bbmax[i] = corner[i]

        return bbmin, bbmax

    def get4x4Matrix(self, matrix):

        ret = yafrayinterface.matrix4x4_t()

        for i in range(4):
            for j in range(4):
                ret.setVal(i, j, matrix[i][j])

        return ret

    def writeObject(self, obj, matrix=None):

        if not matrix:
            matrix = obj.matrix_world.copy()

        if obj.bounty.geometry_type == "volume_region":
            self.writeVolumeObject(obj, matrix)

        elif obj.bounty.geometry_type == "mesh_light":
            self.writeMeshLight(obj, matrix)

        elif obj.bounty.geometry_type == "portal_light":
            self.writeBGPortal(obj, matrix)

        elif obj.particle_systems:  # Particle Hair system
            # TODO: add bake option in UI
            if self.is_preview:
                self.previewhair(obj)
            else:                
                bake = False #self.scene.bounty.gs_type_render == 'xml'
                #
                for pSys in obj.particle_systems:
                    if pSys.settings.type == 'HAIR' and pSys.settings.render_type == 'PATH':
                        if pSys.settings.bounty.strand_shape == 'cylinder':
                            # this method create a lot of new geometry
                            # then, its good only for small hair particle system
                            # or for generate hight resolution closed hairs
                            crv = bpy.data.curves.new('hair_tmp_curve', 'CURVE')
                            crv_ob = bpy.data.objects.new("%s_ob" % crv.name, crv)
                            crv_ob.hide_render = True
                            # generate..
                            self.generate_hair_curves(obj, pSys, crv_ob, crv, matrix)
                            # Clean up the scene
                            bpy.data.objects.remove(crv_ob)
                            bpy.data.curves.remove(crv)
                        if bake:
                            self.bakeParticleStrands(obj, matrix, pSys)
                        else:
                            self.writeParticleStrands(obj, matrix, pSys)

        else:  # The rest of the object types
            self.writeMesh(obj, matrix)

    def writeInstanceBase(self, object):

        # Generate unique object ID
        ID = self.yi.getNextFreeID()

        self.yi.printInfo("Exporting Base Mesh: {0} with ID: {1:d}".format(object.name, ID))

        obType = 512  # Create this geometry object as a base object for instances

        self.writeGeometry(ID, object, None, obType)  # We want the vertices in object space

        return ID

    def writeInstance(self, oID, obj2WorldMatrix, name):

        self.yi.printInfo("Exporting Instance of {0} [ID = {1:d}]".format(name, oID))

        mat4 = obj2WorldMatrix.to_4x4()

        o2w = self.get4x4Matrix(mat4)

        self.yi.addInstance(oID, o2w)
        del mat4
        del o2w

    def writeMesh(self, object, matrix):

        self.yi.printInfo("Exporting Mesh: {0}".format(object.name))

        # Generate unique object ID
        ID = self.yi.getNextFreeID()

        self.writeGeometry(ID, object, matrix)  # obType in 0, default, the object is rendered

    def writeBGPortal(self, object, matrix):
        # use object subclass properties
        obj = object.bounty

        self.yi.printInfo("Exporting Background Portal Light: {0}".format(object.name))

        # Generate unique object ID
        ID = self.yi.getNextFreeID()

        self.yi.paramsClearAll()
        self.yi.paramsSetString("type", "bgPortalLight")
        self.yi.paramsSetFloat("power", obj.bgp_power)
        self.yi.paramsSetInt("samples", obj.bgp_samples)
        self.yi.paramsSetInt("object", ID)
        self.yi.paramsSetBool("with_caustic", obj.bgp_with_caustic)
        self.yi.paramsSetBool("with_diffuse", obj.bgp_with_diffuse)
        self.yi.paramsSetBool("photon_only", obj.bgp_photon_only)
        self.yi.createLight(object.name)

        obType = 256  # Makes object invisible to the renderer (doesn't enter the kdtree)

        self.writeGeometry(ID, object, matrix, obType)

    def writeMeshLight(self, object, matrix):
        # use object subclass properties
        obj = object.bounty        

        self.yi.printInfo("Exporting Meshlight: {0}".format(object.name))

        # Generate unique object ID
        ID = self.yi.getNextFreeID()

        ml_matname = "ML_"
        ml_matname += object.name + "." + str(object.__hash__())

        self.yi.paramsClearAll()
        self.yi.paramsSetString("type", "light_mat")
        self.yi.paramsSetBool("double_sided", obj.ml_double_sided)
        c = obj.ml_color
        self.yi.paramsSetColor("color", c[0], c[1], c[2])
        self.yi.paramsSetFloat("power", obj.ml_power)
        ml_mat = self.yi.createMaterial(ml_matname)

        self.materialMap[ml_matname] = ml_mat

        # Export mesh light
        self.yi.paramsClearAll()
        self.yi.paramsSetString("type", "meshlight")
        self.yi.paramsSetBool("double_sided", obj.ml_double_sided)
        c = obj.ml_color
        self.yi.paramsSetColor("color", c[0], c[1], c[2])
        self.yi.paramsSetFloat("power", obj.ml_power)
        self.yi.paramsSetInt("samples", obj.ml_samples)
        self.yi.paramsSetInt("object", ID)
        self.yi.createLight(object.name)
        # test for hidden meshlight object
        objType = 256 if obj.ml_hidde_mesh else 0

        self.writeGeometry(ID, object, matrix, objType, ml_mat)

    def writeVolumeObject(self, object, matrix):
        # use object subclass properties
        obj = object.bounty

        self.yi.printInfo("Exporting Volume Region: {0}".format(object.name))

        yi = self.yi
        # me = obj.data  /* UNUSED */
        # me_materials = me.materials  /* UNUSED */

        yi.paramsClearAll()

        if obj.vol_region == 'ExpDensity Volume':
            yi.paramsSetString("type", "ExpDensityVolume")
            yi.paramsSetFloat("a", obj.vol_height)
            yi.paramsSetFloat("b", obj.vol_steepness)

        elif obj.vol_region == 'Uniform Volume':
            yi.paramsSetString("type", "UniformVolume")

        elif obj.vol_region == 'Noise Volume':
            if not object.active_material:
                yi.printError("Volume object ({0}) is missing the materials".format(object.name))
            elif not object.active_material.active_texture:
                yi.printError("Volume object's material ({0}) is missing the noise texture".format(object.name))
            else:
                texture = object.active_material.active_texture

                yi.paramsSetString("type", "NoiseVolume")
                yi.paramsSetFloat("sharpness", obj.vol_sharpness)
                yi.paramsSetFloat("cover", obj.vol_cover)
                yi.paramsSetFloat("density", obj.vol_density)
                yi.paramsSetString("texture", texture.name)
            
        # common parameters
        yi.paramsSetFloat("sigma_a", obj.vol_absorp)
        yi.paramsSetFloat("sigma_s", obj.vol_scatter)
        yi.paramsSetInt("attgridScale", self.scene.world.bounty.v_int_attgridres)

        # Calculate BoundingBox: get the low corner (minx, miny, minz)
        # and the up corner (maxx, maxy, maxz) then apply object scale,
        # also clamp the values to min: -1e10 and max: 1e10

        mesh = object.to_mesh(self.scene, True, 'RENDER')
        mesh.transform(matrix)

        vec = [j for v in mesh.vertices for j in v.co]

        yi.paramsSetFloat("minX", max(min(vec[0::3]), -1e10))
        yi.paramsSetFloat("minY", max(min(vec[1::3]), -1e10))
        yi.paramsSetFloat("minZ", max(min(vec[2::3]), -1e10))
        yi.paramsSetFloat("maxX", min(max(vec[0::3]), 1e10))
        yi.paramsSetFloat("maxY", min(max(vec[1::3]), 1e10))
        yi.paramsSetFloat("maxZ", min(max(vec[2::3]), 1e10))

        yi.createVolumeRegion("VR.{0}-{1}".format(obj.name, str(obj.__hash__())))
        bpy.data.meshes.remove(mesh)

    def writeGeometry(self, ID, obj, matrix, obType=0, oMat=None):

        mesh = obj.to_mesh(self.scene, True, 'RENDER')
        isSmooth = False
        hasOrco = False
        # test for UV Map after BMesh API changes
        uv_texture = mesh.tessface_uv_textures if 'tessface_uv_textures' in dir(mesh) else mesh.uv_textures
        # test for faces after BMesh API changes
        face_attr = 'faces' if 'faces' in dir(mesh) else 'tessfaces'
        hasUV = len(uv_texture) > 0  # check for UV's

        if face_attr == 'tessfaces':
            if not mesh.tessfaces and mesh.polygons:
                # BMesh API update, check for tessellated faces, if needed calculate them...
                mesh.update(calc_tessface=True)

            if not mesh.tessfaces:
                # if there are no faces, no need to write geometry, remove mesh data then...
                bpy.data.meshes.remove(mesh)
                return
        else:
            if not mesh.faces:
                # if there are no faces, no need to write geometry, remove mesh data then...
                bpy.data.meshes.remove(mesh)
                return

        # Check if the object has an orco mapped texture
        for mat in [mmat for mmat in mesh.materials if mmat is not None]:
            for m in [mtex for mtex in mat.texture_slots if mtex is not None]:
                if m.texture_coords == 'ORCO':
                    hasOrco = True
                    break
            if hasOrco:
                break

        # normalized vertex positions for orco mapping
        ov = []

        if hasOrco:
            # Keep a copy of the untransformed vertex and bring them
            # into a (-1 -1 -1) (1 1 1) bounding box
            bbMin, bbMax = self.getBBCorners(obj)

            delta = []

            for i in range(3):
                delta.append(bbMax[i] - bbMin[i])
                if delta[i] < 0.0001:
                    delta[i] = 1

            # use untransformed mesh's vertices
            for v in mesh.vertices:
                normCo = []
                for i in range(3):
                    normCo.append(2 * (v.co[i] - bbMin[i]) / delta[i] - 1)

                ov.append([normCo[0], normCo[1], normCo[2]])

        # Transform the mesh after orcos have been stored and only if matrix exists
        if matrix is not None:
            mesh.transform(matrix)

        self.yi.paramsClearAll()
        self.yi.startGeometry()

        self.yi.startTriMesh(ID, len(mesh.vertices), len(getattr(mesh, face_attr)), hasOrco, hasUV, obType)

        for ind, v in enumerate(mesh.vertices):
            if hasOrco:
                self.yi.addVertex(v.co[0], v.co[1], v.co[2], ov[ind][0], ov[ind][1], ov[ind][2])
            else:
                self.yi.addVertex(v.co[0], v.co[1], v.co[2])

        for index, f in enumerate(getattr(mesh, face_attr)):
            if f.use_smooth:
                isSmooth = True

            if oMat:
                ymaterial = oMat
            else:
                ymaterial = self.getFaceMaterial(mesh.materials, f.material_index, obj.material_slots)

            co = None
            if hasUV:

                if self.is_preview:
                    co = uv_texture[0].data[index].uv
                else:
                    co = uv_texture.active.data[index].uv

                uv0 = self.yi.addUV(co[0][0], co[0][1])
                uv1 = self.yi.addUV(co[1][0], co[1][1])
                uv2 = self.yi.addUV(co[2][0], co[2][1])

                self.yi.addTriangle(f.vertices[0], f.vertices[1], f.vertices[2], uv0, uv1, uv2, ymaterial)
            else:
                self.yi.addTriangle(f.vertices[0], f.vertices[1], f.vertices[2], ymaterial)

            if len(f.vertices) == 4:
                if hasUV:
                    uv3 = self.yi.addUV(co[3][0], co[3][1])
                    self.yi.addTriangle(f.vertices[0], f.vertices[2], f.vertices[3], uv0, uv2, uv3, ymaterial)
                else:
                    self.yi.addTriangle(f.vertices[0], f.vertices[2], f.vertices[3], ymaterial)

        self.yi.endTriMesh()

        if isSmooth and mesh.use_auto_smooth:
            self.yi.smoothMesh(0, math.degrees(mesh.auto_smooth_angle))
        elif isSmooth and obj.type == 'FONT':  # getting nicer result with smooth angle 60 degr. for text objects
            self.yi.smoothMesh(0, 60)
        elif isSmooth:
            self.yi.smoothMesh(0, 181)

        self.yi.endGeometry()

        bpy.data.meshes.remove(mesh)

    def getFaceMaterial(self, meshMats, matIndex, matSlots):

        ymaterial = self.materialMap["default"]

        if self.scene.bounty.gs_clay_render:
            ymaterial = self.materialMap["clay"]
        elif len(meshMats) and meshMats[matIndex]:
            mat = meshMats[matIndex]
            if mat in self.materialMap:
                ymaterial = self.materialMap[mat]
        else:
            for mat_slots in [ms for ms in matSlots if ms.material in self.materialMap]:
                ymaterial = self.materialMap[mat_slots.material]

        return ymaterial
    
    def defineStrandValues(self, material):
        #
        if material.strand.use_blender_units:
            strandStart = material.strand.root_size
            strandEnd = material.strand.tip_size
            strandShape = material.strand.shape
        else:  # Blender unit conversion
            strandStart = material.strand.root_size / 100
            strandEnd = material.strand.tip_size / 100
            strandShape = material.strand.shape
        return strandStart, strandEnd, strandShape
    
    def writeParticleStrands(self, obj, matrix, pSys):

        yi = self.yi
        totalNumberOfHairs = 0
        
        # Check for modifiers..
        for mod in [m for m in obj.modifiers if (m is not None) and (m.type == 'PARTICLE_SYSTEM')]:
            if mod.show_render and (pSys.name == mod.particle_system.name):
                yi.printInfo("Exporter: Creating Hair Particle System {!r}".format(pSys.name))
                tstart = time.time()
                #                    
                strandStart = 0.01
                strandEnd = 0.01
                strandShape = 0.0
                #
                print('material: ', pSys.settings.material)
                try:
                    hairMat = obj.material_slots[pSys.settings.material - 1].material
                    strandStart, strandEnd, strandShape = self.defineStrandValues(hairMat)
                except:
                    hairMat = "default"             
                # if clay render is activated..
                if self.scene.bounty.gs_clay_render:
                    hairMat = "clay"
                #
                pSys.set_resolution(self.scene, obj, 'RENDER')    
                steps = pSys.settings.render_step
                steps = 2 ** steps
                print('[Hair] Curve steps: ', steps)
                #
                parents = len(pSys.particles)
                childrens = len(pSys.child_particles)
                            
                totalHairs =  childrens if childrens > 0 else parents
                #
                for particleIdx in range(0, totalHairs):
                    CID = yi.getNextFreeID()
                    yi.paramsClearAll()
                    yi.startGeometry()
                    yi.startCurveMesh(CID, 1)
                    #
                    for step in range(0, steps):
                        point = obj.matrix_world.inverted()*(pSys.co_hair(obj, particleIdx, step))
                        if point.length_squared != 0:
                            yi.addVertex(point[0], point[1], point[2])                            
                    #
                    yi.endCurveMesh(self.materialMap[hairMat], strandStart, strandEnd, strandShape)
                    yi.endGeometry()
                #
                yi.printInfo("Exporter: Particle creation time: {0:.3f}".format(time.time() - tstart))
            
        # total hair's for each particle system              
        yi.printInfo("Exporter: Total hair's created: {0} ".format(totalHairs))
            
        # We only need to render emitter object once
        if pSys.settings.use_render_emitter:
            self.writeMesh(obj, matrix)
                        
            
    def bakeParticleStrands(self, obj, matrix, pSys):
        #------------------------------------------
        # code heavily based on LuxBlend exporter
        #------------------------------------------
        yi = self.yi
        # Check for modifiers visibility..
        for mod in obj.modifiers:
            if mod.show_render and (pSys.name == mod.particle_system.name):

                yi.printInfo('Exporting Hair system {0}...'.format(pSys.name))                
                #                    
                strandStart = pSys.settings.bounty.root_size * 0.01
                strandEnd = pSys.settings.bounty.tip_size * 0.01
                strandShape = pSys.settings.bounty.shape
                # review this..
                hair_size = 0.01
                width_offset = 0.1                 
                    
                try:
                    hairMat = obj.material_slots[pSys.settings.material - 1].material                    
                except:
                    hairMat = "default"
                        
                # if clay render is activated..
                if self.scene.bounty.gs_clay_render:
                    hairMat = "clay"
                #
                pSys.set_resolution(self.scene, obj, 'RENDER')
                steps = 2 ** pSys.settings.render_step
                num_parents = len(pSys.particles)
                num_children = len(pSys.child_particles)        
                
                start = 0
                if num_children != 0:
                    # Number of virtual parents reduces the number of exported children
                    virtual_parents = math.trunc(0.3 * pSys.settings.virtual_parents * pSys.settings.child_nbr * num_parents)
                    start = num_parents + virtual_parents
        
                partsys_name = '%s_%s' % (obj.name, pSys.name)
        
                # Put HAIR_FILES files in frame-numbered subfolders to avoid
                # clobbering when rendering animations
                #sc_fr = '%s/%s/%s/%05d' % ( efutil.export_path, efutil.scene_filename(), 
                #                            bpy.path.clean_name(self.geometry_scene.name),
                #                            self.visibility_scene.frame_current)
                sc_fr = self.scene.render.filepath
                if not os.path.exists(sc_fr):
                    os.makedirs(sc_fr)
        
                hair_filename = '%s.hair' % bpy.path.clean_name(partsys_name)
                hair_file_path = '/'.join([sc_fr, hair_filename])
        
                segments = []
                points = []
                thickness = []
                colors = []
                uv_coords = []
                total_segments_count = 0
                vertex_color_layer = None
                uv_tex = None
                colorflag = 0
                uvflag = 0
                thicknessflag = 0
                image_width = 0
                image_height = 0
                image_pixels = []
        
                mesh = obj.to_mesh(self.scene, True, 'RENDER')
                uv_textures = mesh.tessface_uv_textures
                vertex_color = mesh.tessface_vertex_colors
        
                has_vertex_colors = vertex_color.active and vertex_color.active.data
        
                '''
                if psys.settings.bounty.export_color == 'vertex_color':
                    if has_vertex_colors:
                        vertex_color_layer = vertex_color.active.data
                        colorflag = 1
        
                if uv_textures.active and uv_textures.active.data:
                    uv_tex = uv_textures.active.data
                    if 0: #psys.settings.bounty.export_color == 'uv_texture_map':
                        if uv_tex[0].image:
                            image_width = uv_tex[0].image.size[0]
                            image_height = uv_tex[0].image.size[1]
                            image_pixels = uv_tex[0].image.pixels[:]
                            colorflag = 1
                    uvflag = 1
                '''
                info = 'Modify from LuxBlend exported to use with TheBounty'
        
                #transform = obj.matrix_world.inverted()
                total_strand_count = 0
                #
                if strandStart == strandEnd:
                    thicknessflag = 0
                    # set default tickness
                    hair_size = strandStart
                else:
                    thicknessflag = 1
        
                for pindex in range(start, num_parents + num_children):
                    #det.exported_objects += 1
                    point_count = 0
                    i = 0
        
                    if num_children == 0:
                        i = pindex
        
                    # A small optimization in order to speedup the export
                    # process: cache the uv_co and color value
                    uv_co = None
                    col = None
                    #seg_length = 1.0 
                    
                    for step in range(0, steps):
                        co = pSys.co_hair(obj, pindex, step)
                        #co = obj.matrix_world.inverted() * pSys.co_hair(obj, pindex, step)
                        #        
                        if not co.length_squared == 0:
                            points.append(co)
                            #
                            if thicknessflag:
                                if step == 0:
                                    thickness.append(strandStart)
                                elif step == steps -1:
                                    thickness.append(strandEnd)
                                else:
                                    thickness.append(0.0)
                            # end
                            point_count += + 1
        
                    if point_count == 1:
                        points.pop()
        
                        if thicknessflag:
                            thickness.pop()
                        point_count -= 1
                    elif point_count > 1:
                        segments.append(point_count - 1)
                        total_strand_count += 1
                        total_segments_count = total_segments_count + point_count - 1
        
                with open(hair_file_path, 'wb') as hair_file:
                    # Binary hair file format from http://www.cemyuksel.com/research/hairmodels/
                    print('steps: ', steps)
                    print('hair size: ', hair_size)        
                    # File header
                    hair_file.write(b'HAIR')  # magic number
                    hair_file.write(struct.pack('<I', total_strand_count))  # total strand count
                    hair_file.write(struct.pack('<I', len(points)))  # total point count
                    # bit array for configuration
                    hair_file.write(struct.pack('<I',1 + 2 + 4 * thicknessflag + 16 * colorflag + 32 * uvflag))
                    hair_file.write(struct.pack('<I', steps))      # default segments count
                    hair_file.write(struct.pack('<f', hair_size))  # default thickness
                    hair_file.write(struct.pack('<f', 0.0))        # default transparency
                    color = (0.65, 0.65, 0.65)
                    hair_file.write(struct.pack('<3f', *color))  # default color
                    hair_file.write(struct.pack('<88s', info.encode()))  # information
        
                    # hair data
                    hair_file.write(struct.pack('<%dH' % (len(segments)), *segments))
                    #print('segments: ', len(segments))
        
                    for point in points:
                        hair_file.write(struct.pack('<3f', *point))
                    
                    if thicknessflag:
                        for thickn in thickness:
                            hair_file.write(struct.pack('<1f', thickn))
                            print("tickness: ", thickn)
                
                yi.printInfo('Binary hair file written: {0}'.format(hair_file_path))
                # write parameters on .xml file
                HID = yi.getNextFreeID()
                yi.paramsClearAll()
                yi.addHair(HID, hair_file_path, self.materialMap[hairMat])
                
                if pSys.settings.use_render_emitter:
                    matrix = obj.matrix_world.copy()
                    self.writeMesh(obj, matrix)
                    yi.printInfo('Writing Hair emitter')
        
        return
    
        
    def generate_hair_curves( self, obj, psys, crv_ob, crv_data, matrix):
        #
        # heavily based on Corona Blender exporter code
        #
        yi = self.yi
          
        for mod in obj.modifiers:
            if mod.show_render and (psys.name == mod.particle_system.name):
    
                yi.printInfo('Exporting Hair system {0}...'.format(psys.name))
            
                root_size = psys.settings.bounty.root_size
                tip_size = psys.settings.bounty.tip_size
                # Set the render resolution of the particle system
                psys.set_resolution( self.scene, obj, 'RENDER')
                steps = 2 ** psys.settings.render_step + 1
                parents = len( psys.particles)
                children = len( psys.child_particles)
                curves = []
                crv_meshes = []
                c_append = curves.append
                cm_append = crv_meshes.append
                transform = obj.matrix_world.inverted()
            
                obj.data.update(calc_tessface=True)
                # children is pre multiplied
                total = children if children != 0 else parents
                print("[Hair] Total curves", total)
                #
                for p in range( 0, total):
                    #
                    particle = None
                    if p >= parents:
                       particle = psys.particles[(p - parents) % parents]
                    else:
                       particle = psys.particles[p]            
            
                    crv = bpy.data.curves.new( 'hair_curve_%d' % p, 'CURVE')
                    curves.append( crv)
                    crv.splines.new( 'NURBS')
                    points = crv.splines[0].points
                    crv.splines[0].points.add( steps - 1)
                    crv.splines[0].use_endpoint_u = True
                    crv.splines[0].order_u = 4
                    crv.dimensions = '3D'
                    crv.fill_mode = 'FULL'
                    scaling = psys.settings.bounty.scaling
                    if psys.settings.bounty.thick:
                        crv.bevel_depth = scaling
                        crv.bevel_resolution = psys.settings.bounty.resolution
                    else:
                        crv.extrude = scaling
                    crv.resolution_u = 1
                    p_rad = root_size
                    shaft_size = min(root_size, tip_size)
                    diff = root_size - tip_size
                    co = None
                    curvesteps = steps
                    shapemod = (psys.settings.bounty.shape + 1) * (psys.settings.bounty.shape + 1)
            
                    if tip_size > 0.0 and psys.settings.bounty.close_tip:
                        curvesteps -= 1
            
                    step_size = diff / curvesteps
            
                    for step in range(0, curvesteps):
                        co = psys.co_hair( obj, p, step)
                        points[step].co = mathutils.Vector( ( co.x, co.y, co.z, 1.0))
                        points[step].radius = shaft_size + (curvesteps - step * shapemod) * step_size
            
                    if psys.settings.bounty.close_tip:
                        if tip_size == 0.0:
                            points.add(1)
                        points[curvesteps].co = mathutils.Vector( (co.x, co.y, co.z, 1.0))
                        points[curvesteps].radius = 0.0
            
                    crv.transform( transform)
                    # Create an object for the curve, add the material, then convert to mesh
                    crv_ob.data = bpy.data.curves[crv.name]
                    #
                    try:
                        hairmat = obj.material_slots[psys.settings.material - 1].material.name                    
                    except:
                        hairmat = "default"                            
                    #
                    if self.scene.bounty.gs_clay_render:
                        hairmat = "clay"
                    #
                    crv_ob.data.materials.append( bpy.data.materials[hairmat])
                    #
                    self.writeMesh(crv_ob, matrix)
                    #
                    crv_ob.data = crv_data
                    bpy.data.curves.remove( crv)
                psys.set_resolution( self.scene, obj, 'PREVIEW')
                # test
                if psys.settings.use_render_emitter:
                    matrix = obj.matrix_world.copy()
                    self.writeMesh(obj, matrix)
                return crv_meshes
    
    #
    def previewhair(self, obj):
        #
        yi = self.yi
        strandStart = .0512
        strandEnd = .0256
        strandShape = 0.0
        y = -3
        x = -3
        try:
            hairMat = obj.material_slots[0].material
        except:
            hairMat = "default" 
         
        for idx in range(0, 24):
            CID = yi.getNextFreeID()
            yi.paramsClearAll()
            yi.startGeometry()
            yi.startCurveMesh(CID, 1)
            #
            z = -1.0
            for step in range(0, 3):
                #
                yi.addVertex(x, y, z)
                z += 3
            #
            x += .25 
            y += .125
            #
            yi.endCurveMesh(self.materialMap[hairMat], strandStart, strandEnd, strandShape)
            yi.endGeometry()
        return True
    
def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method = 2, ngon_method = 2)
    bm.to_mesh(me)
    bm.free()
    del bm


    

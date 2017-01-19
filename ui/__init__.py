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

from . import prop_render
from . import prop_camera
from . import prop_material
from . import prop_texture
from . import prop_world
from . import prop_strand
from . import prop_object
from . import prop_light

from . import prop_smoke

from . import prop_scene
from . import prop_render_layer

from bl_ui import properties_object as properties_object
import bl_ui
for member in dir(properties_object):  # add all "object" panels from blender
    subclass = getattr(properties_object, member)
    try:
        subclass.COMPAT_ENGINES.add('THEBOUNTY')
    except:
        pass
del properties_object

from bl_ui import properties_particle as prop_particle
for member in dir(prop_particle):  # add all "particle" panels from blender
    subclass = getattr(prop_particle, member)
    try:
        subclass.COMPAT_ENGINES.add('THEBOUNTY')
    except:
        pass
del prop_particle

from bl_ui import properties_data_mesh as prop_data_mesh
for member in dir(prop_data_mesh):  # add all "object data" panels from blender
    subclass = getattr(prop_data_mesh, member)
    try:
        subclass.COMPAT_ENGINES.add('THEBOUNTY')
    except:
        pass
del prop_data_mesh

from bl_ui import properties_data_speaker as prop_data_speaker
for member in dir(prop_data_speaker):
    subclass = getattr(prop_data_speaker, member)
    try:
        subclass.COMPAT_ENGINES.add('THEBOUNTY')
    except:
        pass
del prop_data_speaker

#-------------------------
# common physics panels
#-------------------------
from bl_ui import properties_physics_common as prop_physics_common

prop_physics_common.PHYSICS_PT_add.COMPAT_ENGINES.add('THEBOUNTY')

del prop_physics_common

#-------------------------
# smoke physics panels
#-------------------------
from bl_ui import properties_physics_smoke as prop_physics_smoke
for member in dir(prop_physics_smoke):
    subclass = getattr(prop_physics_smoke, member)
    try:
        subclass.COMPAT_ENGINES.add('THEBOUNTY')
    except:
        pass
del prop_physics_smoke

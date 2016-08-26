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

from . import tby_object
from . import tby_material
from . import tby_light
from . import tby_scene
from . import tby_camera
from . import tby_texture
from . import tby_world


def register():
    tby_object.register()
    tby_material.register()
    tby_light.register()
    tby_scene.register()
    tby_camera.register()
    tby_texture.register()
    tby_world.register()


def unregister():
    tby_object.unregister()
    tby_material.unregister()
    tby_light.unregister()
    tby_scene.unregister()
    tby_camera.unregister()
    tby_texture.unregister()
    tby_world.unregister()

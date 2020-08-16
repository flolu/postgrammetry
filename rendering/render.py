import bpy

from ..utils import get_absolute_path, open_os_directory, un_hide, hide

class BatchRenderOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render'
    bl_label = 'batch render'
    bl_options = {'UNDO'}

    def execute(self, context):
      Render()
      return {'FINISHED'}

class Render():
  def __init__(self):

    for obj_name in [obj.name for obj in bpy.data.objects]:
      hide(obj_name)

    obj = bpy.context.object
    un_hide(obj.name)

    self.render_textures(obj)
    self.render_wireframe(obj)

  def render_textures(self, obj):
    material = obj.material_slots[0].material
    textures = []
    for n in material.node_tree.nodes:
      if n.type == 'TEX_IMAGE':
        textures.append(n.image)

    nodes = material.node_tree.nodes
    diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse_shader_node.location = (100, 500)

    ouput_node = nodes.get("Material Output")
    material.node_tree.links.new(diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])

    self.setup_evee()
    for texture in textures:
      image_texture_node = nodes.new('ShaderNodeTexImage')
      image = bpy.data.images[texture.name]
      image.colorspace_settings.name = 'sRGB'
      image_texture_node.image = image
      material.node_tree.links.new(image_texture_node.outputs['Color'], diffuse_shader_node.inputs['Color'])
      bpy.context.scene.render.filepath = bpy.path.abspath(bpy.context.scene.export_out_path + texture.name)
      bpy.ops.render.render(write_still = True)
      nodes.remove(image_texture_node)

    principled_bsdf = nodes.get("Principled BSDF")
    material.node_tree.links.new(principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
    nodes.remove(diffuse_shader_node)

  def render_wireframe(self, obj):
    bpy.context.scene.render.use_freestyle = True
    scene = bpy.context.scene
    freestyle = scene.view_layers[0].freestyle_settings
    linestyle = freestyle.linesets[0]
    scene.render.use_freestyle = True
    linestyle.select_silhouette = False
    linestyle.select_border = False
    linestyle.select_crease = False
    linestyle.select_edge_mark = True

    bpy.data.linestyles["LineStyle"].color = (0, 0, 0)
    bpy.data.linestyles["LineStyle"].thickness = 1.5

    material = obj.material_slots[0].material
    nodes = material.node_tree.nodes
    diffuse_shader_node = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse_shader_node.location = (100, 500)
    ouput_node = nodes.get("Material Output")
    material.node_tree.links.new(diffuse_shader_node.outputs['BSDF'], ouput_node.inputs['Surface'])

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.mark_freestyle_edge()
    bpy.ops.object.mode_set(mode='OBJECT')


    bpy.context.scene.render.filepath = bpy.path.abspath(bpy.context.scene.export_out_path + 'wireframe')
    bpy.ops.render.render(write_still = True)

    principled_bsdf = nodes.get("Principled BSDF")
    material.node_tree.links.new(principled_bsdf.outputs['BSDF'], ouput_node.inputs['Surface'])
    nodes.remove(diffuse_shader_node)
    bpy.context.scene.render.use_freestyle = False

  def setup_evee(self):
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.use_freestyle = False

    # TODO create node if not exists
    # world environment strength
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 20

class OpenRenderDirectoryOperator(bpy.types.Operator):
    bl_idname = 'postgrammetry.render_open_directory'
    bl_label = 'open render directory'
    bl_options = {'UNDO'}

    def execute(self, context):
      path = get_absolute_path(bpy.context.scene.render_out_path)
      open_os_directory(path)
      return {'FINISHED'}
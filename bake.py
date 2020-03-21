import bpy
import uuid
import time


class BatchBake(bpy.types.Operator):
    bl_idname = 'bb.bake'
    bl_label = 'batch bake'
    bl_options = {'UNDO'}

    def execute(self, context):
        def my_handler(scene):
            print("post render")

        bpy.app.handlers.render_complete.append(my_handler)
        bpy.app.handlers.render_post.append(my_handler)

        start_time = time.time()
        bpy.context.scene.baking_done = False

        high = context.scene.highpoly_bake_obj

        for obj in bpy.data.objects:
            obj.hide_render = True
            obj.hide_viewport = False

        low_objects = bpy.data.collections[
            context.scene.lowpoly_bake_obj].all_objects[:]
        for obj in low_objects:
            Bake(high, obj.name)

        end_time = time.time()
        bpy.context.scene.baking_done = True
        bpy.context.scene.baking_time = end_time - start_time
        return {'FINISHED'}


class Bake():
    def __init__(self, high, low):
        self.high = high
        self.low = low

        self.prepare()
        self.bake()
        self.clean()

    def prepare(self):
        self.remember_original_settings()

        bpy.data.scenes[bpy.context.scene.name].render.engine = 'CYCLES'
        bpy.data.objects[self.low].hide_render = False
        bpy.data.objects[self.high].hide_render = False

        self.bake_material = bpy.data.materials.new(name=self.low +
                                                    str(uuid.uuid4()))
        if bpy.data.objects[self.low].data.materials:
            bpy.data.objects[self.low].data.materials[0] = self.bake_material
        else:
            bpy.data.objects[self.low].data.materials.append(
                self.bake_material)

        self.bake_material.use_nodes = True
        nodes = self.bake_material.node_tree.nodes
        bake_node = nodes.new('ShaderNodeTexImage')
        bake_node.select = True

        self.bake_image = bpy.data.images.new(
            self.low + str(uuid.uuid4()),
            width=bpy.context.scene.output_size,
            height=bpy.context.scene.output_size)
        bake_node.image = self.bake_image

        bpy.data.objects[self.high].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[self.low]

    def bake(self):
        if (bpy.context.scene.bake_diffuse):
            self.bake_diffuse()
        if (bpy.context.scene.bake_normal):
            self.bake_normal()
        if (bpy.context.scene.bake_ao):
            self.bake_ao()

    def clean(self):
        bpy.data.objects[self.low].hide_render = True
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.images.remove(self.bake_image)
        bpy.data.materials.remove(self.bake_material)
        self.revert_original_settings()

    def setup_baking_settings(self):
        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.context.scene.render.bake.use_selected_to_active = True
        bpy.context.scene.render.bake.use_cage = bpy.context.scene.use_cages
        if bpy.context.scene.use_cages:
            bpy.context.scene.render.bake.cage_object = bpy.data.objects[
                self.low + '_cage']

    def bake_diffuse(self):
        self.setup_baking_settings()
        bpy.ops.object.bake(type='DIFFUSE')

        self.bake_image.filepath_raw = bpy.context.scene.bake_out_path + self.low + '_diffuse.tif'
        self.bake_image.file_format = bpy.context.scene.output_format
        self.bake_image.save()

    def bake_normal(self):
        self.setup_baking_settings()
        bpy.ops.object.bake(type='NORMAL')

        self.bake_image.filepath_raw = bpy.context.scene.bake_out_path + self.low + '_normal.tif'
        self.bake_image.file_format = bpy.context.scene.output_format
        self.bake_image.save()

    def bake_ao(self):
        bpy.context.scene.cycles.samples = bpy.context.scene.ao_samples
        bpy.ops.object.bake(type='AO')

        self.bake_image.filepath_raw = bpy.context.scene.bake_out_path + self.low + '_ao.tif'
        self.bake_image.file_format = bpy.context.scene.output_format
        # TODO save as bw image
        self.bake_image.save()

    def remember_original_settings(self):
        self.original_samples = bpy.context.scene.cycles.samples
        self.original_render_engine = bpy.data.scenes[
            bpy.context.scene.name].render.engine
        if len(bpy.data.objects[self.low].data.materials):
            self.original_material = bpy.data.objects[
                self.low].data.materials[0]
        else:
            self.original_material = None

    def revert_original_settings(self):
        bpy.data.scenes[
            bpy.context.scene.name].render.engine = self.original_render_engine
        if self.original_material:
            bpy.data.objects[
                self.low].data.materials[0] = self.original_material
        bpy.context.scene.cycles.samples = self.original_samples
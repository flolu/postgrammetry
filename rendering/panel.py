import bpy


class RenderPanel(bpy.types.Panel):
    bl_label = 'Rendering'
    bl_idname = 'MAIN_PT_batch_renderer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Postgrammetry'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator('postgrammetry.render_setup', text='Setup')
        layout.separator()

        # render settings
        row = layout.row()
        row.prop(bpy.context.scene.cycles, 'samples')
        row = layout.row()
        row.prop(bpy.context.scene.render, 'resolution_x')
        row.prop(bpy.context.scene.render, 'resolution_y')
        row = layout.row()
        row.prop(bpy.context.scene.render, 'resolution_percentage')

        row = layout.row()
        row.prop(bpy.context.scene, 'render_contrast', text='Contrast')
        row = layout.row()
        row.prop(bpy.context.scene, 'render_saturation', text='Saturation')

        row = layout.row()
        row.prop(context.scene, 'render_env_texture', text='HDRI')
        row = layout.row()
        row.prop(context.scene, 'render_bg_strength', text='Strength')
        row = layout.row()
        # TODO use 'postgrammetry_properties.<someting>' too (may also be easier to unregister addon)
        row.prop(context.scene.sun_pos_properties, 'hdr_azimuth')

        # modes
        row = layout.row()
        row.label(text='Modes')
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'render_full',
                 icon='SHADING_RENDERED', text='Full Still')

        row = col.row(align=True)
        row.prop(context.scene, 'render_texture_maps',
                 icon='TEXTURE', text='Texture Maps')

        row = col.row(align=True)
        row.prop(context.scene, 'render_matcap',
                 icon='OUTLINER_OB_META', text='Matcap')

        row = col.row(align=True)
        row.prop(context.scene, 'render_uv_grid',
                 icon='UV_DATA', text='UV Grid')
        row = col.row(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'render_uv_layout',
                 icon='UV_FACESEL', text='UV Layout')
        row = col.row(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'render_wireframe',
                 icon='SHADING_WIRE', text='Wireframe')
        if bpy.context.scene.render_wireframe:
            row.prop(context.scene,
                     'render_wireframe_look_for_lods',
                     text='Search LODs')

        row = col.row(align=True)
        row.prop(context.scene, 'render_turntable',
                 icon='FILE_REFRESH', text='Turntable')
        if bpy.context.scene.render_turntable:
            row.prop(context.scene, 'turntable_image_count',
                     text='Count')
            row = layout.row()
            row.prop(context.scene, 'render_turntable_rotation',
                     text='Preview Rotation')

        # background modes
        row = layout.row()
        row.label(text='Backgrounds')
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, 'render_transparent',
                 icon='TEXTURE', text='Transparent')
        row = col.row(align=True)
        row.prop(context.scene, 'render_black_bg',
                 icon='COLORSET_16_VEC', text='Black')
        row = col.row(align=True)
        row.prop(context.scene, 'render_white_bg',
                 icon='SNAP_FACE', text='White')
        row = col.row(align=True)

        layout.separator()

        # output
        row = layout.column()
        row.prop(context.scene, 'render_out_path', text='')

        # button
        row = layout.row()
        row.operator('postgrammetry.render_open_directory',
                     text='Open directory')
        row.operator('postgrammetry.render', text='Render')

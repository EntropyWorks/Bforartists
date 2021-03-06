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
from bpy.types import Menu, Panel


class RENDER_MT_presets(Menu):
    bl_label = "Render Presets"
    preset_subdir = "render"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class RENDER_MT_ffmpeg_presets(Menu):
    bl_label = "FFMPEG Presets"
    preset_subdir = "ffmpeg"
    preset_operator = "script.python_file_run"
    draw = Menu.draw_preset


class RENDER_MT_framerate_presets(Menu):
    bl_label = "Frame Rate Presets"
    preset_subdir = "framerate"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class RenderButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene and (scene.render.engine in cls.COMPAT_ENGINES)

class RENDER_PT_render(RenderButtonsPanel, Panel):
    bl_label = "Renderer Options"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        split = layout.split(percentage=0.33)

        split.label(text="Display:")
        row = split.row(align=True)
        row.prop(rd, "display_mode", text="")
        row.prop(rd, "use_lock_interface", icon_only=True)



class RENDER_PT_dimensions(RenderButtonsPanel, Panel):
    bl_label = "Dimensions"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    _frame_rate_args_prev = None
    _preset_class = None

    @staticmethod
    def _draw_framerate_label(*args):
        # avoids re-creating text string each draw
        if RENDER_PT_dimensions._frame_rate_args_prev == args:
            return RENDER_PT_dimensions._frame_rate_ret

        fps, fps_base, preset_label = args

        if fps_base == 1.0:
            fps_rate = round(fps)
        else:
            fps_rate = round(fps / fps_base, 2)

        # TODO: Change the following to iterate over existing presets
        custom_framerate = (fps_rate not in {23.98, 24, 25, 29.97, 30, 50, 59.94, 60})

        if custom_framerate is True:
            fps_label_text = "Custom (%r fps)" % fps_rate
            show_framerate = True
        else:
            fps_label_text = "%r fps" % fps_rate
            show_framerate = (preset_label == "Custom")

        RENDER_PT_dimensions._frame_rate_args_prev = args
        RENDER_PT_dimensions._frame_rate_ret = args = (fps_label_text, show_framerate)
        return args

    @staticmethod
    def draw_framerate(sub, rd):
        if RENDER_PT_dimensions._preset_class is None:
            RENDER_PT_dimensions._preset_class = bpy.types.RENDER_MT_framerate_presets

        args = rd.fps, rd.fps_base, RENDER_PT_dimensions._preset_class.bl_label
        fps_label_text, show_framerate = RENDER_PT_dimensions._draw_framerate_label(*args)

        sub.menu("RENDER_MT_framerate_presets", text=fps_label_text)

        if show_framerate:
            sub.prop(rd, "fps")
            sub.prop(rd, "fps_base", text="/")

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        rd = scene.render

        row = layout.row(align=True)
        row.menu("RENDER_MT_presets", text=bpy.types.RENDER_MT_presets.bl_label)
        row.operator("render.preset_add", text="", icon='ZOOMIN')
        row.operator("render.preset_add", text="", icon='ZOOMOUT').remove_active = True

        split = layout.split()

        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Resolution:")
        sub.prop(rd, "resolution_x", text="X")
        sub.prop(rd, "resolution_y", text="Y")
        sub.prop(rd, "resolution_percentage", text="")

        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Frame Range:")
        sub.prop(scene, "frame_start")
        sub.prop(scene, "frame_end")

        self.draw_framerate(sub, rd)

        ############## Subtab #####################
        
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["bforartists_UI_flags"].preferences

        if not addon_prefs.SP_render_dimensions_options:
            layout.prop(addon_prefs,"SP_render_dimensions_options", emboss=False, icon="TRIA_RIGHT", text="- Advanced -")

        else:
            layout.prop(addon_prefs,"SP_render_dimensions_options", emboss=False, icon="TRIA_DOWN", text="+ Advanced +")
            
            split = layout.split()

            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Aspect Ratio:")
            sub.prop(rd, "pixel_aspect_x", text="X")
            sub.prop(rd, "pixel_aspect_y", text="Y")

            row = col.row()
            row.prop(rd, "use_border", text="Border")
            sub = row.row()
            sub.active = rd.use_border
            sub.prop(rd, "use_crop_to_border", text="Crop")

            col = split.column()
            sub = col.column(align=True)
            sub.prop(scene, "frame_step")         

            subrow = sub.row(align=True)
            subrow.label(text="Time Remapping:")
            subrow = sub.row(align=True)
            subrow.prop(rd, "frame_map_old", text="Old")
            subrow.prop(rd, "frame_map_new", text="New")


class RENDER_PT_antialiasing(RenderButtonsPanel, Panel):
    bl_label = "Anti-Aliasing"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw_header(self, context):
        rd = context.scene.render

        self.layout.prop(rd, "use_antialiasing", text="")

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        layout.active = rd.use_antialiasing

        split = layout.split()

        col = split.column()
        col.row().prop(rd, "antialiasing_samples", expand=True)
        sub = col.row()
        sub.prop(rd, "use_full_sample")

        col = split.column()
        col.prop(rd, "pixel_filter_type", text="")
        col.prop(rd, "filter_size", text="Size")


class RENDER_PT_motion_blur(RenderButtonsPanel, Panel):
    bl_label = "Sampled Motion Blur"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return not rd.use_full_sample and (rd.engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        rd = context.scene.render

        self.layout.prop(rd, "use_motion_blur", text="")

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        layout.active = rd.use_motion_blur

        row = layout.row()
        row.prop(rd, "motion_blur_samples")
        row.prop(rd, "motion_blur_shutter")


class RENDER_PT_shading(RenderButtonsPanel, Panel):
    bl_label = "Shading"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        split = layout.split()

        col = split.column()
        col.prop(rd, "use_textures", text="Textures")
        col.prop(rd, "use_shadows", text="Shadows")
        col.prop(rd, "use_sss", text="Subsurface Scattering")
        
        col = split.column()
        col.prop(rd, "use_envmaps", text="Environment Map")
        col.prop(rd, "use_raytrace", text="Ray Tracing")
        col.prop(rd, "use_world_space_shading", text="World Space Shading")


class RENDER_PT_performance(RenderButtonsPanel, Panel):
    bl_label = "Performance"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Threads:")
        col.row(align=True).prop(rd, "threads_mode", expand=True)
        sub = col.column(align=True)
        sub.enabled = rd.threads_mode == 'FIXED'
        sub.prop(rd, "threads")

        col.label(text="Tile Size:")
        col.prop(rd, "tile_x", text="X")
        col.prop(rd, "tile_y", text="Y")

        col.separator()
        col.prop(rd, "preview_start_resolution")
        col.prop(rd, "preview_pixel_size", text="")

        col = split.column()
        col.label(text="Memory:")
        sub = col.column()
        sub.enabled = not rd.use_full_sample
        sub.prop(rd, "use_save_buffers")
        sub = col.column()
        sub.active = rd.use_compositing
        sub.prop(rd, "use_free_image_textures")
        sub = col.column()
        sub.active = rd.use_raytrace
        sub.label(text="Acceleration Structure:")
        sub.prop(rd, "raytrace_method", text="")
        if rd.raytrace_method == 'OCTREE':
            sub.prop(rd, "octree_resolution", text="Resolution")
        else:
            sub.prop(rd, "use_instances", text="Instances")
        sub.prop(rd, "use_local_coords", text="Local Coordinates")


class RENDER_PT_post_processing(RenderButtonsPanel, Panel):
    bl_label = "Post Processing"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        split = layout.split()

        col = split.column()
        col.prop(rd, "use_compositing")
        col.prop(rd, "use_sequencer")

        split.prop(rd, "dither_intensity", text="Dither", slider=True)

        
        ############## Subtab #####################
        
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["bforartists_UI_flags"].preferences

        if not addon_prefs.SP_render_postpro_BI_options:
            layout.prop(addon_prefs,"SP_render_postpro_BI_options", emboss=False, icon="TRIA_RIGHT", text="- Advanced -")

        else:
            layout.prop(addon_prefs,"SP_render_postpro_BI_options", emboss=False, icon="TRIA_DOWN", text="+ Advanced +")

            split = layout.split()

            col = split.column()
            col.prop(rd, "use_fields", text="Fields")
            sub = col.column()
            sub.active = rd.use_fields
            sub.row().prop(rd, "field_order", expand=True)
            sub.prop(rd, "use_fields_still", text="Still")

            col = split.column()
            col.prop(rd, "use_edge_enhance")
            sub = col.column()
            sub.active = rd.use_edge_enhance
            sub.prop(rd, "edge_threshold", text="Threshold", slider=True)
            sub.prop(rd, "edge_color", text="")


class RENDER_PT_stamp(RenderButtonsPanel, Panel):
    bl_label = "Metadata"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        layout.prop(rd, "use_stamp")

        ############## Subtab #####################
        
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["bforartists_UI_flags"].preferences

        if not addon_prefs.SP_render_metadata_stampoptions:
            layout.prop(addon_prefs,"SP_render_metadata_stampoptions", emboss=False, icon="TRIA_RIGHT", text="- Stamp Options -")

        else:
            layout.prop(addon_prefs,"SP_render_metadata_stampoptions", emboss=False, icon="TRIA_DOWN", text="+ Stamp Options +") 

            col = layout.column()
            col.active = rd.use_stamp
            row = col.row()
            row.prop(rd, "stamp_font_size", text="Font Size")
            row.prop(rd, "use_stamp_labels", text="Draw labels")

            row = col.row()
            row.column().prop(rd, "stamp_foreground", slider=True)
            row.column().prop(rd, "stamp_background", slider=True)

        ############## Subtab #####################
        
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["bforartists_UI_flags"].preferences

        if not addon_prefs.SP_render_metadata_enabled:
            layout.prop(addon_prefs,"SP_render_metadata_enabled", emboss=False, icon="TRIA_RIGHT", text="- Enabled Metadata -")

        else:
            layout.prop(addon_prefs,"SP_render_metadata_enabled", emboss=False, icon="TRIA_DOWN", text="+ Enabled Metadata +") 

            layout.label("Enabled Metadata")
            split = layout.split()

            col = split.column()
            col.prop(rd, "use_stamp_time", text="Time")
            col.prop(rd, "use_stamp_date", text="Date")
            col.prop(rd, "use_stamp_render_time", text="RenderTime")
            col.prop(rd, "use_stamp_frame", text="Frame")
            col.prop(rd, "use_stamp_scene", text="Scene")
            col.prop(rd, "use_stamp_memory", text="Memory")

            col = split.column()
            col.prop(rd, "use_stamp_camera", text="Camera")
            col.prop(rd, "use_stamp_lens", text="Lens")
            col.prop(rd, "use_stamp_filename", text="Filename")
            col.prop(rd, "use_stamp_marker", text="Marker")
            col.prop(rd, "use_stamp_sequencer_strip", text="Seq. Strip")

        row = layout.split(percentage=0.2)
        row.prop(rd, "use_stamp_note", text="Note")
        sub = row.row()
        sub.active = rd.use_stamp_note
        sub.prop(rd, "stamp_note_text", text="")
        if rd.use_sequencer:
            layout.label("Sequencer:")
            layout.prop(rd, "use_stamp_strip_meta")


class RENDER_PT_output(RenderButtonsPanel, Panel):
    bl_label = "Output"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER', 'CYCLES'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        image_settings = rd.image_settings
        file_format = image_settings.file_format

        layout.prop(rd, "filepath", text="")

        ############## Subtab #####################
        
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["bforartists_UI_flags"].preferences

        if not addon_prefs.SP_render_output_options:
            layout.prop(addon_prefs,"SP_render_output_options", emboss=False, icon="TRIA_RIGHT", text="- Options -")

        else:
            layout.prop(addon_prefs,"SP_render_output_options", emboss=False, icon="TRIA_DOWN", text="+ Options +")

            split = layout.split()

            col = split.column()
            col.active = not rd.is_movie_format
            col.prop(rd, "use_overwrite")
            col.prop(rd, "use_placeholder")

            col = split.column()
            col.prop(rd, "use_file_extension")
            col.prop(rd, "use_render_cache")

        layout.template_image_settings(image_settings, color_management=False)

        ##### Cycles or BI transparency settings for background ##########

        scene = context.scene      
        if scene.render.engine == 'CYCLES':
        
            ## Cycles transparent background.
            scene = context.scene
            cscene = scene.cycles 
            
            #split = layout.split()

            #col = split.column()
            layout.prop(cscene, "film_transparent", text = "Transparent Background")
            sub = layout.row()
            sub.prop(cscene, "film_transparent_glass", text="Transparent Glass")
            sub.active = cscene.film_transparent
            sub = layout.row()
            sub.prop(cscene, "film_transparent_roughness", text="Roughness Threshold")
            sub.active = cscene.film_transparent and cscene.film_transparent_glass
            
        else:
        
            ## BI transparent background  
            layout.prop(rd, "alpha_mode", text="Transparency")

        ##################################################################

        if rd.use_multiview:
            layout.template_image_views(image_settings)


class RENDER_PT_encoding(RenderButtonsPanel, Panel):
    bl_label = "Encoding"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return rd.image_settings.file_format in {'FFMPEG', 'XVID', 'H264', 'THEORA'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        ffmpeg = rd.ffmpeg

        layout.menu("RENDER_MT_ffmpeg_presets", text="Presets")

        split = layout.split()
        split.prop(rd.ffmpeg, "format")
        split.prop(ffmpeg, "use_autosplit")

        layout.separator()

        needs_codec = ffmpeg.format in {'AVI', 'QUICKTIME', 'MKV', 'OGG', 'MPEG4'}
        if needs_codec:
            layout.prop(ffmpeg, "codec")

        if ffmpeg.codec in {'DNXHD'}:
            layout.prop(ffmpeg, "use_lossless_output")

        # Output quality
        if needs_codec and ffmpeg.codec in {'H264', 'MPEG4'}:
            layout.prop(ffmpeg, "constant_rate_factor")

        # Encoding speed
        layout.prop(ffmpeg, "ffmpeg_preset")
        # I-frames
        layout.prop(ffmpeg, "gopsize")
        # B-Frames
        row = layout.row()
        row.prop(ffmpeg, "use_max_b_frames", text="Max B-frames")
        pbox = row.split()
        pbox.prop(ffmpeg, "max_b_frames", text="")
        pbox.enabled = ffmpeg.use_max_b_frames

        if ffmpeg.constant_rate_factor == 'NONE':
            split = layout.split()
            col = split.column()
            col.label(text="Rate:")
            col.prop(ffmpeg, "video_bitrate")
            col.prop(ffmpeg, "minrate", text="Minimum")
            col.prop(ffmpeg, "maxrate", text="Maximum")
            col.prop(ffmpeg, "buffersize", text="Buffer")

            col = split.column()
            col.label(text="Mux:")
            col.prop(ffmpeg, "muxrate", text="Rate")
            col.prop(ffmpeg, "packetsize", text="Packet Size")

        layout.separator()

        # Audio:
        if ffmpeg.format != 'MP3':
            layout.prop(ffmpeg, "audio_codec", text="Audio Codec")

        if ffmpeg.audio_codec != 'NONE':
            row = layout.row()
            row.prop(ffmpeg, "audio_bitrate")
            row.prop(ffmpeg, "audio_volume", slider=True)



classes = (
    RENDER_MT_presets,
    RENDER_MT_ffmpeg_presets,
    RENDER_MT_framerate_presets,
    RENDER_PT_render,
    RENDER_PT_dimensions,
    RENDER_PT_antialiasing,
    RENDER_PT_motion_blur,
    RENDER_PT_shading,
    RENDER_PT_performance,
    RENDER_PT_post_processing,
    RENDER_PT_stamp,
    RENDER_PT_output,
    RENDER_PT_encoding,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

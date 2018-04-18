bl_info = {
    "name": "Wireframe on shaded",
    "description": "Press 'F4' to toggle all-edges wireframe on objects in scene",
    "author": "Jonathan Williamson, Oliver Lockwood, Javier Pintor, Benjamin Sauder",
    "version": (0, 1),
    "category": "3D View",
    }
 
import bpy
from bpy.app.handlers import persistent

selection = None

# very minial operator to toggle the wiredisplay
class toggleObjectEdgesWiresDisplay(bpy.types.Operator):
    """Toggle Wire Display With All Edges"""
    bl_label = "Wireframe on shaded"
    bl_idname = "object.toggle_objects_edges_wire"
    bl_description = "Toggle all-edges wireframe on objects in scene"
    
    def execute(self, context):
        context.scene.wire_toggle_state = not context.scene.wire_toggle_state
        return {"FINISHED"} 


# utility
def set_wire_state(objects, state):
    for obj in objects:

        if obj.wire_override_setting:
            continue
        
        obj.show_wire = state
        obj.show_all_edges = state

# the main function, keeps track of selection changes and user actions
last_wire_toggle_state = None
last_wire_on_selected_state = None

@persistent
def scene_update_handler(scene):
    global selection, last_wire_toggle_state, last_wire_on_selected_state
    
    # update wire drawing on all objects 
    if (last_wire_toggle_state != scene.wire_toggle_state or 
       last_wire_on_selected_state != scene.wire_on_selected):
        #print ("update wire state state: %s" %(scene.wire_toggle_state))

        for obj in scene.objects:
            if obj.wire_override_setting:
                continue

            if scene.wire_on_selected:    		
                obj.show_wire = obj.select and scene.wire_toggle_state
                obj.show_all_edges = obj.select and scene.wire_toggle_state
            else:
                obj.show_wire = scene.wire_toggle_state
                obj.show_all_edges = scene.wire_toggle_state

        last_wire_toggle_state = scene.wire_toggle_state
        last_wire_on_selected_state = scene.wire_on_selected
   
    if not scene.wire_on_selected or not scene.wire_toggle_state:
        return 

    # initialize if no selection ever happend
    if selection == None:
        selection = bpy.context.selected_objects       
        set_wire_state(selection, True and scene.wire_toggle_state)
        return    

    # update wire drawing on selection change
    if selection != bpy.context.selected_objects:
        set_wire_state(selection, False and scene.wire_toggle_state)
        selection = bpy.context.selected_objects 
       
        set_wire_state(selection, True and scene.wire_toggle_state)

# UI extensions
def display_extension(self,context):
    obj = context.object
    
    obj_type = obj.type
    is_geometry = (obj_type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'})    
    is_dupli = (obj.dupli_type != 'NONE')
    
    layout = self.layout    
    row = layout.row()
    
    if is_geometry or is_dupli:
        row.prop(obj, "wire_override_setting", text="Override Wire Drawing")


def view3d_display_extension(self,context):        
    obj = context.object
    
    layout = self.layout    
    row = layout.row()
    
    row.prop(bpy.context.scene, "wire_toggle_state", text="Wireframe")
    row = layout.row()
    row.active = bpy.context.scene.wire_toggle_state
    row.prop(bpy.context.scene, "wire_on_selected", text="Wireframe On Selected")


# property change handlers
def update_wire_selected(self, context):
    if context.scene.wire_on_selected: 
        set_wire_state(context.scene.objects, False)


# register / unregister in blender
addon_keymaps = []

def register():
	# register classes
    bpy.utils.register_class(toggleObjectEdgesWiresDisplay)
 
 	# register callbacks
    bpy.app.handlers.scene_update_post.append(scene_update_handler)

    # register properties
    bpy.types.Scene.wire_toggle_state = bpy.props.BoolProperty(
    name = "wire_toggle_state",
    default = False)    

    bpy.types.Scene.wire_on_selected = bpy.props.BoolProperty(
    name = "wire_on_selected",
    default = False,
    update = update_wire_selected)

    bpy.types.Object.wire_override_setting = bpy.props.BoolProperty(
    name = "wire_override_setting",
    default = False)    

    # extend default UI
    bpy.types.OBJECT_PT_display.prepend(display_extension)
    bpy.types.VIEW3D_PT_view3d_display.prepend(view3d_display_extension)

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.toggle_objects_edges_wire', 'F4', 'PRESS')
    addon_keymaps.append((km, kmi))


def unregister():
	# unregister classes
    bpy.utils.unregister_class(toggleObjectEdgesWiresDisplay)
    
    # unregister callbacks
    bpy.app.handlers.scene_update_post.remove(scene_update_handler)

    # cleanup properties
    del bpy.types.Scene.wire_toggle_state
    del bpy.types.Scene.wire_on_selected
    del bpy.types.Object.wire_override_setting

    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
bl_info = {
    "name": "Wireframe on shaded",
    "description": "Press 'F4' to toggle all-edges wireframe on selected objects in scene",
    "author": "Jonathan Williamson, Oliver Lockwood, Javier Pintor, Benjamin Sauder",
    "version": (0, 1),
    "category": "3D View",
    }
 
import bpy

selection = None
only_selected = True
toggle_mode = True
 
class allObjectsEdgesWire(bpy.types.Operator):
    """Toggle Wire Display With All Edges"""
    bl_label = "Wireframe on shaded"
    bl_idname = "object.selected_objects_edges_wire"
    bl_description = "Toggle all-edges wireframe on selected objects in scene"
    
    def execute(self, context):
        global toggle_mode
        
        toggle = toggle_mode
        
        objects = context.scene.objects 
        if only_selected:
            objects = selection
        
        toggle = not context.active_object.show_wire
        
        #for obj in objects:
        #    toggle |= not obj.show_wire
            
        for obj in objects:
            obj.show_wire = toggle
            obj.show_all_edges = toggle
            
            
        toggle_mode = toggle
        return {"FINISHED"}


def set_wire_state(state):
    for obj in selection:
        obj.show_wire = state
        obj.show_all_edges = state


def scene_update_handler(scene):
    global selection, toggle_mode, only_selected
    
    if not toggle_mode or not only_selected:
        return 
    
    if selection == None:
        selection = bpy.context.selected_objects
        set_wire_state(True)
        return    
    
    if selection != bpy.context.selected_objects:
        set_wire_state(False)
        selection = bpy.context.selected_objects 
        set_wire_state(True)

addon_keymaps = []
 
def register():
    bpy.utils.register_class(allObjectsEdgesWire)
 
    bpy.app.handlers.scene_update_post.append(scene_update_handler)

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.selected_objects_edges_wire', 'F4', 'PRESS')
    addon_keymaps.append((km, kmi))
 
def unregister():
    bpy.utils.unregister_class(allObjectsEdgesWire)
    bpy.app.handlers.scene_update_post.remove(scene_update_handler)
    
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
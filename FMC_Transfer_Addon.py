bl_info = {
    "name" : "FMC Transfer",
    "author" : "Mean Michael",
    "version" : (1, 0),
    "blender" : (3, 5, 1),
    "location" : "View3d > Tool",
    "description" : "Attaches a transfer rig to the Free Mocap empties",
    "warning" : "Requires the transfer rig from the GitHub URL",
    "wiki_url" : "https://github.com/MeansModels/Mocap-Transfer-Rig",
    "category" : "Rigging",
}

import bpy

class ARMATURE_OT_FMC_Transfer(bpy.types.Operator):
    """Transfers the rig to the empties"""
    bl_idname = "armature.fmc_transfer"
    bl_label = "FMC Transfer"

    #Bone Functions


    def rightLeft(arm, bone, base, target, pole):
        
        #Right side
            
        targetR = "right_" + target
                
        baseR = "right_" + base
                
        boneR = bone + ".R"
        
        #For bones without pole targets. Alows a None input
        poleR = pole
        
        if pole != None:        

            poleR = pole + ".R"

        
        ARMATURE_OT_FMC_Transfer.conSelect(arm, boneR, targetR, baseR, poleR)

            
        #left side
                    
        targetL = "left_" + target
                    
        baseL = "left_" + base
                    
        boneL = bone + ".L"
        
        #For bones without pole targets. Alows a None input
        poleL = pole
                
        if pole != None:
            
            poleL = pole + ".L"
                
        
        ARMATURE_OT_FMC_Transfer.conSelect(arm, boneL, targetL, baseL, poleL)
        

    #Base is the head of the bone, target is the tail and the IK target.
    def IK(arm, bone, conObj, base, target, pole):            
        
        #Get bone for edit mode
        boneE = bpy.data.armatures[arm].edit_bones[bone]
        
        #Get empty object
        emTarget = bpy.data.objects[target]
        
        emBase = bpy.data.objects[base]
        
        #Set bone tail to empty location
        boneE.tail = emTarget.location
        
        boneE.head = emBase.location
        
        #Set bone constraint target to empty
        conObj.target = emTarget
        
        if pole != None:
        
            poleObj = bpy.data.objects[pole]
            
            conObj.pole_target = poleObj
     
     
    #Base is the head of the bone, target is the target of the location constraint
    #PointTo is the TrackTo target
    def nonIK(arm, bone, conObj, base, target, pointTo):
        
        #Get bone for edit mode
        boneE = bpy.data.armatures[arm].edit_bones[bone]
        
        #Get empty object
        emTarget = bpy.data.objects[target]
        
        emPoint = bpy.data.objects[pointTo]
        
        emBase = bpy.data.objects[base]
        
        #Set bone constraint target to empty
        conObj.target = emPoint
        
        #Set bone tail to empty location
        boneE.tail = emTarget.location
        
        boneE.head = emBase.location
        
        if abs((boneE.tail - boneE.head).magnitude) < .001:
        
            boneE.tail.z += .2
            
            
            
    #Checks the constraint of the selected bone, and runs the according function
    def conSelect(arm, bone, target, base, pole):
        
        conArray = bpy.data.objects[arm].pose.bones[bone].constraints
        
        for conObj in conArray:
        
            if conObj.type == "IK":   
            
                ARMATURE_OT_FMC_Transfer.IK(arm, bone, conObj, base, target, pole)
            
            elif conObj.type == "COPY_LOCATION":
            
                ARMATURE_OT_FMC_Transfer.nonIK(arm, bone, conObj, base, base, base)
            
            elif conObj.type == "TRACK_TO":
                
                ARMATURE_OT_FMC_Transfer.nonIK(arm, bone, conObj, base, base, target)
                
                
    #Object functions


    def geoNodes(nodeGroup, top, bottom, joint):
        
        nodeGroupL = nodeGroup + ".L"
        
        topL = "left_" + top
        
        bottomL = "left_" + bottom
        
        jointL = "left_" + joint
        
        bpy.data.node_groups[nodeGroupL].nodes["Top Tracker"].inputs[0].default_value = bpy.data.objects[topL]
        
        bpy.data.node_groups[nodeGroupL].nodes["Bottom Tracker"].inputs[0].default_value = bpy.data.objects[bottomL]
        
        bpy.data.node_groups[nodeGroupL].nodes["Joint Tracker"].inputs[0].default_value = bpy.data.objects[jointL]
        
        
        nodeGroupR = nodeGroup + ".R"
        
        topR = "right_" + top
        
        bottomR = "right_" + bottom
        
        jointR = "right_" + joint
        
        bpy.data.node_groups[nodeGroupR].nodes["Top Tracker"].inputs[0].default_value = bpy.data.objects[topR]
        
        bpy.data.node_groups[nodeGroupR].nodes["Bottom Tracker"].inputs[0].default_value = bpy.data.objects[bottomR]
        
        bpy.data.node_groups[nodeGroupR].nodes["Joint Tracker"].inputs[0].default_value = bpy.data.objects[jointR]
                
                

    def execute(self, context):

        #Toggle Edit Mode
        bpy.ops.object.mode_set(mode = "EDIT")


        arm = "Tracking Armature"

        #Upper Arm
        ARMATURE_OT_FMC_Transfer.rightLeft(arm, "Upper Arm", "shoulder", "elbow", "ElbowMesh")

        #Lower Arm
        ARMATURE_OT_FMC_Transfer.rightLeft(arm, "Lower Arm", "elbow", "wrist", "ElbowMesh")

        #upper Leg
        ARMATURE_OT_FMC_Transfer.rightLeft(arm, "Upper Leg", "hip", "knee", "KneeMesh")

        #Lower Leg
        ARMATURE_OT_FMC_Transfer.rightLeft(arm, "Lower Leg", "knee", "ankle", "KneeMesh")

        #Head
        ARMATURE_OT_FMC_Transfer.conSelect(arm, "Head", "nose", "head_center", None)

        #Neck
        ARMATURE_OT_FMC_Transfer.conSelect(arm, "Neck", "head_center", "neck_center", None)

        #Shoulder Rotation
        ARMATURE_OT_FMC_Transfer.conSelect(arm, "Shoulder Rotation", "neck_center", "neck_center", None)

        #Upper Torso
        ARMATURE_OT_FMC_Transfer.conSelect(arm, "Upper Torso", "neck_center", "trunk_center", None)

        #Torso
        torsoCon = bpy.data.objects[arm].pose.bones["Torso"].constraints["Track To The Right Hip Empty"]

        ARMATURE_OT_FMC_Transfer.nonIK(arm, "Torso", torsoCon, "hips_center", "trunk_center", "right_hip")

        #Hip Rotation
        ARMATURE_OT_FMC_Transfer.conSelect(arm, "Hip Rotation", "right_hip", "hips_center", None)

        #Location Reference For Driver
        ARMATURE_OT_FMC_Transfer.conSelect(arm, "Location Reference For Driver", "hips_center", "hips_center", None)

        #Target for Leg Local Location
        ARMATURE_OT_FMC_Transfer.rightLeft(arm, "Target for Leg Local Location", "ankle", "ankle", None)



        #Geometry Node target assignment
        ARMATURE_OT_FMC_Transfer.geoNodes("Elbow", "shoulder", "wrist", "elbow")

        ARMATURE_OT_FMC_Transfer.geoNodes("Knee", "hip", "ankle", "knee")


        #Object consraint tartget assingment
        locConObj = bpy.data.objects["Hip Direction For Pole Targets"].constraints["Copy Location Of the Hip Center"]

        trkConObj = bpy.data.objects["Hip Direction For Pole Targets"].constraints["Track To The Right Upper Leg"]

        locTgt = bpy.data.objects["hips_center"]

        trkTgt = bpy.data.objects["right_hip"]

        locConObj.target = locTgt

        trkConObj.target = trkTgt

        #Toggle Opbect Mode
        bpy.ops.object.mode_set(mode = "OBJECT")
        
        return{"FINISHED"}



class FMC_Transfer_Panel(bpy.types.Panel):
    bl_label = "FMC Transfer"
    bl_idname = "PT_FMC_Transfer_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FMC Transfer"

    def draw(self, context):
        
        row = self.layout.row()
        row.label(text = "Import Tracking Objects collection")
        
        row = self.layout.row()
        row.label(text = "from the Transfer Rig.blend file")
        
        row = self.layout.row()
        row.label(text = "Then press the big button", icon = "TRIA_DOWN")
        
        row = self.layout.row()
        row.operator("armature.fmc_transfer", icon = "ARMATURE_DATA")



def register():
    
    bpy.utils.register_class(ARMATURE_OT_FMC_Transfer)
    
    bpy.utils.register_class(FMC_Transfer_Panel)
    
def unregister():
    
    bpy.utils.unregister_class(ARMATURE_OT_FMC_Transfer)
    
    bpy.utils.unregister_class(FMC_Transfer_Panel)
    
if __name__ == "__main__":
    register()
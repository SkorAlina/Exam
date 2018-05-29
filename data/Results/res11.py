import arcpy

fieldFacilities = arcpy.GetParameterAsText(0)
zipField = arcpy.GetParameterAsText(1)

try:
    arcpy.MakeFeatureLayer_management(fieldFacilities, "AllStatesLayer")
    arcpy.MakeFeatureLayer_management(fieldFacilities, "SelectionStateLayer", '"' + str(nameField) + '" =' + "'" + str(state) + "'")
    arcpy.SelectLayerByLocation_management("AllStatesLayer","BOUNDARY_TOUCHES","SelectionStateLayer",3000 meters)
    with arcpy.da.SearchCursor("AllStatesLayer", (nameField,)) as cursor:
        for row in cursor:
            print row[0]

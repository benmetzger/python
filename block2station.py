"""
This script will identify the closest station (shortest distance) for every block centroids
"""

# Import system modules
import arcpy, string
from arcpy import env
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("Network")

#Set environment settings
env.workspace = "Y:\\Documents\\GeoDecision\\road_network_model\\road_model\\road_model.gdb"
env.overwriteOutput = True

#Set local variables
inNetworkDataset = "road_network\\road_data"
outNALayerName = "ClosestStations"
impedanceAttribute = "Minutes"
accumulateAttributeName = ["Minutes"]
inFacilities = "stomping_station"
inIncidents = "block_centroid"
outLayerFile = "Y:\\Documents\\GeoDecision\\road_network_model\\road_model\\" + outNALayerName + ".lyr"


try:

    #Create a new closest facility analysis layer. Apart from finding the drive 
    #time to the closest warehouse, we also want to find the total distance. So
    #we will accumulate the "Meters" impedance attribute.
    outNALayer = arcpy.na.MakeClosestFacilityLayer(inNetworkDataset,outNALayerName,
                                                   impedanceAttribute,"TRAVEL_TO",
                                                   "",1, accumulateAttributeName,
                                                   "NO_UTURNS")
    
	
    #Get the layer object from the result object. The closest facility layer can 
    #now be referenced using the layer object.
    outNALayer = outNALayer.getOutput(0)
    
    #Get the names of all the sublayers within the closest facility layer.
    subLayerNames = arcpy.na.GetNAClassNames(outNALayer)
    #Stores the layer names that we will use later
    facilitiesLayerName = subLayerNames["Facilities"]
    incidentsLayerName = subLayerNames["Incidents"]
    
    #Load the stomping stations as Facilities using the default field mappings and 
    #search tolerance
    fieldMappings = arcpy.na.NAClassFieldMappings(outNALayer, facilitiesLayerName)
    fieldMappings["Name"].mappedFieldName = "ID"
    arcpy.na.AddLocations(outNALayer, facilitiesLayerName, inFacilities, fieldMappings, "")
    
    #Load the block centroids as Incidents. Map the Name property from the NOM field
    #using field mappings
    fieldMappings = arcpy.na.NAClassFieldMappings(outNALayer, incidentsLayerName)
    fieldMappings["Name"].mappedFieldName = "ORIG_FID"
    arcpy.na.AddLocations(outNALayer, incidentsLayerName, inIncidents,
                          fieldMappings,"")
    
    #Solve the closest facility layer
    arcpy.na.Solve(outNALayer)
    
    #Save the solved closest facility layer as a layer file on disk with 
    #relative paths
    arcpy.management.SaveToLayerFile(outNALayer,outLayerFile,"RELATIVE")
    
    arcpy.AddMessage("Script completed successfully")

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    arcpy.AddMessage("An error occured on line %i" % tb.tb_lineno)
    arcpy.AddMessage(str(e))
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# public.py
# Created on: 2017-05-26 10:03:25.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: public <mav_bcr_boundary_includ_ridg_nad15_wgs84_shp> <gdbMoistSoilLMVJV_DBO_WMU> <Workspace> <Public_shp> 
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, sys, getopt, logging
from arcpy.sa import *


# Required parameters
# Name for the feature classes within the geodatabase

publicinput = "Public_input_8_12_16"
arcpy.env.overwriteOutput = True;

def checkField (shp, field):
        fields = arcpy.ListFields(shp, field)
        if len(fields) !=1:
                return True
        else:
                return False

        
# Setup model specifics
def runPublic (region, workspace, gdb):
        logging.info('Running public model')
        logging.info('Public input: ' + publicinput)
	gdb = os.path.join(workspace, gdb)
	scratchgdb = os.path.join(workspace, region + "_scratch.gdb")
	aoi = os.path.join(gdb, region)


	#setup databases
	if not (os.path.exists(scratchgdb)):
                print("Creating scratch GDB")
		arcpy.CreateFileGDB_management(workspace, region + "_scratch.gdb")
	else:
                print("Scratch GDB already exists.  Using it")

        #check for setup files
        if not (arcpy.Exists(aoi)):
                print("Area of interest '" + aoi + "' does not exist")
                sys.exit(2)
        if not (arcpy.Exists(os.path.join(gdb, publicinput))):
                print("Public input '" + publicinput + "' does not exist")
                sys.exit(2)

        print "Processing public data"
        # Process: Clip
        pubaoi = arcpy.Clip_analysis(os.path.join(gdb, publicinput), aoi, "in_memory/pubaoi", "")

        # Process: Add Field
        arcpy.AddField_management(pubaoi, "OWNER", "TEXT", "", "", "20", "", "NULLABLE", "NON_REQUIRED", "")

        # Process: Calculate Field
        arcpy.CalculateField_management(pubaoi, "OWNER", "'PUBLIC'", "PYTHON_9.3", "")

        # Process: Feature Class to Feature Class
        arcpy.FeatureClassToFeatureClass_conversion(pubaoi, gdb, "Public_output_" + region , "", 'BCR_NAME \"BCR\" true true false 16 Text 0 0 ,First,#,"in_memory/pubaoi",BCR_NAME,-1,-1;STATE \"STATE\" true true false 2 Text 0 0 ,First,#,"in_memory/pubaoi",STATE,-1,-1;MANAGING_A \"Managing Agency\" true true false 35 Text 0 0 ,First,#,"in_memory/pubaoi",MANAGING_A,-1,-1;MANAGEMENT \"Management\" true true false 30 Text 0 0 ,First,#,"in_memory/pubaoi",MANAGEMENT,-1,-1;COMMON_NAM \"Common Name\" true true false 30 Text 0 0 ,First,#,"in_memory/pubaoi",COMMON_NAM,-1,-1;ACRES \"Acres\" true true false 8 Double 0 0 ,First,#,"in_memory/pubaoi",ACRES,-1,-1;HECTARES \"Hectares\" true true false 8 Double 0 0 ,First,#,"in_memory/pubaoi",HECTARES,-1,-1;HABITAT_TY \"Habitat Type\" true true false 16 Text 0 0 ,First,#,"in_memory/pubaoi",HABITAT_TY,-1,-1;COVER_TYPE \"Cover Type\" true true false 16 Text 0 0 ,First,#,"in_memory/pubaoi",COVER_TYPE,-1,-1;Z_HARVESTE \"Pct Harvested\" true true false 8 Double 0 0 ,First,#,"in_memory/pubaoi",Z_HARVESTE,-1,-1;Z_RED_OAK_ \"Pct Red Oak\" true true false 8 Double 0 0 ,First,#,"in_memory/pubaoi",Z_RED_OAK_,-1,-1;FUNCTIONAL \"Functional\" true true false 1 Text 0 0 ,First,#,"in_memory/pubaoi",FUNCTIONAL,-1,-1;DED \"Duck Energy Days\" true true false 8 Double 0 0 ,First,#,"in_memory/pubaoi",DED,-1,-1;WATERSHED \"WATERSHED\" true true false 45 Text 0 0 ,First,#,"in_memory/pubaoi",GAUGE,-1,-1;OWNER \"OWNER\" true true false 20 Text 0 0 ,First,#,"in_memory/pubaoi",OWNER,-1,-1', "")

        print "Processing complete"
        logging.info('Public model complete with outout: Public_output' + region) 

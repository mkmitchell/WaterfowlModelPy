# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Naturalflood.py
# Created on: 2017-05-23 07:55:04.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: Naturalflood <Workspace> <Flooding> <Crops> <WRP> <State> <Natural_flood_shp> <MAV> <WorkspaceGDB> 
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, sys, getopt, prepflood, logging
from arcpy.sa import *


# Required parameters
# Name for the feature classes within the geodatabase

crops = "CDL_2015"
stateboundary = "State_boundaries"
wrp = "WRP"
floodpct = 40
arcpy.env.overwriteOutput = True;

def checkField (shp, field):
        fields = arcpy.ListFields(shp, field)
        if len(fields) !=1:
                return True
        else:
                return False

        
# Setup model specifics
def runFlood (region, workspace, gdb):
        logging.info('Running natural flood model')
        logging.info('Crops: ' + crops)
        logging.info('WRP: ' + wrp)
        logging.info('Flood: ' + str(floodpct) + '%')
	gdb = os.path.join(workspace, gdb)
	scratchgdb = os.path.join(workspace, region + "_scratch.gdb")
	aoi = os.path.join(gdb, region)
        flood = "IF_" + region
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
        if not (arcpy.Exists(os.path.join(gdb, flood))):
                print("Flood dataset '" + flood + "' does not exist")
                sys.exit(2)
        if not (arcpy.Exists(os.path.join(gdb, stateboundary))):
                print("State boundaries '" + stateboundary + "' does not exist")
                sys.exit(2)
        if not (arcpy.Exists(os.path.join(gdb, wrp))):
                print("WRP dataset '" + wrp + "' does not exist")
                sys.exit(2)
        if not (arcpy.Exists(os.path.join(gdb, crops))):
                print("Crop dataset '" + crops + "' does not exist")
                sys.exit(2)


# Script arguments from ArcGIS.  Keeping these and setting them = to input parameters
        Workspace = gdb
        Flooding = os.path.join(gdb, flood)
        Crops = os.path.join(gdb, crops)
        WRP = os.path.join(gdb, wrp)
        State = os.path.join(gdb, stateboundary)
        WorkspaceGDB = scratchgdb
        try:
                if arcpy.CheckExtension("Spatial") == "Available":
                        arcpy.CheckOutExtension("Spatial")
                else:
                        print("Spatial analyst license not available")
                        sys.exit(2)
        except Exception, e:
                print("Can't acquire spatial analyst license: ", e)
                sys.exit(2)
        print "Starting analysis"
        rasCrop = Raster(Crops)
        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
        print "Configuring crop type"
        outCrop = Con((rasCrop == 1) | (rasCrop == 3) | (rasCrop == 4) | (rasCrop == 5) | (rasCrop == 29) | (rasCrop == 190), rasCrop, 0)
        print "Converting crop raster to polygon.  This can take a very long time"
        ############# SKIP
        polyCrop = arcpy.RasterToPolygon_conversion(outCrop, os.path.join(scratchgdb, "polyCrop"), "NO_SIMPLIFY", "Value")
        #print "Skipping polygon conversion for testing"
        #polyCrop = os.path.join(scratchgdb, "polyCrop")
        ############
        selectCrop = arcpy.Select_analysis(polyCrop, os.path.join(scratchgdb, "sltCrop"), "gridcode > 0")
        arcpy.AddField_management(selectCrop, "CLASS_NAME", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(selectCrop, "CLASS_NAME", "Calc( !gridcode!)", "PYTHON_9.3", "def Calc(grid):\\n  if (grid==1):\\n    return 'Corn'\\n  if (grid==3):\\n    return 'Rice'\\n  if (grid==4):\\n    return 'Sorghum'\\n  if (grid==5):\\n    return 'Soybeans'\\n  if (grid==29):\\n    return 'Millet'\\n  if (grid==190):\\n    return 'Woody Wetlands'")
        ###### Also skipping for speed and testing
        print "Import flood"
        prepflood.prepFlood(scratchgdb, floodpct, Flooding)
        Flooding = os.path.join(scratchgdb, "floodSetup")
        plyFlood = arcpy.RasterToPolygon_conversion(Raster(Flooding), os.path.join(scratchgdb, "flooding"), "NO_SIMPLIFY", "VALUE")
        #plyFlood = os.path.join(scratchgdb, "flooding")
        selectFlood = arcpy.Select_analysis(plyFlood, os.path.join(scratchgdb,"sltFlood"), "\"gridcode\" = 1")
        print "Clipping flood to " + region
        floodregion = arcpy.Clip_analysis(selectFlood, aoi, os.path.join(scratchgdb, "floodAOI"), "")
        #floodregion = os.path.join(scratchgdb, "floodAOI")
        #######
        print "Adding some cool fields and doing calculations"
        arcpy.AddGeometryAttributes_management(floodregion, "AREA;PERIMETER_LENGTH", "METERS", "SQUARE_METERS", "")
        fields = arcpy.ListFields(floodregion, "SQUARE")
        if len(fields) !=1:
                arcpy.AddField_management(floodregion, "SQUARE", "DOUBLE", "", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(floodregion, "SQUARE", "!POLY_AREA! / (( !PERIMETER!/4)**2)", "PYTHON_9.3", "")
        fields = arcpy.ListFields(floodregion, "MANAGE")
        if len(fields) !=1:
                arcpy.AddField_management(floodregion, "MANAGE", "SHORT", "1", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(floodregion, "MANAGE", "Calc( !SQUARE!)", "PYTHON_9.3", "def Calc(square):\\n  if (square >= 0.40):\\n    return 1\\n  else:\\n    return 0")
        print "Clipping crops with flood"
        ### More testing
        cropflood = arcpy.Clip_analysis(selectCrop, floodregion, os.path.join(scratchgdb, "crop_cpW_Flood"), "")
        #cropflood = os.path.join(scratchgdb, "crop_cpW_Flood")
        #####
        print "Clipping state data with flood"
        cleanState = arcpy.RepairGeometry_management(State, "DELETE_NULL")      
        clipState = arcpy.Clip_analysis(cleanState, floodregion, "in_memory/stateflood", "")
        print "Union state, wrp, flood, and crop data"
        ### More testing
        bigunion = arcpy.Union_analysis([WRP, floodregion, clipState, cropflood], os.path.join(scratchgdb, "All_Union"), "ALL", "", "GAPS")
        #bigunion = os.path.join(scratchgdb, "All_Union")
        print "Clip union output with flood"
        unionclip = arcpy.Clip_analysis(bigunion, floodregion, os.path.join(scratchgdb, "Union_Clipped"), "")
        #unionclip = os.path.join(scratchgdb, "Union_Clipped")
        print "Lots of field adding and manipulation"
        arcpy.CalculateField_management(unionclip, "MANAGE", "Calc( !MANAGE!, !Program_Na! )", "PYTHON_9.3", "def Calc(manage, wrp):\\n  if (wrp == 'WRP'):\\n    return 2\\n  else:\\n    return manage")
        if checkField(unionclip, "Z_RED_OAK_"):
                arcpy.AddField_management(unionclip, "Z_RED_OAK_", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "HABITAT_TY"):
                arcpy.AddField_management(unionclip, "HABITAT_TY", "TEXT", "", "", "16", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "Z_HARVESTE"):
                arcpy.AddField_management(unionclip, "Z_HARVESTE", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "MANAGING_A"):
                arcpy.AddField_management(unionclip, "MANAGING_A", "TEXT", "35", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "COMMON_NAM"):
                arcpy.AddField_management(unionclip, "COMMON_NAM", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "PROTECTION"):
                arcpy.AddField_management(unionclip, "PROTECTION", "TEXT", "", "", "20", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "SEEDINDEX"):
                arcpy.AddField_management(unionclip, "SEEDINDEX", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "WTRCNTRL"):
                arcpy.AddField_management(unionclip, "WTRCNTRL", "TEXT", "", "", "5", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "PUMP"):
                arcpy.AddField_management(unionclip, "PUMP", "TEXT", "", "", "5", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "REF_HAB"):
                arcpy.AddField_management(unionclip, "REF_HAB", "TEXT", "", "", "5", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "REFHABAC"):
                arcpy.AddField_management(unionclip, "REFHABAC", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(unionclip, "MANAGING_A", "'Private'", "PYTHON_9.3", "")
        arcpy.CalculateField_management(unionclip, "HABITAT_TY", "Calc( !CLASS_NAME!)", "PYTHON_9.3", "def Calc(cover):\\n  ag = ['Corn', 'Millet', 'Sorghum', 'Rice', 'Soybeans']\\n  if (cover in ag):\\n    return 'Cropland'\\n  if (cover == 'Woody Wetlands'):\\n    return cover\\n  return ''\\n")
        arcpy.CalculateField_management(unionclip, "HABITAT_TY", "Calc( !MANAGE!, !HABITAT_TY! )", "PYTHON_9.3", "def Calc(manage, hab):\\n  if(manage==2):\\n    return 'WRP'\\n  else:\\n    return hab")
        arcpy.CalculateField_management(unionclip, "CLASS_NAME", "Calc( !MANAGE!, !CLASS_NAME! )", "PYTHON_9.3", "def Calc(manage, cover):\\n  if(manage==2):\\n    return 'WRP'\\n  else:\\n    return cover")
        if checkField(unionclip, "MANAGEMENT"):
                arcpy.AddField_management(unionclip, "MANAGEMENT", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(unionclip, "MANAGEMENT", "Calc( !MANAGE!)", "PYTHON_9.3", "def Calc(mng):\\n  if(mng == 0):\\n    return 'Natural Flood'\\n  elif(mng == 1):\\n    return 'Managed'\\n  elif(mng == 2):\\n    return 'WRP'")
        if checkField(unionclip, "FUNCTIONAL"):
                arcpy.AddField_management(unionclip, "FUNCTIONAL", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "DEDCALC"):
                arcpy.AddField_management(unionclip, "DEDCALC", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        if checkField(unionclip, "OWNER"):
                arcpy.AddField_management(unionclip, "OWNER", "TEXT", "", "", "20", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(unionclip, "OWNER", "'Private'", "PYTHON_9.3", "")
        if checkField(unionclip, "COVER_TYPE"):
                arcpy.AddField_management(unionclip, "COVER_TYPE", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(unionclip, "COVER_TYPE", "!CLASS_NAME!", "PYTHON", "")
        print "Time to convert to multipart"
        singlepart = arcpy.MultipartToSinglepart_management(unionclip, os.path.join(scratchgdb, "SinglePart"))
        print "Cleaning up and adding geometry"
        arcpy.AddGeometryAttributes_management(singlepart, "AREA", "", "ACRES", "PROJCS['WGS_1984_UTM_Zone_15N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-93.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]")
        arcpy.DeleteField_management(singlepart, "ACRES")
        arcpy.AddField_management(singlepart, "ACRES", "DOUBLE", "18", "3", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(singlepart, "ACRES", "!POLY_AREA!", "PYTHON_9.3", "")
        print "Final output"
        arcpy.FeatureClassToFeatureClass_conversion(singlepart, Workspace, "Natural_flood_" + region, "ACRES >= 1 AND COVER_TYPE <> ''", "MANAGE \"MANAGE\" true true false 2 Short 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",MANAGE,-1,-1;BASIN__HUC \"BASIN__HUC\" true true false 29 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",BASIN__HUC,-1,-1;ACRES \"ACRES\" true true false 4 Double 3 18 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",ACRES,-1,-1;WATERSHED \"WATERSHED\" true true false 45 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",GAUGE,-1,-1;STATE \"STATE\" true true false 2 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",STATE_ABBR,-1,-1;Z_RED_OAK_ \"Z_RED_OAK_\" true true false 8 Double 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",Z_RED_OAK_,-1,-1;HABITAT_TY \"HABITAT_TY\" true true false 16 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",HABITAT_TY,-1,-1;Z_HARVESTE \"Z_HARVESTE\" true true false 8 Double 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",Z_HARVESTE,-1,-1;MANAGING_A \"MANAGING_A\" true true false 255 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",MANAGING_A,-1,-1;COMMON_NAM \"COMMON_NAM\" true true false 100 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",COMMON_NAM,-1,-1;PROTECTION \"PROTECTION\" true true false 20 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",PROTECTION,-1,-1;SEEDINDEX \"SEEDINDEX\" true true false 8 Double 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",SEEDINDEX,-1,-1;WTRCNTRL \"WTRCNTRL\" true true false 5 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",WTRCNTRL,-1,-1;PUMP \"PUMP\" true true false 5 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",PUMP,-1,-1;REF_HAB \"REF_HAB\" true true false 5 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",REF_HAB,-1,-1;REFHABAC \"REFHABAC\" true true false 8 Double 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",REFHABAC,-1,-1;MANAGEMENT \"MANAGEMENT\" true true false 100 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",MANAGEMENT,-1,-1;FUNCTIONAL \"FUNCTIONAL\" true true false 1 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",FUNCTIONAL,-1,-1;DEDCALC \"DEDCALC\" true true false 4 Float 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",DEDCALC,-1,-1;OWNER \"OWNER\" true true false 20 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",OWNER,-1,-1;COVER_TYPE \"COVER_TYPE\" true true false 255 Text 0 0 ,First,#," + os.path.join(scratchgdb, "SinglePart") + ",COVER_TYPE,-1,-1", "")
        print("Everything good")
        logging.info('Done with flood model.  Output: Natural_flood_' + region)
        


def printHelp():
        print '\n naturalflood.py -r <Area of interest feature class> -w <workspace folder where geodatabases should reside> -g <geodatabase name>\n\n' \
                '\n This is the main python script for running the wintering grounds waterfowl model for both the Mississippi Alluvial Valley and West Gulf Coastal Plain regions.\n'\
                'It was written in python using the arcgis python libraries.  Initially it used ArcModels but they proved a bit limiting and not stable enough for future use.\n\n'\
                '\nusage: waterfowlmodel \t[--help] [--region <region>] \n'\
                '\t\t\t[--workspace <path>] [--geodatabase <geodatabase>] \n\n' \
                'These are the options used to initiate and run the waterfowl model properly.\n\n' \
                'Region\n' \
                '\t mav\t\t This option sets the model up to run the Mississippi Alluvial Valley region as the area of interest\n' \
                '\t wgcp\t\t This option sets the model up to run the West Gulf Coastal Plain region as the area of interest\n\n' \
                'Workspace\t\t The folder location where your geodatabase and scratch geodatabase will be write/read to/from\n' \
                'Geodatabase\t\t The geodatabase name where your input datasets will be read from and final output written to\n\n' \
                'Example:\n' \
                'naturalflood.py -r mav -w c:\intputfolder -g modelgeodatabase.gdb\n'
        sys.exit(2)
        
def main(argv):
   aoi = ''
   inworkspace = ''
   ingdb = ''
   try:
      opts, args = getopt.getopt(argv,"hr:w:g:",["region=","workspace="])
   except getopt.GetoptError:
           printHelp()
   for opt, arg in opts:
      if opt in ('-h', '--help'):
         printHelp()
      elif opt in ("-r", "--region"):
         aoi = arg
         if (len(aoi) < 1):
                 print 'Region is incorrect'
                 sys.exit(2)
      elif opt in ("-w", "--workspace"):
         inworkspace = arg
         if not (os.path.exists(inworkspace)):
                 print "Workspace folder doesn't exist.  Please create it"
                 sys.exit(2)
      elif opt in ("-g", "--geodatabase"):
         ingdb = arg
         if not (os.path.exists(inworkspace)):
                 print "GDB doesn't exist.  Please create it"
                 sys.exit(2)

   if len(opts) < 3:
        printHelp()
        
   print 'Region of interest: ', aoi
   print 'Workspace: ', inworkspace
   print 'GDB: ', ingdb

   runFlood(aoi.lower(), inworkspace, ingdb)

if __name__ == "__main__":
   main(sys.argv[1:])





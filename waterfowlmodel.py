# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# WaterfowlModel.py
# Created on: 2017-05-16 15:23:10.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: WaterfowlModel <Workspace> <output> <Imported_natural_flood> <Public_input> <Distirbance_input> 
# Description: The change from ArcMap to ArcPro changed a lot of functions with how models are stored.  I'm attempting to work through more changes by leaving the model in python
# ---------------------------------------------------------------------------

# Set the necessary product code
# import arcinfo


# Import arcpy module
import finaloutput, naturalflood, public
import arcpy, os, sys, getopt, datetime

def printHelp():
        print '\n waterfowlmodel.py -m <waterfowl or flood> -r <Area of interest feature class> -w <workspace folder where geodatabases should reside> -g <geodatabase name>\n\n' \
                '\n This is the main python script for running the wintering grounds waterfowl model for both the Mississippi Alluvial Valley and West Gulf Coastal Plain regions.\n'\
                'It was written in python using the arcgis python libraries.  Initially it used ArcModels but they proved a bit limiting and not stable enough for future use.\n\n'\
                '\nusage: waterfowlmodel \t[--help] [--model <model>] [--region <region>] \n'\
                '\t\t\t[--workspace <path>] [--geodatabase <geodatabase>] \n\n' \
                'These are the options used to initiate and run the waterfowl model propertly.\n\n' \
                'Models\n' \
                '\t waterfowl\t This does the main processing and requires all sub pieces to be complete\n' \
                '\t flood\t\t This runs the flood model\n\n' \
                '\t public\t\t This runs the public model with local input\n\n' \
                'Region\n' \
                '\t mav\t\t This option sets the model up to run the Mississippi Alluvial Valley region as the area of interest\n' \
                '\t wgcp\t\t This option sets the model up to run the West Gulf Coastal Plain region as the area of interest\n\n' \
                'Workspace\t\t The folder location where your geodatabase and scratch geodatabase will be write/read to/from\n' \
                'Geodatabase\t\t The geodatabase name where your input datasets will be read from and final output written to\n\n' \
                'Example:\n' \
                'waterfowlmodel.py -m waterfowl -r mav -w c:\intputfolder -g modelgeodatabase.gdb\n'
        sys.exit(2)
def main(argv):
   aoi = ''
   model = ''
   inworkspace = ''
   ingdb = ''
   try:
      opts, args = getopt.getopt(argv,"hm:r:w:g:",["region=","workspace="])
   except getopt.GetoptError:
           printHelp()
   for opt, arg in opts:
      if opt in ('-h', '--help'):
         printHelp()
      elif opt in ("-m", "--model"):
         model = arg
         if model.lower() not in ("waterfowl", "flood", "public"):
                 print 'Model is incorrect'
                 sys.exit(2)
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

   if len(opts) < 4:
        printHelp()
        
   print 'Model: ', model
   print 'Region of interest: ', aoi
   print 'Workspace: ', inworkspace
   print 'GDB: ', ingdb

   if model == 'waterfowl':
           finaloutput.runWaterfowl(aoi.lower(), inworkspace, ingdb)
   elif model == 'flood':
           naturalflood.runFlood(aoi.lower(), inworkspace, ingdb)
   elif model == 'public':
           public.runPublic(aoi.lower(), inworkspace, ingdb)
           
if __name__ == "__main__":
   main(sys.argv[1:])

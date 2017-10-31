# WaterfowlModelPy
Python waterfowl model using Arc libraries
This is a python script designed to run the Ducks Unlimited precursor waterfowl model.  This model uses spatially explicit habitat and flood data to prepare input for the truemet model.<br>
The script requires you provide the final waterfowl model with output from the flood and public models.  To run any of the models you must provide a workspace (folder) and a geodatabase name that resides in the folder.<br>
The script will copy the named input geodatabase to a folder with the current date and region of interest.  This was done to consolidate the input, output, and log for each run.  This will allow us to reproduce <br>
exact results.<br>
I’ve setup a command line with a help statement.  Through the command line you can run the waterfowl, flood, or public models.  The structure looks something like
<br><br>Waterfowlmodel.py –model (waterfowl, flood, public) –region (mav or wgcp) –workspace (folder with gdb inside and where scratchgdb will be created) –geodatabase (input geodatabase where data resides)

Output is created in the geodatabase specified in the run command.  The truemet input .csv file is created in the folder workspace created inside the specified folder.<br>

Input requirements<br>
All models require the working folder, input geodatabase, and area of interest (mav or wgcp)<br>
Natural flood<br>
	&emsp;Flood – IF_region should be a 0-100 flood frequency dataset.  We're currently using the GCPO Flood frequency dataset clipped to the region of interest.<br>
	&emsp;Crops – Cropscape from whatever year<br>
	&emsp;State boundary<br>
	&emsp;WRP<br>
Public<br>
	&emsp;Public input (data pull from LMVJV web app)<br>
Waterfowl<br>
	&emsp;Natural flood model output<br>
	&emsp;Public model output<br>
	&emsp;State boundary<br>
	
<br><br>


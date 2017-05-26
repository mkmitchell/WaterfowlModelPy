# WaterfowlModelPy
Python waterfowl model using Arc libraries

I’ve setup a command line call with a help statement.  Through the command line you can run the waterfowl, flood, or public models.  The structure looks something like
<br><br>Waterfowlmodel.py –model (waterfowl, flood, public) –region (whatever you specify) –workspace (folder with gdb inside and where scratchgdb will be created) –geodatabase (input geodatabase where data resides)

Once you input the command you want it opens the corresponding python model and runs the analysis.  Output is created in the geodatabase specified in the run command.

Input requirements<br>
They all need the working folder, input geodatabase, and area of interest (mav or wgcp but I set it up for anything)<br>
Natural flood<br>
	&emsp;Flood – I believe this needs to be a binary 0/1 file of our flood area of interest.  I want to make this more dynamic though<br>
	&emsp;Crops – Cropscape from whatever year<br>
	&emsp;State boundary<br>
	&emsp;WRP<br>
Public<br>
	&emsp;Public input (data pull from LMVJV web app)<br>
Waterfowl<br>
	&emsp;Natural flood model output<br>
	&emsp;Public model output<br>
	&emsp;State boundary<br>

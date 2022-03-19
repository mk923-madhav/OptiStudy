# OptiStudy
Codebase for Spring Studio project, OptiStudy

How to setup -
1. Copy the project to your local folder either via git or by downloading
2. Use the following lines to download the required packages
  a. cd copied-project/
  b. python3 -m venv virtualenv/
  c. python3 -m pip install -r requirements.txt

How to use this script -
1. Create a new folder under 'Experiments' for the individual whose calendar you are creating
2. Update the folder name accordingly in the variable 'location' (line 20) - make sure there is a '/' after the folder
3. Add the Canvas URL to 'target_url' (line 23)
4. Execute the script

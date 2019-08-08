# Get the parent directory of this script
$scriptDir = split-path -parent $MyInvocation.MyCommand.Definition
$appDir = split-path -parent $scriptDir
echo $appDir

# Activate the apps python environment.
& ${appDir}\venv\Scripts\Activate.ps1
if (! $?) {
    echo "Error activating python virutal environment.  Exiting."
    exit 1
}

$env:PYTHONPATH = "${appDir}\lib;${appDir}\models;${appDir}\venv\Lib\site-packages"

# Run the app passing along all of the args
python.exe ${appDIR}/lib/main.py $args

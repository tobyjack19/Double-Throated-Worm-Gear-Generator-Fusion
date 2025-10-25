# Double Throated Worm Gear Generator Fusion
Double Throated/Enveloping Worm Gear Drive Parametric Generator for Autodesk Fusion.

This Fusion script will generate the tooth pattern for a double throated / globoid worm gear using the parametric equation set and methodology defined in  https://www.otvinta.com/globoid.html. The parameters for the gear can be edited within the script.

This script does not include generation of the internal body of the worm gear, or the generation of the corresponding spur gears, I found these were simple enough to create using the methodology set out in https://www.otvinta.com/tutorial02.html, however generation of these parts could be incorporated into the script in the future if somebody has the patience.

# Worth noting

# When generating the Gear, you will need to create two copies, one with a defined falloff value (>1), which will be the one used in practice, as the teeth taper off at each end, and another with a falloff value of 0, this will be the one used as reference geometry to create the spur gears, when following the steps laid out in the video (via the URL) above.

The gear drive created using this process is mathematically pretty good, but the gear teeth are fairly basic. It will do the job for those looking for a compact, high(er) torque, robust worm gear setup which can be 3D printed.

For those without prior experience scripting in Fusion, the basics for creating and editing scripts are laid out here: https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-9701BBA7-EC0E-4016-A9C8-964AA4838954

You need only copy the code from the python file in this repo into the python file created upon creating your own fusion script, then run within the Fusion UI as normal. You could also copy the folder "Globoid Gear Helix Generator (V3)" into your default Fusion script folder, this should also work (I believe).

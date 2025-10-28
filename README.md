# Double Throated Worm Gear Generator Fusion
Double Throated/Enveloping/Globoid Worm Gear Drive Parametric Generator for Autodesk Fusion.

This Fusion script will generate the tooth pattern for a double throated / globoid worm gear using the parametric equation set and methodology defined in  https://www.otvinta.com/globoid.html. The parameters for the gear can be edited within the script.

This script does not include generation of the internal body of the worm gear, or the generation of the corresponding spur gears, I found these were simple enough to create using the methodology set out in https://www.otvinta.com/tutorial02.html, however generation of these parts could be incorporated into the script in the future if somebody has the patience.

# Worth noting

When generating the Gear, you will need to create two copies, one with a defined falloff value (>1), which will be the one used in practice, as the teeth taper off at each end, and another with a falloff value of 0, this will be the one used as reference geometry to create the spur gears, when following the steps laid out in the video (via the URL) above.

Once the script has Run in fusion, a message will pop up saying:

---------------------------
Runtime: 5.1385 seconds, worm and gear distance: ... mm, angle between teeth: ... degrees
---------------------------

Make a note of the worm and gear distance (this is the distance between the centrepoint of the worm gear, and the centrepoint of the arc / spur gear) and angle between teeth, these will be necessary using the methodology set out in the video.

# Fusion Scripting

The gear drive created using this process is mathematically pretty good, but the gear teeth are fairly basic. It will do the job for those looking for a compact, high(er) torque, robust worm gear setup which can be 3D printed.

For those without prior experience scripting in Fusion, the basics for creating and editing scripts are laid out here: https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-9701BBA7-EC0E-4016-A9C8-964AA4838954

You need only copy the code from the python file in this repo into the python file created upon creating your own fusion script, then run within the Fusion UI as normal. You could also copy the folder "Globoid Gear Helix Generator (V3)" into your default Fusion script folder, this should also work (I believe).

# The script will generate something like this: 
<img width="1115" height="937" alt="Screenshot 2025-10-25 165958" src="https://github.com/user-attachments/assets/b36c3e4f-fbc2-4752-814c-225e05d84cfc" />

# Which can then be turned into something like this:
<img width="1815" height="952" alt="Screenshot 2025-10-25 17adfasf" src="https://github.com/user-attachments/assets/c5d5d541-162e-498d-ab42-030ace5cc5d2" />

# 3D Printable - but requires some multi part assembly
<img width="1815" height="952" src="[https://github.com/user-attachments/assets/85a45a6e-bdd3-49df-8e93-a5148abdb246]" />

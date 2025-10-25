"""This file acts as the main module for this script."""

import traceback
import adsk.core
import adsk.fusion
import math
import time
# import adsk.cam

# Initialize the global variables for the Application and UserInterface objects.
app = adsk.core.Application.get()
ui  = app.userInterface


def run(_context: str):
    """This function is called by Fusion when the script is run."""
    start_time = time.time()

    try:
        # Your code goes here.
        ui.messageBox(f'"{app.activeDocument.name}" is the active Document.')

        des = adsk.fusion.Design.cast(app.activeProduct)
        root = des.rootComponent
        features = root.features
        #from GenerateCurveFunctions import generate_worm_spiral_func

        sketches = root.sketches
        xyPlane = root.xYConstructionPlane

        # --- USER PARAMETERS ---
        num_curves = 4
        num_points = 50 #Must be even
        u_min, u_max = -1.0, 1.0

        module = 0.2
        arc_angle = 90
        teeth_beta = 5
        ref_radius = 1.2
        falloff_rate = 0 # 0 for no falloff (useful for generating corresponding spur gears), >=1 for falloff

        sketch_name = [
            "Tooth Tip, Top", 
            "Tooth Tip, Bottom", 
            "Tooth Root, Top", 
            "Tooth Root, Bottom"]
        
        x_func = []
        y_func = []
        z_func = []

        # --- GENERATE CURVE FUNCTIONS ---

        CurveFunctions, WormAndGearDistance = generate_worm_spiral_func(module, arc_angle, teeth_beta, ref_radius, falloff_rate, True)

        for i in range(num_curves):
            x_func_in, y_func_in, z_func_in = CurveFunctions[i]
            x_func.append(x_func_in)
            y_func.append(y_func_in)
            z_func.append(z_func_in)

        # --- CREATE SPLINES AND STORE POINTS ---
        spline_points = []  # store all point arrays
        spline_refs = []

        # --- GENERATE MULTIPLE SPLINES ---
        for i in range(num_curves):
            sketch = sketches.add(xyPlane)
            sketch.name = sketch_name[i]
            points = []

            for j in range(num_points + 1):
                u = u_min + (u_max - u_min) * j / num_points
                pt = adsk.core.Point3D.create(x_func[i](u), y_func[i](u), z_func[i](u))
                points.append(pt)

            spline_points.append(points)

             # Add sketch spline
            fit_collection = adsk.core.ObjectCollection.create()
            for p in points:
                fit_collection.add(p)
            spline = sketch.sketchCurves.sketchFittedSplines.add(fit_collection)
            spline_refs.append(spline)

        # --- CREATE Rail lines and loft helixes ---
        pairs = [(0, 1), (1, 3), (3, 2), (2, 0)] #The ordering of the rails in each pair dictates how the end patches are created (use each id only once in the first position to create a loop)
        tolerance = adsk.core.ValueInput.createByReal(0.1)
        lofts = features.loftFeatures
        patches = features.patchFeatures
        stitches = features.stitchFeatures
        helix_surfaces = adsk.core.ObjectCollection.create()
        rail_refs_all = []

        for a, b in pairs:
            ptsA = spline_points[a]
            ptsB = spline_points[b]
            #segment_bodies = adsk.core.ObjectCollection.create()
            sketch = sketches.add(xyPlane)
            sketch.name = f"Loft Splines between {sketch_name[a]} and {sketch_name[b]}"
            RailLines = sketch.sketchCurves.sketchLines

            # Create rail lines connecting the two splines at corresponding parameter samples
            rail_refs = adsk.core.ObjectCollection.create()
            for i in range(num_points + 1):
                p1 = ptsA[i]
                p2 = ptsB[i]
                line1 = RailLines.addByTwoPoints(p1, p2)
                # store the sketch line reference for use as a rail
                rail_refs.add(line1)
            rail_refs_all.append(rail_refs)

            # Create a loft between the two spline sketch curves and include all rails
            loftInput = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            # Add the two spline sketches as sections
            section1 = loftInput.loftSections.add(root.features.createPath(spline_refs[a], False))
            section2 = loftInput.loftSections.add(root.features.createPath(spline_refs[b], False))

            # Add rails to the loft input
            railsCollection = loftInput.centerLineOrRails
            for r in rail_refs:
                railsCollection.addRail(root.features.createPath(r, False))

            loftFeature = lofts.add(loftInput)

            helix_surfaces.add(loftFeature.bodies.item(0))

        # Create patches to close the open ends of the lofts using the collected rail lines
        # Build closed sketch profiles from the start (i=0) and end (i=num_points) endpoints across all pairs
        start_pts = []
        end_pts = []

        for idx in range(len(rail_refs_all)):
            eachSurface = rail_refs_all[idx]

            first_rail = eachSurface.item(0)
            last_rail = eachSurface.item(num_points)

            start_pts.append(first_rail.startSketchPoint.geometry)
            end_pts.append(last_rail.startSketchPoint.geometry)

        def make_closed_sketch_from_points(points_list, sketch_name_suffix):
            sk = sketches.add(xyPlane)
            sk.name = f'Patch profile {sketch_name_suffix}'
            sk_lines = sk.sketchCurves.sketchLines
            first_pt = points_list[0]
            prev_pt = first_pt
            for pt in points_list[1:]:
                sk_lines.addByTwoPoints(prev_pt, pt)
                prev_pt = pt
            # close the loop
            sk_lines.addByTwoPoints(prev_pt, first_pt)

            # Return the first profile found in the sketch
            return sk.profiles.item(0)

        # Create start profile and patch
        profile_start = make_closed_sketch_from_points(start_pts, 'start')
        startPatchInput = patches.createInput(profile_start, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        startPatch = patches.add(startPatchInput)
        helix_surfaces.add(startPatch.bodies.item(0))
            
        # Create end profile and patch
        profile_end = make_closed_sketch_from_points(end_pts, 'end')
        endPatchInput = patches.createInput(profile_end, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        endPatch = patches.add(endPatchInput)
        helix_surfaces.add(endPatch.bodies.item(0))
            
        # Stitch the lofted bodies (including the new patches)
        stitchInput = stitches.createInput(helix_surfaces, tolerance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        stitch = stitches.add(stitchInput)

        end_time = time.time()
        ui.messageBox(f"Runtime: {end_time - start_time:.4f} seconds, worm and gear distance: {(WormAndGearDistance*10):.4f} mm")

    except:  #pylint:disable=bare-except
        # Write the error message to the TEXT COMMANDS window.
        ui.messageBox(f'Failed:\n{traceback.format_exc()}')

###################################################################

def generate_worm_spiral_func(module, arc_angle, teeth_beta, ref_radius, falloff_rate=0, print_equations=False):
    """
    Generate toroidal spiral functions for a worm gear.
    
    Parameters:
        module: gear module
        arc_angle: arc angle in degrees
        teeth_beta: number of teeth within the arc
        ref_radius: reference radius of the worm's waist
        falloff_rate: tooth height falloff rate (0 for no falloff)
        print_equations: if True, prints the formulas for x(u), y(u), z(u)
    
    Returns:
        A list of tuples [(x1(u), y1(u), z1(u)), ..., (x4(u), y4(u), z4(u))]
    """
    # Validation
    if module <= 0:
        raise ValueError("Module must be greater than 0")
    if arc_angle <= 0 or arc_angle >= 180:
        raise ValueError("Arc angle must be >0 and <180")
    
    total_teeth = (360 / arc_angle) * teeth_beta
    if not total_teeth.is_integer():
        raise ValueError("Total number of teeth must be an integer")
    
    if ref_radius < 2 * module:
        raise ValueError("Reference radius must be at least 2 * module")
    
    if falloff_rate > 0 and falloff_rate < 1:
        raise ValueError("Falloff rate must be 0 or greater than or equal to 1")
    
    # Constants
    nTeeth = int(total_teeth)
    distance = ref_radius + (module * nTeeth) / 2
    nAlpha = math.radians(20)  # fixed pressure angle
    
    # Tooth dimensions
    fTop = module * (math.pi / 2 - 2 * math.tan(nAlpha))
    fBottom = fTop + 2 * module * 2.25 * math.tan(nAlpha)
    
    # Torus radii
    r = module * nTeeth / 2
    R = ref_radius + r
    fAngleCoef = 360 / arc_angle
    
    # Tooth angle offsets
    fDelta1 = math.atan(fTop / 2 / (r - module))
    fDelta2 = math.atan(fBottom / 2 / (r + 1.25 * module))
    
    # Function generator
    def make_functions(radius_base, fDelta, nFalloffRate, fMaxRadius):
        def radius_func(u):
            if nFalloffRate > 0:
                return (-0.1*module) + radius_base + (fMaxRadius - radius_base) * 6 * (u**(nFalloffRate*4)/2 - u**(nFalloffRate*6)/3)
            return radius_base
        
        def x(u):
            rad = radius_func(u)
            return - (R - rad * math.cos(u * math.pi / fAngleCoef + (fDelta))) * math.cos(u * math.pi * teeth_beta)

        def y(u):
            rad = radius_func(u)
            return - (R - rad * math.cos(u * math.pi / fAngleCoef + (fDelta))) * math.sin(u * math.pi * teeth_beta)

        def z(u):
            rad = radius_func(u)
            return - rad * math.sin(u * math.pi / fAngleCoef + (fDelta))
        
        if print_equations:
            print(f"\n--- Spiral equations with base radius {radius_base:.4f}, fDelta={fDelta:.4f} ---")
            print(f"x(u) = -( {R:.4f} - radius(u) * cos(u*pi/{fAngleCoef:.4f} + {fDelta:.4f}) ) * cos(u*pi*{teeth_beta})")
            print(f"y(u) = -( {R:.4f} - radius(u) * cos(u*pi/{fAngleCoef:.4f} + {fDelta:.4f}) ) * sin(u*pi*{teeth_beta})")
            print(f"z(u) = - radius(u) * sin(u*pi/{fAngleCoef:.4f} + {fDelta:.4f})")
            if nFalloffRate > 0:
                print(f"radius(u) = {radius_base:.4f} + ({fMaxRadius - radius_base:.4f}) * 6 * (u**{nFalloffRate*4}/2 - u**{nFalloffRate*6}/3)")
            else:
                print(f"radius(u) = {radius_base:.4f}")
        
        return x, y, z
    
    # Generate four spirals
    spirals = [
        make_functions(r - module, -fDelta1, falloff_rate, r + 1.25*module),
        make_functions(r - module, +fDelta1, falloff_rate, r + 1.25*module),
        make_functions(r + 1.25*module, -fDelta2, 0, 0),
        make_functions(r + 1.25*module, +fDelta2, 0, 0)
    ]
    
    return spirals, distance

# Example usage
""" if __name__ == "__main__":
    module = 1
    arc_angle = 90
    teeth_beta = 5
    ref_radius = 12
    falloff_rate = 5

    spirals = generate_worm_spiral_func(module, arc_angle, teeth_beta, ref_radius, falloff_rate, print_equations=True)

    # Sample evaluation
    for u in [0, 0.25, 0.5, 0.75, 1.0]:
        x1, y1, z1 = spirals[0]
        print(f"u={u:.2f}, x1={x1(u):.4f}, y1={y1(u):.4f}, z1={z1(u):.4f}") """

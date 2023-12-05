# Fusion 360 Tips and Tricks

## How to install an add-in or script in Fusion 360

Add the script/add-in to Fusion 360 manually:

If the add-in or script has no installer or is self-created, it must be added manually. A script belongs in the Scripts folder. An add-in belongs in the add-ins folder.

On Windows, these are the folder paths:

For a script, `%appdata%\Autodesk\Autodesk Fusion 360\API\Scripts`.
For an Add-In, `%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns`.

On macOS, these are the folder paths:

For a script, the path is `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts`.
For an add-in, the path is `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns`.

To set up:

See the readme file to determine if the download is a script or an add-in.

Inside the appropriate folders, create a folder that includes all the files of the Add-In or Script. Give the folder the same name as the add-in or script and manifest files.

For example, for the add-in ParameterIO_Python, the script and manifest file names are ParameterIO_Python, so that the folder name would be ParameterIO_Python.

For an existing add-in, replace the existing files with the new versions. To make the add-in or script available, restart Fusion.

The add-in or script is now ready to use and appears in the Scripts and Add-Ins dialog box:

In the toolbar, go to `UTILITIES > Scripts and Add-Ins`.

Run the `Script` or `Add-In` from the list.

## Custom Threads Profiles for 3d-Printing

Fusion 360's current selection of thread profiles aren't overly useful for those looking to design parts that will be 3D printed. Standard 60 degree V threads can be printed satisfactorily by decreasing print speed or increasing cooling. However their tolerances are still machining centric and thus can be difficult to print at times.

 simple script that would generate custom thread profiles that are more conducive to 3D printing. The profiles are trapezoidal in nature with root and crest flats 1/4th the width of the thread pitch. This yields robust threads that will not break easily. The included thread angles are 50, 60, 70, 80, and 90 degrees. For reference the overhang angle of a thread printed in the vertical orientation is 90 - (threadAngle/2) degrees.
 
 Since many are not familiar with thread classes(tolerances) I tried to make the classes self-explanatory. When you select the class drop down you will see 0.###e for external threads, and 0.###i for internal threads. 0.### is the tolerance in millimeters compared to the nominal thread form. External threads are smaller than the nominal, and internal threads are larger than the nominal. If you designed a bolt with a class of 0.100e and a nut with a class of 0.100i, they would have a 0.1 + 0.1 = 0.2mm tolerance/gap between them when threaded together.
 
### Links

[Thread Keeper Fusion 360 Plugin](https://github.com/thomasa88/ThreadKeeper)
[Fusion-360-FDM-threads](https://github.com/dans98/Fusion-360-FDM-threads)
[3D-Printed Threads](https://github.com/BalzGuenat/CustomThreads)
[Custom Screw Creator](https://github.com/Bitfroest/CustomScrews)

## Gears HelicalGear Plus

Generates straight, helical and herringbone external, internal and rack gears as well as non-enveloping worms and worm gears. Parts based on Ross Korsky's Helical gear generator.

https://github.com/NicoSchlueter/HelicalGearPlus

## Export to SVG

Exports bodies & sketch geometry as SVG with an infinite number of color and stroke-width settings.

https://github.com/NicoSchlueter/ExportToSVG


## Reconstructs BRep Surfaces from mesh points.

Reconstructs BRep Surfaces from mesh points.
Generates geometry very close to the original source file, generally within 1e-6mm.

https://github.com/NicoSchlueter/Reverse

## Bevel Gear Generator

https://github.com/padarom/bevel-gear

## Export Cut List

https://github.com/bluekeyes/Fusion360-ExportCutlist

## fusion360-cycloidal-drive

Parametric cycloidal drive generator script for Fusion 360

https://github.com/jackw01/fusion360-cycloidal-drive


## Silvanus Fusion 360 Box Generator

https://github.com/hobbyistmaker/silvanus

## Fusion 360 Bridge support geometry addin

https://github.com/MatejBosansky/Fusion360-Bridge-support-geometry-addin

## Sprocket Generator

https://github.com/kylediaz/Sprocket

## 3D Labprint-style wings

https://github.com/stephensmitchell-forks/fusion360scripts

## Center Of Mass Point

https://github.com/stephensmitchell-forks/fusion360scripts
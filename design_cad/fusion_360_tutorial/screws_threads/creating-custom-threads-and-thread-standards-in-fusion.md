# Creating custom threads and thread standards in Fusion

## Issue:

User reported that, a nonstandard thread or a thread larger than a specific diameter is not available as a predefined thread type for Fusion.

- Unable to create and use a custom/nonstandard thread.
- Unable to define an entire custom thread standard.

## Solution:

### **Use a 3rd party add-on.**

To create a custom threaded screw in Windows, use the [Custom Screw Creator plug-in for Fusion](https://apps.autodesk.com/FUSION/en/Detail/Index?id=79972190430973837&appLang=en&os=Win64).  

### **Modify the thread library.**

Use the following steps to set custom thread parameters and have them appear in the Create > Thread menu in Fusion:

1. Allow access to hidden files and directories. 

   - [How to turn on hidden files and folders on Windows](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-enable-hidden-files-and-folders-on-Windows.html)
   - [How to Access Hidden User Library folder on macOS](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-Access-Hidden-User-Library-folder-on-Mac-OS.html)
   
2. Browse to the following directory:

   > **Note:** Sort by: "Date-created" to find the most recent <version ID> folder. 

   Windows:
   
   `%localappdata%\\Autodesk\\webdeploy\\Production\\<version ID>\\Fusion\\Server\\Fusion\\Configuration\\ThreadData`
   
   macOS:
   
   `Macintosh HD> Users> [Username] > Library > Application Support > Autodesk > Webdeploy > production > [Version ID] > Then right click "Autodesk Fusion 360" and choose Show Package Contents > Contents > Libraries > Applications > Fusion > Fusion > Server > Fusion > Configuration >ThreadData`
   
   [A video showing how to find this location in Finder is linked here.](https://autode.sk/3pqZ8oM)
   
3. Create a copy of the XML thread family that needs to be customized and rename file, for instance:

   "`ACMEScrewThreads.xml`" copy to "`CustomACMEThread.xml`"
   
4. Open the copied file "`CustomACMEThread.xml`". Use a program like Notepad++ or Microsoft Visual Studio to open the XML file. 

5. Modify the name line for the custom thread. 

   (For example, Change "<Name>ACME Screw Threads</Name>" to "<Name>My Customize Threads</Name>")

   > **Note:** all names must be unique.
   
6. Customize other parameters such as pitch, diameter, etc.
7. Save the XML.

> **Notes**: 
> - If this design file is used in Fusion when there is no access to the customized XML file, the following error message may appear:
> 
> "...the current thread family has no suitable type..."
> - When modifying a standard thread type, the design file will be modified back to the standard settings if the feature is recomputed on a machine without access to the customized thread XML file. 
> - When using this procedure to create a custom thread in Fusion, the XML specific formatting is important. XML typos or syntax errors can cause problems in which standard threads are removed from Fusion, and preventing the custom threads from being used in the program. Using an [XML Parser such as this one](https://www.w3schools.com/xml/xml_validator.asp) can help to confirm that the syntax is correct.

# Quick guide on creating the custom thread profile

1. I deleted this space in Notepad++
2. Saved the CustomMetricThread.xml
3. Closed Fusion 360
4. Inserted the XML into `%localappdata%\Autodesk\webdeploy\production\a7c43410973dfb12159f946aa55bfe5a9d8c57c4\Fusion\Server\Fusion\Configuration\ThreadData`
5. Launched Fusion and it seems to work

|![undefined](images/creating-custom-threads-and-thread-standards-in-fusion_original)|![undefined](images/creating-custom-threads-and-thread-standards-in-fusion_original1)|
|------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|

# Reference

- [Fusion 360: Create your own custom Threads Profile](https://youtu.be/IpfPoA6_OWM)

  <iframe width="1280" height="608" src="https://www.youtube.com/embed/IpfPoA6_OWM" title="Fusion 360: Create your own custom Threads Profile" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
  
- [Accurate Parametric Threaded Screw (Bolt) in Fusion 360](https://youtu.be/TKyXV3r7MU8)

  <iframe width="1280" height="720" src="https://www.youtube.com/embed/TKyXV3r7MU8" title="Accurate Parametric Threaded Screw (Bolt) in Fusion 360" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
  
  
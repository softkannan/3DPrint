# Parametric Bottle Cap Generator

**Lost a lid or just want a more functional cap? Generate and print your own, compatible with any existing threads!**

![Beauty shot of various generated bottle caps](images/fusion-360-parametric-bottle-cap-generator_beautyshot1.jpg)

# CAD & Testing

This model was designed in Fusion 360 and uses 3 required input parameters and [standard Metric thread profile](https://amesweb.info/Screws/metric-thread-profile-form-formula.aspx) equations to generate a cap that will perfectly fit any of your threaded containers. Input Parameters can be found from an existing threaded connector following the documentation below and their values can be written in their corresponding Expression boxes in the Parameters spreadsheet of the attached Parametric Bottle Cap Fusion 360 file (shown below)

![Fusion 360 parameters spreadsheet for cap generation](images/fusion-360-parametric-bottle-cap-generator_capparameters.png)

## Project Origins

I originally set out to make this generator due to a need for a lower profile cap for the isopropyl alcohol bottle I keep next to my printer. The thread profile of this bottle is rather abnormal, and thus I found myself finding thread component values with [standard Metric thread profile](https://amesweb.info/Screws/metric-thread-profile-form-formula.aspx) equations, the same used by the generator.

Following the standard Metric thread profile[1](https://teddywarner.org/Projects/ParametricGenerator/#fn:1) (displayed in the diagram below)…

![fusion-360-parametric-bottle-cap-generator_ISOThreadForm1.jpg](images/fusion-360-parametric-bottle-cap-generator_ISOThreadForm1.jpg)

The model derives all necessary values from three required input parameters, all of which are fed into Fusion 360’s coil tool, creating entirely parametrically generated threads. The calculations for user parameters derived from the three required input parameters are as followed …

- Thread Height - 0.8660254037844386 \* ThreadPitch
- Hole Size - ConnectDiamater + ThreadHight
- ThreadDmax - ConnectDiamater
- ThreadDmin - ThreadDmax - 2 \* 5 / 8 \* ThreadHight
- Cap Diamater - *HoleSize + ThreadHight*
- Cap Height - *ConnectLegnth + ThreadPitch / 2 + 1.5 mm*

The implementation of these [standard Metric thread profile](https://amesweb.info/Screws/metric-thread-profile-form-formula.aspx) equations in a Fusion model parametrically was the real kicker of this design. Unfortunately, Fusion’s native thread tool is incompatible with user parameters and thus was unusable in the case of this generator. In its place, I utilized Fusion’s coil tool, manipulating the values found in the generator’s user parameters to create the caps inner threads. The final working coil tool calculations are as followed …

- Diameter - *ThreadDmax + ThreadHight / 4 \* 2*
- Height - *ConnectLegnth + ThreadPitch / 2*
- Pitch - *ThreadPitch*
- Angle - *0.0 deg*
- Selection Size - *ThreadHeight*

all of which are included, shown below, to generate the cap’s threads.

![Fusion 360 coil tool settings for thread generation](images/fusion-360-parametric-bottle-cap-generator_ThreadCap.png)

Following the Generation of the caps thread, an inner contour is added defined by the ISO 965-1 standard[2](https://teddywarner.org/Projects/ParametricGenerator/#fn:2) - shown in the diagram below.

![fusion-360-parametric-bottle-cap-generator_ISOExternalThreadRootContour.jpg](images/fusion-360-parametric-bottle-cap-generator_ISOExternalThreadRootContour.jpg)

This standard calls for radius value *ThreadPitch / 4*, and thus the following values are used in the inner contour …

- Radius - *ThreadPitch / 4*
- Radius Type - *Constant*

The contour is created with Fusion’s Fillet tool and the prior mentioned values, shown below.

![Fusion 360 fillet tool settings for thread contour](images/fusion-360-parametric-bottle-cap-generator_threadfillet.png)

All this yields the successful basic generator, embedded below …

<iframe src="https://myhub.autodesk360.com/ue2cecd93/shares/public/SH9285eQTcf875d3c539495c089187ac95b8?mode=embed" width="95%" height="500" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true" frameborder="0"></iframe>

… however, what fun would a custom cap generator be without a little customization. The generator includes four different body styles,

1. Plain
2. Single-Hole
3. Salt-Shaker
4. Lanyard

… allowing for total cap customization. These styles can be changed, along with two other customization factors, discussed in the *Cap Generation* section below.

# Cap Generation

For documentation purposes, I created a new cap for my Nalgene water bottle …

## Required Measurements

There are three measurements required to generate your cap, all of which can be taken from the existing threaded connector …

1. **Connector Diameter -** Measure the diameter (in MM) of your existing connector, from the very farthest point (i.e. the point of the thread) on either side.

   ![Measuring connector diameter with calipers](images/fusion-360-parametric-bottle-cap-generator_diametermeasurment.jpg)
   
   Then, update the Expression value in the ConnectDiameter row (the box highlighted yellow below) with this found value.

2. **Connector Length -** Measure the height (in MM) of your existing connector, from the top lip to underneath the threads.

   ![Measuring connector length with calipers](images/fusion-360-parametric-bottle-cap-generator_legnthmeasurement.jpg)
   
   Then, update the Expression value in the ConnectLegnth row (the box highlighted yellow below) with this found value.

3. **Thread Pitch -** Measure the thread pitch of your existing connector, the distance in MM between the points of two sequential threads.

   ![Measuring thread pitch with calipers](images/fusion-360-parametric-bottle-cap-generator_pitchmeasurment.jpg)
   
   Then, update the Expression value in the ThreadPitch row (the box highlighted yellow below) with this found value.

## Optional Customization

To offer a bit more customization to each generated cap, there are a couple of different preferences allowing for different functions.

1. **Number of Grips -** The number of grips lining the edge of the cap can be changed in the Expression value of the NumofGrips row. I find values between 40 through 55 work best, but if your experimenting, going below 11 will stop the generation of grip chamfered.

   ![NumofGrips parameter input in Fusion 360](images/fusion-360-parametric-bottle-cap-generator_numofgrips.png)

2. **Grip Depth -** The depths of these grips can be altered, determining how grippy your grips are. I’ve found a value around 0.3 or 0.4 offers a good texture around the edge.

   ![GripDepth parameter input in Fusion 360](images/fusion-360-parametric-bottle-cap-generator_gripdepth.png)

3. **Lid Style -** The lid style of your cap can be toggled between 4 presets in the Fusion Parametric Bottle Cap file by navigating to

   ```
   Parametric-Bottle_Cap > Bodies > Styles
   ```

in the Fusion browser. The lid styles can be toggled between via the eye icon to the left of each style. The four styles are included below, with each of the toggles highlighted.

1. Plain -

   ![Plain cap style selection in Fusion 360](images/fusion-360-parametric-bottle-cap-generator_plain.png)
   
2. Single Hole -

   ![Single hole cap style selection in Fusion 360](images/fusion-360-parametric-bottle-cap-generator_singlehole.png)
   
3. Salt Shaker -

   ![Salt shaker cap style selection in Fusion 360](images/fusion-360-parametric-bottle-cap-generator_saltshaker.png)
   
4. Lanyard -

   ![Lanyard cap style selection in Fusion 360](images/fusion-360-parametric-bottle-cap-generator_lanyard.png)

# Reference

1. https://amesweb.info/Screws/metric-thread-profile-form-formula.aspx [↩](https://teddywarner.org/Projects/ParametricGenerator/#fnref:1)
2. https://www.iso.org/standard/57778.html [↩](https://teddywarner.org/Projects/ParametricGenerator/#fnref:2)




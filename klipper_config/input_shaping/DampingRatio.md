## Prerequisite
I recommend running Dmitry’s latest resonance testing branch and using the pulses method outlined below:

    https://github.com/Klipper3d/klipper/issues/4560
    https://github.com/dmbutyugin/klipper/tree/resonance-test-methods

I would only go down this path if you're getting ghosting with really high speed prints. On the Annex Engineering K3 for example, no matter how perfect the graphs looked, I was still getting some ghosting. That prompted me to go down this path. I'm now able to print at 20-30k acceleration, 250-350mm/s, and 15scv with perfect quality that can usually only be seen at significantly slower speeds. 

The default settings in Klipper have the damping ratio set to .1. This should be fine for most people with sane settings. I like to go for the insane. 

## Calculating your damping ratio
Once you have your graph generated, you can pull the raw CSV values into your favorite graphing software. We will use the half power method to calculate the damping ratio. 
Find your highest resonant frequency and divide the amplitude at this point 1.41 (or the square root of 2). Note the frequency of the intersects at this amplitude. 
 
![image](https://user-images.githubusercontent.com/224365/135765527-05980b08-fc81-407f-804c-f424624dd3ef.png)

The two formulas that we will use are `Q=f0/(f2-f1)` where f0 is your highest resonant frequency, f2 is your higher frequency at the half power intersect, and f1 is the lower. 
The second formula is `Q=1/(2*damping ratio)`
From this you can solve for your damping ratio.
```Damping ratio = (f2-f1)/(2f0)```

## Verifying your damping ratio
You can then test your value. To do this, you need to make a small (hacky) change to input_shaper.py if you want to iterate them both at the same time. 
In `input_shaper.py` in the extras folder of your klipper directory, change the line `damping_ratio_x, damping_ratio_y)` on line 135 to `damping_ratio_x, damping_ratio_x)`
You’ll need to completely restart your klipper instance with `systemctl restart klipper` via ssh. Or just restart your pi completely. Do not just restart via the UI of fluidd/mainsail

You can then use the resonance test STL and iterate your damping value with the tuning tower command. 
```TUNING_TOWER COMMAND=SET_INPUT_SHAPER PARAMETER=DAMPING_RATIO_X START=<some value> = <some value>```

I personally iterated from 0 to .11ish with a factor of .002. 
You can then inspect the output and where you think it looks best. Your calculated value should get you in just about the right space if your IS graphs are clean.  

Don't forget to undo the change listed above in `input_shaper.py` and restart klipper again.

To apply your newly found value add it to your `[input_shaper]` section of your config. 
For me, I added the following to it: 

    [input_shaper]
    ...
    damping_ratio_x: 0.06
    damping_ratio_y: 0.06

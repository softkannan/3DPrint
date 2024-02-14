# Writing Klipper Macros

The following guide is my attempt at explaining how Klipper [1](https://docs.vorondesign.com/community/howto/voidtrance/Klipper_Macros_Beginners_Guide.html#fn:1)†macros work and how write macros. ItÄôs mostly based on my knowledge from reading the Klipper documentation, experimentation, and information from the Klipper Discord.

> **Warning**†The guide below includes GCode and macro examples. They are for illustration purposes only and are not meant to be used on actual hardware. Please, do not copy the examples to your working/production configurations.

## What Are Macros?

Macros are a collection of GCode commands [2](https://docs.vorondesign.com/community/howto/voidtrance/Klipper_Macros_Beginners_Guide.html#fn:2)†that Klipper executes as a unit when the macro is executed. Macros can contain any valid GCode commands and when triggered the entire macro is executed to completion.

Since Klipper is effectively single-threaded, only one macro can be executed at a time (see†`delayed_gcode`†for more on this).

Macros are a convenient way to run an arbitrary number of GCode commands with a single click.

## Structure of a Macro

### A Little Bit on Sections

Klipper's configuration files are divided into sections. Each section has a section header that starts the section. Sections end when a different section is defined or the file ends.

Sections contain multiple key/value pairs separated byÄò:Äô orÄò=Äô. Values can span multiple lines as long as all lines are indented deeper than the original line. This is especially important for macros since they are usually comprised of multiple GCode commands, each on a separate line.

### Basic Structure of a GCode Command

To better understand macros, it is helpful to understand the structure/syntax of GCode commands.

GCode commands consist of the command name and, optionally, a list of parameters. GCode commands appear one per line, where the line starts with the GCode command name, followed by any parameters and, may be, a comment at the end of the line:

```gcode
G0 X10 Y10 Z10 F3600 ; Move to X=10, Y=10, Z=10 at 3600 mm/min
```

In the above example, `G0` is the GCode command name, `X10 Y10 Z10 F3600` are the command parameters, and ; Move to X=10, Y=10, Z=10 at 3600 mm/min is the comment following the command. (The `;` character tells any GCode processors that a comment is starting and that everything after it can be ignored.)GCode commands donít necessarily have to have arguments. Some GCode commands donít even accept parameters as they donít need them. For example, `G90` or `G91`. Furthermore, not all accepted parameters have to be specified. For example, the `G0` command accepts X, Y, Z, and F as parameters but a `G0` command may specify any subset of them:

```gcode
G0 X20 ; Move to X20 maintaining current Y and Z coordinates.
```

### Macros

Macros are defined with the†`[gcode_macro]`†section. You can see the full Klipper documentation for the†`gcode_macro` section† [here](https://www.klipper3d.org/Config_Reference.html#gcode_macro).

Normally, a macro will take the following form:

```ini
[gcode_macro <MACRO_NAME>]
gcode:
<GCode command>
...
```

`<MACRO_NAME>` can be any name that you want. Valid characters are alphanumerics and underscore. Usually, the macro name is written in all caps but thatís not required. Numbers can only appear at the end of the macro names. Macro names that start with underscore (ë_í) are ìhiddenî. They are still defined and callable but are not shown in frontends like Mainsail or Fluidd.Macros are called/triggered either from a frontend or from other macros. To trigger a macro from another macro call it at the appropriate time. For example:

```ini
[gcode_macro MACRO1]
gcode:
  G28 ; home all axis

[gcode_macro MACRO2]
gcode:
  # Home the printer first
  MACRO1
  G0 X0 Y0
```

In the above example, `MACRO2` triggers `MACRO1` as the first command executed. This will cause `MACRO1` to be executed entirely before `MACRO2` continuing to the next GCode command.

#### A BIT MORE ABOUT MACROS AND HOW TO CALL THEM

When a macro is defined with `[gcode_macro MACRO_NAME]`, the collection of GCode commands that are in the body of the macro are grouped together and given the label `MACRO_NAME`. From that point on, `MACRO_NAME` becomes pseudo-GCode command that Klipper recognizes. As such, it can be used in any way that can be used to execute GCode commands - Mainsail console, Moonraker API, GCode files, etc. Also, just like any other GCode command, macros may be created to accept parameters (see (Basic Structure of a GCode Command)[#basic-structure-of-a-gcode-command] and (Macro Template Parameters)[#macro-template-parameters]) or not.It is important to remember that Klipper treats macros as GCode commands in order to better understand how Klipper sequences operations.Klipper completes each GCode command before executing the another one. There is no way to execute two separate GCode commands at the same time. Since macros are treated as GCode commands, they are subject to the same rule - the macro has to complete before the next GCode command is executed. So, despite the fact that macros are comprised of many other GCode commands, Klipper cannot insert/execute other GCode commands while the macro is being executed.

### Variables

Macro variables (the variable_<name> key/value pair) are persistent variables assigned to the macro. Their values can be used/set within the macro or even from another macro. You can think of them as macro-specific global variables.

```ini
[gcode_macro MACRO3]
variable_var1: 0
gcode:
```

The example above defines a macro variable `var1` with an initial value of `0`. This value will be assigned to the variable when Klipper starts up and initializes all macro objects. If the value of the variable is changed at a later time, the new value will persist until changed again.Variables defined by a macro can be referenced from within the macro directly:

```ini
[gcode_macro MACRO4]
variable_var1: 0
gcode:
  M117 Var1 is equal to {var1}
```

Referencing macro variables from a different macro requires the look up of the macro object that defines the desired variables:

```ini
[gcode_macro MACRO5]
gcode:
  {% set macro2 = printer["gcode_macro MACRO2"] %}
  M117 Var1 from MACRO2 is set to {macro2.var1}
```

Changing variable values at runtime is done with the†`SET_GCODE_VARIABLE`command:

```ini
[gcode_macro MACRO6]
gcode:
  SET_GCODE_VARIABLE MACRO=MACRO2 VARIABLE=var1 VALUE=10
```

Please note that the `SET_GCODE_VARIABLE`†command has to be used regardless if the variable is being changed from the defining macro or another one.

### User Macro Settings

Because Klipper allows the definition of an ìemptyî macro - a macro that does not contain any GCode commands, a macro can be created that is just a common storage for various settings/values:

```ini
[gcode_macro _USER_VARIABLES]
variable_var1: 0
variable_var2: 1
gcode:

[gcode_macro MACRO7]
gcode:
  {% set user_vars = printer["gcode_macro _USER_VARIABLES"] %}
  M117 Variable 1: {user_vars.var1}
  M117 Variable 2: {user_vars.var2}
```

In the above example, a hidden macro called†`_USER_VARIABLES` is created, which is used just to hold variables. Then, other macros can reference it to use and/or set variables values.

This is a common usage pattern for many configurations in the Voron community, for example.

## Organizing Configuration Files

Macros are generally placed in configuration files - files with the `.cfg` extension located in the configuration directory (usually `/home/pi/printer_data/config`). Macros can be placed all in a single, large file or split into multiple files, each containing macros and configuration specific to a particular function/configuration.Normally, Klipper looks for a files called printer.cfg in the configuration directory. That file serves as the top-level configuration file. Many users just place all their configuration and macros in that single file.If the configuration is spread into multiple files, the configuration files have to be included into printer.cfg. This is done with the `[include]` directive. This directive instructs Klipper to include the specified file into its configuration. `[include]` directives can be placed in any file and Klipper will include the specified file as itís processing the current configuration file. This allows for the creation of nested configuration.Even if macros are split into multiple configuration files, Klipper creates a singular configuration for the printer. What this means is that all macros defined in all configuration files are defined and available. Therefore, any defined macro can called/triggered from any other macro.

## Macro Templates

Macro templates3 are a way to dynamically change what a macro does based on some conditions or logic. Klipper provides a way to alter the GCode commands executed by wrapping sets of commands with control statements based on the Jinja2 template language4.Macro templates can be a bit confusing because it looks like they offer the ability to created non-static macros (macros that change what they do based on some condition). This is only partially true. The Jinja2 template language is only a macro pre-processor.Klipper evaluates the macro when the macro is triggered/called. The evaluation processes the conditions at that time and generates the body of the macro (the set of commands that the macro will execute). Once evaluated, the set of commands executed by the macro cannot be changed until the macro is triggered/called again. What this means is that there is no way to have the macro content change based on changing printer conditions.The following is an example that illustrates this. Consider the following example macro:

```ini
[gcode_macro EXAMPLE]
gcode:
  M109 S200
  {% for i in range(5) %}
    {% if printer.extruder.temperature < 100 %}
      M117 HEATING...
    {% else %}
      M117 Done.
    {% endif %}
  {% endfor %}
```

Normally, the expectation would be that the above macro will output ìDoneî five times to the console since the `M109 S200` command would ensure that the extruder has reached *200C* before the loop begins. Hence, the condition inside the loop will always be false. The expected GCode stream would be:

```gcode
M109 S200
M117 Done.
M117 Done.
M117 Done.
M117 Done.
M117 Done.
```

However, as described above Klipper macro evaluation happens when the macro is triggered and it happens only once. The template portion of the macro is evaluate prior to any of the GCode commands listed in the macro having been executed. Therefore, if the macro is triggered when the extruder is cold, the `M109 S200` command would not have been issued yet and the extruder temperature used in the condition would be the ambient temperature. Hence, the condition inside the loop will always be true. The actual GCode steam generated would be:

```gcode
M1109 S200
M117 HEATING...
M117 HEATING...
M117 HEATING...
M117 HEATING...
M117 HEATING...
```

Going through the Jinja2 template language is beyond the scope of this guide. However, below are a few examples with descriptions:

### Setting Internal Variables

```ini
[gcode_macro EXAMPLE1]
gcode:
  {% set var1 = printer.toolhead.axis_maximum.x %}
  G0 X{var1}
```

In the example above, the template creates a variable called†`var1` and assigns the maximum position of the X axis [5](https://www.klipper3d.org/Config_Reference.html#gcode_macro). The it uses the variable to move the toolhead to that position along the X axis.

### Conditions

```ini
[gcode_macro EXAMPLE1]
gcode:
  {% set var1 = printer.toolhead.axis_maximum.x %}
  {% set var2 = printer.toolhead.position.x %}

  {% if var2 < var1 %}
    G0 X{var1}
  {% endif %}
```

In the example above, the template creates one variable (`var1` ) to hold the maximum position of the X axis and another (`var2` ) to hold the current position of the toolhead along the X axis. It then check if the current position is less than the maximum and if so, moves the toolhead to the maximum position.

### Loops

Since macro templates are evaluated only once, prior to the execution of any GCode commands from the macro, the template language provides a limited abilities to loop (execute a set of commands repeatedly). For example, the template language does not provide a†`while` loop since such a loop would depend on evaluating changing conditions, which is not possible.

```ini
[gcode_macro EXAMPLE3]
gcode:
  {% set var1 = 10 %}
  {% set var2 = printer.toolhead.axis_maximum.x %}
  {% set var3 = printer.toolhead.axis_maximum.y %}

  G28
  G0 X0 Y0 Z10
  {% for i in range(var1) %}
    G0 X{var2} Y{var3}
    G0 X0 Y0
  {% endfor %}
```

This example uses 3 variables:

1. `var1`, which holds the value `10`ù.
2. `var2`, which holds the maximum position of the X axis.
3. `var3`, which holds the maximum position of the Y axis.


After defining the variables, the printer is homed (`G28` ) and the toolhead is moved to the origin, 10mm above the build plate (`G0 X0 Y0 Z10` ).

Then the macro repeats the commands

```gcode
G0 X{var2} Y{var3}
G0 X0 Y0
```

10 times (the value of†`var1` ), which moves the toolhead to the opposite corner and back to the origin.

### Macro Template Parameters

Klipper provides a way for callers (frontends or other macros) to pass parameters to macros. The Klipper documentation already includes a pretty good section on passing macro parameters. It can be found at https://www.klipper3d.org/Command_Templates.html?h=params#macro-parameters.

Parameters are passed through the†`params`†object that is automatically provided and populated by Klipper. If a macro requires parameters, it can make use of the†`params`†object like below:

```ini
[gcode_macro EXAMPLE4]
gcode:
  {% set var1 = params.VALUE1 %}
```

Then callers can trigger the macro as such:

```gcode
EXAMPLE1 VALUE1=<value>
```

The value set for the†`VALUE1` parameter will automatically be available from†`params.VALUE1`.

Parameter values are always stored as strings. Therefore, it may be necessary to perform a conversion to a more appropriate type (integer, float, list, etc.). This can be done through the use of Jinja's filters [6](#svg-copy). Filters are applied to values through the pipe (`|` ) operator. While a full discussion on filters is beyond the scope of this guide, common filters are†`int`,†`float` , `split`.

```ini
[gcode_macro EXAMPLE5]
gcode:
  {% set var_int = params.INT_VALUE|int %}
  {% set var_float = params.FLOAT_VALUE|float %}
  {% set var_list = params.LIST_VALUE|split(",") %}
```

Another useful filter is the `default()` filter, which will assign a default value to a parameter:

```ini
[gcode_macro EXAMPLE6]
gcode:
  {% set var_int = params.INT_VALUE|default(5)|int %}
  {% set var_float = params.FLOAT_VALUE|default(2.5)|float %}
```

The difference between†`EXAMPLE5`†and†`EXAMPLE6`†is that†`EXAMPLE5`†requires the parameters be set when triggering the macro. Otherwise, Klipper will generate an error due to the missing parameters. On the other hand,†`EXAMPLE6`†can be called without using any parameters, in which case, the default values provided by the†`default()`†filter will be used.

As you can see, filters can be chained one after the other to provide fuller control over parameter values and types.

## Delayed GCode

Delayed GCode [7](#svg-link) macros are a way to schedule a macro to be executed at a later time. They are mostly the same as normal macros with the following exceptions:

- The only key/value pairs that are valid are†`gcode`†and†`initial_duration`.
- They cannot define variables.
- They do not accept parameters.

Unfortunately, this makes them a bit less flexible than normal macros, although there is a workaround for passing parameters to delayed macros.

To define a delayed GCode macro, use the†`[delayed_gcode]`†section:

```ini
[delayed_gcode DELAYED_GCODE_MACRO1]
gcode:
  M117 Delayed GCode macro triggered.
```

Scheduling the delayed GCode macro is done with the†`UPDATE_DELAYED_GCODE`†command:

```ini
UPDATE_DELAYED_GCODE ID=<delayed GCode macro name> DURATION=<delay before execution>
```

The†`DURATION`†value is in seconds. It specifies the number of seconds from the execution of the†`UPDATE_DELAYED_GCODE`†command to when the delayed GCode macro will be triggered. For example, to schedule the†`DELAYED_GCODE_MACRO1`†macro to trigger 5 seconds in the future, the command would be:

```ini
UPDATE_DELAYED_GCODE ID=DELAYED_GCODE_MACRO1 DURATION=5
```

Cancelling a delayed GCode that has already been schedule can be done by setting the†`DURATION`†value to 0. It is not an error to attempt to cancel a delayed GCode macro that had not been already scheduled.

### Passing Parameters to Delayed GCode

While it is not possible to pass variables and/or parameters to delayed GCode macros directly, there is an indirect way to do this - by using variables defined by another macro (see† [User Macro Settings](#svg-copy) ):

```ini
[gcode_macro __PARAMETERS]
variable_var1: 0
variable_var2: 10

[delayed_gcode DELAYED_GCODE_MACRO2]
gcode:
  {% set parameters = printer["gcode_macro __PARAMETERS] %}
  M117 var1 = {var1}, var2 = {var2}

[gcode_macro SCHEDULE_DELAYED]
gcode:
  SET_GCODE_VARIABLE MACRO=__PARAMETERS VARIABLE=var1 VALUE=20
  SET_GCODE_VARIABLE_MACRO=__PARAMETERS VARIABLE=var2 VALUE=40
  UPDATE_DELAYED_GCODE ID=DELAYED_GCODE_MACRO2 DURATION=10
```

The above example makes uses of several feature of Klipper macros:

1. `Hiddenù` macros, which are not shown in frontends.
2. Macro variables.
3. Ability to reference macro variables from other macros.
4. Ability to set macro variables from other macros.


### Background Macros

One of the more common uses of delayed GCode macros is to create `background` macros - macros that execute somewhat asynchronously in the background. This is done by creating the delayed GCode macro in such a way that it repeatedly schedules itself based on current conditions. This is possible because Klipper updates the current state of the printer just prior to executing the macro. Below is a simple example of this:

```ini
[delayed_gcode DELAYED_GCODE_MACRO3]
gcode:
  {% set current_temp = printer[printer.toolhead.extruder].temperature %}
  {% set target_temp = printer[printer.toolhead.extruder].target %}

  {% if current_temp < target_temp> %}
    M117 Still heating...
    UPDATE_DELAYED_GCODE ID=DELAYED_GCODE_MACRO3 DURATION=1
  {% else %}
    M117 Target temperature reached
    UPDATE_DELAYED_GCODE ID=DELAYED_GCODE_MACRO3 DURATION=0
  {% endif %}

[gcode_macro HEAT_EXTRUDER]
gcode:
  M104 S240
  UPDATE_DELAYED_GCODE ID=DELAYED_GCODE_MACRO3 DURATION=1
```

The above example shows how delayed GCode macros can be used to implement a pseudo†`while`†loop. When triggered, the†`HEAD_EXTRUDER`†macro will set the extruder temperature to `240` degrees and schedule the†`DELAYED_GCODE_MACRO3`†to execute in 1 second.

When the†`DELAYED_GCODE_MACRO3`†executes, it will look up the current and target temperature of the extruder. If the current temperature is less than the target, it will re-schedule itself to run again after 1 second. Otherwise, it will cancel itself.

> **Warning**†Be careful when using the above mechanism to create background macros. In most case, it is difficult to implement the exact desired behavior due to the limitations imposed by Klipper and delayed GCode macros.

## Saving and Restoring GCode State

Klipper GCode state is the current state of the GCode parser. The state includes the following settings:

- GCode coordinate mode (absolute vs relative).
- Extrude mode (absolute vs relative).
- Origin.
- Z offset.
- Speed and extrude overrides.
- Move speed.
- Current nozzle position.
- Relative extruder position.

Saving the GCode state allows other macros to perform actions without interfering with the state of previous macros. This is especially useful for macros like†`PAUSE`†and†`RESUME`†- the†`PAUSE`†macro saves the GCode state when the print was paused and the†`RESUME`†macro restores it. This prevents any GCode that is executed between the†`PAUSE`†and†`RESUME`†macros (like change filament macros, clean nozzle macros, etc.) from interfering or destroying the state the printer was in when it paused.

Saving and restoring GCode state is done with the†`SAVE_GCODE_STATE` [8](https://docs.vorondesign.com/community/howto/voidtrance/Klipper_Macros_Beginners_Guide.html#variables)†and†`RESTORE_GCODE_STATE` [9](https://docs.vorondesign.com/community/howto/voidtrance/Klipper_Macros_Beginners_Guide.html#variables)†commands. When saving a state, the†`SAVE_GCODE_STATE`†command takes in a†`NAME`†argument. The saved state can then be referenced using that name. This allows nesting of these commands.

Upon execution of the†`SAVE_GCODE_STATE NAME=<name>`†command, the current GCode state is saved under the nameÄú". When the `RESTORE_GCODE_STATE NAME=` command is executed, the state saved as "" is restored. Any changes to the settings listed above done between the `SAVE_GCODE_STATE` and `RESTORE_GCODE_STATE` commands is lost (unless saved under a different name).

> **Warning**†The use of the save/restore commands should be done carefully and intentionally. State that has changed between two two commands can be lost, which can lead to unexpected results. One example of this is using save/restore in†`PRINT_START`†macros. Action done by a†`PRINT_START`†macro wrapped by a set of†`SAVE_GCODE_STATE/RESTORE_GCODE_STATE`†commands might be lost after the previous state is restored.
>
> For example, if one of the things that a†`PRINT_START`†macro does is adjust the Z offset for a particular filament type or print surface, the newly set Z offset will be lost when the†`PRINT_START`†macro ends.

## Macros and Slicers

When first building or setting up a new printer, the first place where a user might need to modify Klipper macros is probably going to be the†`PRINT_START`†and/or†`PRINT_END`†macros.

These two macros are usually used to do all of the operations to prepare for a print (`PRINT_START` ) or to finish a print (`PRINT_END` ). Such operations may include homing, bed leveling, generating a bed mesh, pre-heating the nozzle, bed, or chamber, etc.

Normally, this will take the shape of adding code to the macro to do the desired operations. However, a frequent issue that has happened to users is the need to pass information from the slicer to the printer.

Slicer profiles define the parameters for the printer, filament(s), and the individual print. Those parameters are then used to generate the appropriate GCode commands for the print.

While passing values, settings, etc. from a slicer to the printer can take many different forms, a common way to do that is to use macro parameters to pass values to the†`PRINT_START`†macro. Such values may include the bed and extruder temperatures, chamber temperature, type of filament being used, etc.

Passing values from the slicer is as simple as calling the†`PRINT_START`†macro in the beginning of the produced GCode. Every commonly used slicer has a way for the user to provide custom GCode that will be inserted at the start of the output file. Each slicer also should have a way to reference slicer setting by that custom GCode. At this point, passing information to the printer is only a matter of calling†`PRINT_START`†with a macro parameter for each of the slicer settings of interest.
More detailed information about passing values from slicers to Klipper
Below are some examples for some of the common slicers.

> **WARNING**†What is shown below are just examples. Please, donÄôt just use the GCode blindly. Verify that the correct settings/placeholders are being used.

### PrusaSlicer/SuperSlicer

PrusaSlicer (PS) and SuperSlicer (SS) have multiple places where custom GCode can be added depending on what that GCode affects. For the†`PRINT_START`†macro, the location where to add custom GCode is in ***Start G-codeù*** section under the `Printer Settings -> Custom G-code`ù.

```gcode
PRINT_START EXTRUDER_TEMP={first_layer_temperature[initial_extruder]} BED_TEMP=[first_layer_bed_temperature] CHAMBER_TEMP=[chamber_temperature]
```

The above example will call the†`PRINT_START`†macro in the beginning of the GCode file, passing the extruder, bed, and chamber temperature as defined in the slicer profile being used. In order to allow the slicer to substitute the actual values, the command uses `placeholdersù` [10](https://docs.vorondesign.com/community/howto/voidtrance/Klipper_Macros_Beginners_Guide.html#what-are-macros). When outputting the final GCode, PS/SS will substitute the actual values in place of the placeholders. For example, if the profile being used define extruder temperature as `240C`, bed temperature as `75C`, and chamber temperature as `40C`, the command appearing in the GCode file will be:

```gcode
PRINT_START EXTRUDER_TEMP=240 BED_TEMP=75 CHAMBER_TEMP=40
```

### Cura

The place where to add similar custom GCode in Cura is in the `Start G-code`ù window in the `Machine Settings -> Printer`ù screen.

```gcode
PRINT_START EXTRUDER_TEMP={material_print_temperature_layer_0} BED_TEMP={material_bed_temperature_layer_0} CHAMBER_TEMP={build_volume_temperature}
```

The Cura GCode is very similar with the exception of the placeholder names [11](#svg-link).## Examples### 1. Print Start ```gcode
;TYPE:CustomM104 S0 ; Stops PS/SS from sending temp waits separatelyM140 S0PRINT_START BED=55 EXTRUDER=215 CHAMBER=15 SIZE=120.678_167.153_229.322_182.847 MATERIAL=PLAM107G21 ; set units to millimetersG90 ; use absolute coordinatesM83 ; use relative distances for extrusion;_TOOLCHANGE 0M107;LAYER_CHANGE;Z:0.25;HEIGHT:0.25;BEFORE_LAYER_CHANGE;0.25
```
```ini
[gcode_macro PRINT_START]gcode:     # Parameters    {% set BED_TEMP = params.BED|float %}    {% set EXTRUDER_TEMP = params.EXTRUDER_TEMP|float %}        {% set CHAMBER_TEMP = params.CHAMBER|float %}    {% set MATERIAL = params.MATERIAL|string %}    {% set FL_SIZE = params.SIZE|default("0_0_0_0")|string %}    G32                            ; home all axes    G1 Z100 F3000                   ; move nozzle away from bed    M190 S{BED_TEMP}            ; set and wait for bed to reach temp    M109 S{EXTRUDER_TEMP}       ; set and wait for hot end to reach temp	RESPOND MSG="Printing {MATERIAL} at {EXTRUDER_TEMP}"```

### 2. Delay command with hours, minutes, and seconds.

-Takes in hours, minutes, and seconds and converts it to millisceonds for an easy way to delay an exact time.

```ini
[gcode_macro DELAY]description: Send `DELAY [H=<value>] [M=<value>] [S=<value>] [P=<value>] ` to set the Hours, Minutes, and Seconds for a delay. Passing no paramaters will not have any delay.gcode:	{% set Hours   = params.H|default(0)|int %}	{% set Minutes = params.M|default(0)|int %}	{% set Seconds = params.S|default(0)|int %}	{% set Milliseconds = params.P|default(0)|int %}	{% set TIME = (((Hours*3600) + (Minutes*60) + (Seconds))*1000)+Milliseconds|int %}		{action_respond_info('Delaying for {} milliseconds'.format(TIME))}	G4 P{TIME}
```
### 3. Beeper

Allows you to utilize your LCD beeper. This requires you to specify your beeper pin as an output pin.

#### PWM Beeper

A PWM beeper is more common nowadays, and is used on the common MINI12864 display.

Your†`pin` †may be different.

```ini
[output_pin beeper]
pin: EXP1_1
value: 0
shutdown_value: 0
pwm: True
cycle_time: 0.0005 ; Default beeper tone in kHz. 1 / 0.0005 = 2000Hz (2kHz)
```

Usage:

- `BEEP` : Beep once with defaults.
- `BEEP I=3` : Beep 3 times with defaults.
- `BEEP I=3 DUR=200 FREQ=2000` : Beep 3 times, for 200ms each, at 2kHz frequency.

```ini
[gcode_macro BEEP]gcode:    # Parameters    {% set i = params.I|default(1)|int %}           ; Iterations (number of times to beep).    {% set dur = params.DUR|default(100)|int %}     ; Duration/wait of each beep in ms. Default 100ms.    {% set freq = params.FREQ|default(2000)|int %}  ; Frequency in Hz. Default 2kHz.    {% for iteration in range(i|int) %}        SET_PIN PIN=beeper VALUE=0.8 CYCLE_TIME={ 1.0/freq if freq > 0 else 1 }        G4 P{dur}        SET_PIN PIN=beeper VALUE=0        G4 P{dur}    {% endfor %}
```

This is the simple looping implementation. If you're feeling fancy, you can also† [![:page_facing_up:](https://github.githubassets.com/images/icons/emoji/unicode/1f4c4.png)†play tunes with it](https://github.com/majarspeed/Profiles-Gcode-Macros/tree/main/Beeper%20tunes). (Tune macros by Dustinspeed#6423)

## Non-PWM Beeper

Non-PWM beepers are used on some other displays such as the Ender 3 stock display.

Your†`pin` †will likely be different.

```ini
[output_pin beeper]
pin: P1.30
value: 0
shutdown_value: 0
```

Usage:

- `BEEP` : Beep once with defaults.
- `BEEP I=3` : Beep 3 times with defaults.
- `BEEP I=3 DUR=100` : Beep 3 times, for 100ms each.

```ini
[gcode_macro BEEP]gcode:    # Parameters    {% set i = params.I|default(1)|int %}        ; Iterations (number of times to beep).    {% set dur = params.DUR|default(100)|int %}  ; Duration/wait of each beep in ms. Default 100ms.    {% for iteration in range(i|int) %}        SET_PIN PIN=beeper VALUE=1        G4 P{dur}        SET_PIN PIN=beeper VALUE=0		G4 P{dur}    {% endfor %}```

### 4. Home if not already homed.

This is useful to throw at the beginning of other macros.

```
[gcode_macro _CG28]
gcode:
  {% if "xyz" not in printer.toolhead.homed_axes %}
    G28
  {% endif %}```



## References


- [Klipper Documentation](https://www.klipper3d.org/)
- [Klipper GCode command reference](https://www.klipper3d.org/G-Codes.html)
- [Klipper Command Templates](https://www.klipper3d.org/Command_Templates.html)- [Variables](https://www.klipper3d.org/Command_Templates.html#variables)
- [Printer Variable](https://www.klipper3d.org/Command_Templates.html?h=printer#the-printer-variable)- [Delayed G-Code](https://www.klipper3d.org/Command_Templates.html?h=delayed#delayed-gcodes)- [Save G-Code State](https://www.klipper3d.org/G-Codes.html?h=save_gc#save_gcode_state)- [Restore G-Code State](https://www.klipper3d.org/G-Codes.html?h=save_gc#restore_gcode_state)
- [Jinja Documentation](https://jinja.palletsprojects.com/en/2.10.x/templates/#)- [Jinja Templates Filters](https://jinja.palletsprojects.com/en/3.1.x/templates/#filters)
- [PrusaSlicer Placeholders](https://help.prusa3d.com/article/list-of-placeholders_205643)
- [Cura Placeholders](http://files.fieldofview.com/cura/Replacement_Patterns.html)
- [Print Tuning Guide](https://ellis3dp.com/Print-Tuning-Guide/)


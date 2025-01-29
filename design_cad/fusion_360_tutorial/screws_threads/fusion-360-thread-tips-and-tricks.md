# How to add Custom Threads to Fusion 360!

<iframe width="1280" height="720" src="https://www.youtube.com/embed/VPDngPAvFnQ" title="How to add Custom Threads to Fusion 360! | Fusion 360 Tutorial" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Path: C:\Users\[USER]\AppData\Local\Autodesk\webdeploy\production\[VERSION]\Fusion\Server\Fusion\Configuration\ThreadData

It gives your alot of control. That is much better than doing it manually.

Here is a description of what you can control.

## Sample XML with Functional Parameters:

```xml
<?xml version="1.0" encoding="utf-8"?>
<ThreadTable version="1.0">
  <ThreadType>
    <Name>Metric 3D Printed Plastic Threads</Name>
    <CustomName>Metric 3D Printed Plastic Threads</CustomName>
    <Unit>mm</Unit>
    <Angle>45</Angle>
    <SortOrder>26</SortOrder>

    <ThreadSize>
      <Size>1.0</Size>
      <Designation>
        <ThreadDesignation>1x0.44</ThreadDesignation>
        <CTD>1x0.44</CTD>
        <Pitch>0.44</Pitch>

        <Thread>
          <Gender>external</Gender>
          <Class>h14</Class>
          <MajorDia>1</MajorDia>
          <PitchDia>0.82</PitchDia>
          <MinorDia>0.64</MinorDia>
        </Thread>

        <Thread>
          <Gender>internal</Gender>
          <Class>G14</Class>
          <MajorDia>1.0</MajorDia>
          <PitchDia>0.85</PitchDia>
          <MinorDia>0.66</MinorDia>
        </Thread>
      </Designation>
    </ThreadSize>
  </ThreadType>
</ThreadTable>
```

## Explanation of Functional Parameters:

1. **`<MajorDia>`**:
   
   - **Effect**: Defines the **major diameter**, which is the largest diameter for external threads and the smallest diameter for internal threads.
   - **Explanation**: This parameter controls the outermost dimension of the thread, ensuring that external threads fit into internal threads of matching diameters.
   
2. **`<MinorDia>`**:

   - **Effect**: Defines the **minor diameter**, which is the smallest diameter for external threads and the largest diameter for internal threads.
   - **Explanation**: This governs the innermost part of the thread profile, playing a critical role in ensuring the threads mate properly without excessive gaps or friction.

3. **`<PitchDia>`**:
   
   - **Effect**: The **pitch diameter** is the diameter where the thread’s profile is equally thick on both sides.
   - **Explanation**: The pitch diameter is crucial for achieving the correct fit between internal and external threads. It determines how tightly the threads engage and the overall strength of the threaded connection.

4. **`<Pitch>`**:

   - **Effect**: Defines the **pitch**, which is the distance between adjacent thread peaks (or valleys).
   - **Explanation**: The pitch determines how fine or coarse the threading is. A finer pitch (smaller number) results in more threads per length, while a coarser pitch (larger number) results in fewer threads per length, which can affect both the strength and ease of printing or machining.

5. **`<Angle>`**:

   - **Effect**: Specifies the **thread angle**, which is the angle between the sides (flanks) of the thread.
   - **Explanation**: This angle is typically set at 30° for most metric threads but can vary. In the sample, it’s set to 45°, which affects the overall thread profile and can make threads easier to print or manufacture, particularly with plastic materials.

## Summary:

In this XML sample, the functional parameters that influence the actual thread geometry are:

- **`<MajorDia>`**: Controls the outer diameter.
- **`<MinorDia>`**: Controls the inner diameter.
- **`<PitchDia>`**: Determines the fit and strength.
- **`<Pitch>`**: Controls the distance between threads.
- **`<Angle>`**: Determines the thread flank angle.


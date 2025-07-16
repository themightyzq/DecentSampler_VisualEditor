# 🎵 DecentSampler Sample Grouping Guide

## Understanding Sample Groups in DecentSampler

Sample groups are the key to creating sophisticated, expressive sample libraries. Here's how to set up the three main grouping scenarios you mentioned:

---

## 📊 **Scenario 1: Velocity Layers**
*Different samples trigger based on how hard you play*

### How It Works:
- **Multiple groups** with **same key ranges** but **different velocity ranges**
- Soft playing triggers one sample, loud playing triggers another
- Each group has separate samples for different dynamics

### Example Setup:
```
Group 1: "Soft Layer"    - Velocity 0-63   - Contains: Piano_C4_Soft.wav
Group 2: "Medium Layer"  - Velocity 64-100 - Contains: Piano_C4_Medium.wav  
Group 3: "Loud Layer"    - Velocity 101-127- Contains: Piano_C4_Loud.wav
```

### In Your Editor:
1. **Create 3 groups** using "Create Velocity Layers" button
2. **Import samples** for each dynamic level
3. **Assign samples** to appropriate velocity group
4. **Set velocity ranges** in each group (editor will auto-calculate)

### Result:
- Gentle keypress = Soft sample plays
- Medium keypress = Medium sample plays  
- Hard keypress = Loud sample plays

---

## 🎛️ **Scenario 2: Sample Blending (BrokenPiano Style)**
*Multiple samples play simultaneously with crossfade control*

### How It Works:
- **Single group** containing **multiple samples** for the **same keys**
- All samples play at once, but volumes are controlled by **tags**
- UI slider crossfades between tagged sample sets

### BrokenPiano Analysis:
Looking at the example file, here's exactly what happens:

```xml
<group enabled="true">
  <!-- BOTH samples are in the SAME group for C4 (notes 60-71) -->
  <sample path="Samples/C4_Close.wav" rootNote="60" loNote="60" hiNote="71" />
  <sample path="Samples/C4_Distant.wav" rootNote="60" loNote="60" hiNote="71" />
</group>
```

**The Magic**: The "Mic Blend" slider (lines 81-84) uses **tag-based volume control**:
```xml
<control parameterName="Mic Blend" minValue="0" maxValue="100" value="50">
  <binding type="amp" level="tag" identifier="mic_close" parameter="AMP_VOLUME" 
           translation="linear" translationOutputMin="1" translationOutputMax="0" />
  <binding type="amp" level="tag" identifier="mic_distant" parameter="AMP_VOLUME" 
           translation="linear" translationOutputMin="0" translationOutputMax="1" />
</control>
```

### In Your Editor:
1. **Create 1 group** using "Create Blend Layers" button
2. **Import both sample types** (close and distant mics)
3. **Add ALL samples to the same group**
4. **Tag samples**: "mic_close" for close samples, "mic_distant" for distant
5. **Create blend control** that crossfades between tags

### Result:
- **Both samples always play together**
- Slider at 0% = Only close mic audible
- Slider at 50% = Both mics at equal volume
- Slider at 100% = Only distant mic audible

---

## 🔄 **Scenario 3: Multiple Simultaneous Layers**
*Several samples play together on the same key for rich textures*

### How It Works:
- **Single group** with **multiple samples** covering **same key range**
- All samples trigger together when key is pressed
- Used for creating rich, layered sounds

### Example Setup:
```
Group 1: "Layered Sound"
  - Piano_C4_Close.wav    (loNote: 60, hiNote: 60)
  - Strings_C4.wav        (loNote: 60, hiNote: 60)  
  - Pad_C4.wav           (loNote: 60, hiNote: 60)
```

### In Your Editor:
1. **Create 1 group**
2. **Import all layer samples**
3. **Add all to the same group** with **identical key ranges**
4. **Adjust individual sample volumes** for balance

### Result:
- **All samples play simultaneously** when C4 is pressed
- Creates rich, complex timbres
- Individual volumes can be adjusted per sample

---

## 🎯 **Quick Reference: When to Use What**

| Scenario | Groups | Samples Per Key | Control Method | Use Case |
|----------|---------|-----------------|----------------|----------|
| **Velocity Layers** | Multiple | 1 per group | Velocity sensitivity | Piano dynamics, drum hits |
| **Sample Blending** | Single | Multiple | Tag-based volume | Close/distant mics, pickup blends |
| **Simultaneous Layers** | Single | Multiple | Individual volumes | Rich textures, layered sounds |

---

## 🛠️ **How to Set These Up in Your Editor**

### **Step 1: Open Group Manager**
The new Group Manager panel provides all the tools you need.

### **Step 2: Choose Your Scenario**
- **Velocity Layers**: Click "Create Velocity Layers" → Choose number of layers
- **Sample Blending**: Click "Create Blend Layers" → Set up tags  
- **Simultaneous Layers**: Click "Add Group" → Add multiple samples to same group

### **Step 3: Assign Samples**
- Drag samples from main list to appropriate groups
- Set key ranges and velocity ranges as needed
- Add tags for blending scenarios

### **Step 4: Create Controls**
- For velocity layers: ADSR controls affect all layers
- For blending: Create blend slider with tag bindings
- For layers: Individual volume controls or master mix

---

## 💡 **Pro Tips**

### **For Velocity Layers:**
- Use 2-4 layers max (more becomes unwieldy)
- Overlap velocity ranges slightly for smooth transitions
- Match sample timing and tuning carefully

### **For Sample Blending:**
- Record samples in same session for consistent timbre
- Use clear, descriptive tags (mic_close, mic_far, pickup_neck, pickup_bridge)
- Test blend positions to ensure smooth crossfades

### **For Simultaneous Layers:**
- Balance volumes carefully to avoid muddy mix
- Use complementary timbres (not competing frequencies)
- Consider phase relationships between samples

---

## 🔍 **Real-World Examples**

### **Piano Preset** (Velocity Layers):
```
Group 1: "Piano Soft"    - Velocity 0-42
Group 2: "Piano Medium"  - Velocity 43-84  
Group 3: "Piano Hard"    - Velocity 85-127
```

### **Guitar Preset** (Sample Blending):
```
Group 1: "Guitar Blend"
  - Samples tagged "pickup_neck" and "pickup_bridge"
  - Blend control crossfades between pickup positions
```

### **Pad Preset** (Simultaneous Layers):
```
Group 1: "Rich Pad"
  - Analog_Pad.wav + String_Section.wav + Choir_Ah.wav
  - All play together for lush texture
```

---

## ❓ **Troubleshooting**

### **Velocity Layers Not Working?**
- Check velocity ranges don't overlap incorrectly
- Verify each group has samples in correct velocity range
- Test with different velocity values

### **Blend Control Not Smooth?**
- Ensure samples are tagged correctly
- Check tag names match exactly in control bindings
- Verify translation ranges (0-1 for volume)

### **Layers Too Quiet/Loud?**
- Adjust individual sample volumes within group
- Use group volume control for overall level
- Check for phase cancellation between samples

---

This system gives you complete control over how samples are organized and triggered, allowing you to create everything from simple single-layer presets to complex, multi-dimensional instruments!
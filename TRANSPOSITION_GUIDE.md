# 🎵 Sample Transposition System Guide

## Overview

The DecentSampler frontend now includes a comprehensive transposition system that automatically handles pitch shifting when samples are played across the keyboard. This system calculates the proper pitch ratio based on the root note and applies high-quality audio transposition.

---

## 🎯 **How It Works**

### **Core Concept**
- Each sample has a **root note** (the original pitch it was recorded at)
- When you play a different note, the system calculates the **pitch ratio** needed
- The audio is transposed in real-time using the best available method

### **Pitch Calculation**
```
Semitone Difference = Played Note - Root Note
Pitch Ratio = 2^(Semitone Difference / 12)
```

**Examples:**
- Playing C5 (60) when root is C4 (48) = +12 semitones = 2.0x pitch ratio (octave up)
- Playing C3 (36) when root is C4 (48) = -12 semitones = 0.5x pitch ratio (octave down)
- Playing D4 (50) when root is C4 (48) = +2 semitones = 1.122x pitch ratio

---

## 🎹 **Visual Indicators on Piano**

### **Transposition Arrows**
- **↑** Green arrows: Notes pitched up from root
- **↓** Red arrows: Notes pitched down from root  
- **⇈** Dark green: More than octave up
- **⇊** Dark red: More than octave down

### **Root Note Markers**
- **🔸 Red diamonds**: Show the original root note of each sample
- **Color stripes**: Bottom of white keys show mapping ranges
- **Colored dots**: Top of black keys indicate mapped samples

### **Hover Tooltips**
Rich information when hovering over keys:
- Sample name and file path
- Key range (lo-hi) and root note
- **Transposition direction and amount**
- **Pitch ratio** for the current note
- **Total cents** if fine-tuned
- Velocity range and volume info

---

## 🎚️ **Transposition Controls**

### **TranspositionControlWidget**
Full-featured control panel for precise transposition:

#### **Root Note Section**
- **MIDI Note Spinner**: Set root note (0-127)
- **Note Name Display**: Shows note name (e.g., "C4")
- **Auto-Detect Button**: Attempts to detect root from filename

#### **Fine Tuning Section**
- **Cents Adjustment**: ±1200 cents (±1 octave)
- **Semitone Offset**: ±24 semitones (±2 octaves)
- **Reset Button**: Return to default tuning

#### **Preview Section**
- **Test Note Selector**: Choose any note to preview
- **Play Button**: Hear the transposed result
- **Transposition Info**: Real-time feedback on pitch changes

#### **Capabilities Info**
- **Engine Status**: Shows available transposition quality
- **Recommendations**: Suggests library installations for better quality

### **MiniTranspositionWidget**
Compact version for inline use:
- Root note spinner
- Tune cents spinner
- Minimal footprint for crowded UIs

---

## 🔧 **Transposition Engine**

### **Quality Levels**

#### **High Quality - Librosa PSOLA**
```bash
pip install librosa soundfile
```
- **Best quality**: Uses phase vocoder technology
- **Preserves timbre**: Maintains original character
- **Handles extreme ranges**: Works well for large pitch shifts

#### **Medium Quality - Pydub Speed Change**
```bash
pip install pydub
```
- **Good quality**: Simple speed-based transposition
- **Fast processing**: Lower CPU usage
- **Moderate ranges**: Best for ±1 octave shifts

#### **Basic Quality - No Transposition**
- **Fallback mode**: When no libraries available
- **Shows calculations**: Displays pitch info without actual transposition
- **Direct playback**: Plays original samples unchanged

### **Automatic Method Selection**
The system automatically detects and uses the best available method:

1. **Librosa** (if available) - Highest quality
2. **Pydub** (if available) - Medium quality  
3. **Basic** (always available) - Information only

---

## 🎼 **Usage Examples**

### **Setting Up a Piano Sample**
1. **Import sample**: `Piano_C4.wav`
2. **Set root note**: 60 (C4)
3. **Map range**: C3 to C5 (48-72)
4. **Result**: 
   - C3 plays at 0.5x speed (octave down)
   - C4 plays at original pitch
   - C5 plays at 2.0x speed (octave up)

### **Creating Multi-Octave Instruments**
1. **Sample at C4**: Map to C2-C6 (24-84)
2. **Wide range**: 5 octaves from single sample
3. **Smooth transitions**: Automatic pitch calculation
4. **Natural sound**: High-quality transposition preserves timbre

### **Fine-Tuning for Ensemble**
1. **Tune individual samples**: ±50 cents for ensemble blend
2. **Detune for richness**: Slight variations create depth
3. **Temperament adjustments**: Non-equal temperament tuning

---

## 🚀 **Advanced Features**

### **Real-Time Preview**
- **Instant feedback**: Hear changes as you adjust
- **Any test note**: Preview transposition at any pitch
- **Visual feedback**: See pitch ratios and cent values

### **Automatic Root Detection**
Smart algorithms attempt to detect root notes from:
- **Filename patterns**: "Piano_C4.wav", "Violin_A3.wav"
- **Range analysis**: Uses middle of mapped range
- **User override**: Manual adjustment always possible

### **Temporary File Management**
- **Automatic cleanup**: Removes processed audio files
- **Memory efficient**: Only keeps necessary cached data
- **Cross-platform**: Works on Windows, macOS, and Linux

### **Integration with Sample Groups**
- **Velocity layers**: Each layer can have different tuning
- **Round-robin**: Variations can be tuned independently
- **Blend controls**: Mix samples with different transpositions

---

## 📊 **Performance Considerations**

### **CPU Usage**
- **Librosa**: Higher CPU, better quality
- **Pydub**: Lower CPU, good quality
- **Basic**: Minimal CPU, no processing

### **Memory Usage**
- **Temporary files**: Created for processed audio
- **Auto-cleanup**: Removes files after playback
- **Caching**: Efficient reuse of processed samples

### **Latency**
- **Processing time**: Depends on sample length and method
- **Real-time capable**: Fast enough for interactive use
- **Optimization**: Shorter samples process faster

---

## 💡 **Best Practices**

### **Root Note Selection**
- **Use actual pitch**: Set root to the sample's recorded pitch
- **Consider timbre**: Some samples work better at specific ranges
- **Test extensively**: Play across the full range to check quality

### **Mapping Ranges**
- **Conservative ranges**: ±1 octave usually sounds natural
- **Overlap carefully**: Avoid conflicts between different samples
- **Consider timbre changes**: Extreme transposition may sound unnatural

### **Tuning Strategy**
- **Start with detection**: Use auto-detect as starting point
- **Fine-tune by ear**: Adjust cents for perfect intonation
- **Test in context**: Check tuning against other instruments

### **Quality Optimization**
- **Install libraries**: Get librosa for best results
- **Shorter samples**: Process faster and use less memory
- **Reasonable ranges**: Extreme transposition may degrade quality

---

## 🔍 **Troubleshooting**

### **No Transposition Occurring**
- **Check libraries**: Install librosa or pydub
- **Verify root note**: Ensure correct root note is set
- **Test preview**: Use preview button to verify

### **Poor Audio Quality**
- **Upgrade method**: Install librosa for better quality
- **Reduce range**: Limit transposition to ±1 octave
- **Check sample quality**: Higher quality input = better output

### **Slow Performance**
- **Optimize samples**: Use shorter samples when possible
- **Check CPU usage**: Monitor system resources
- **Consider pydub**: Faster processing, acceptable quality

---

## 🎵 **Result: Professional Transposition**

The transposition system now provides:

✅ **Automatic pitch calculation** based on root notes
✅ **High-quality audio processing** with multiple methods
✅ **Visual feedback** showing transposition direction
✅ **Interactive controls** for fine-tuning
✅ **Real-time preview** of transposed samples
✅ **Professional tooltips** with detailed information
✅ **Seamless integration** with existing sample mapping

Your DecentSampler presets now have **realistic transposition** that makes single samples sound natural across the entire keyboard range! 🎹✨
# DecentSampler Frontend - Accessibility Features

This document describes the comprehensive accessibility features implemented to make the DecentSampler Frontend application usable by people with various forms of color vision deficiency and visual impairments.

## Overview

The accessibility features are designed to provide alternative visual cues that don't rely solely on color differences. This ensures the application is usable by people with:

- Protanopia (red-blindness)
- Deuteranopia (green-blindness) 
- Tritanopia (blue-blindness)
- Protanomaly (red-weakness)
- Deuteranomaly (green-weakness)
- Tritanomaly (blue-weakness)
- Low vision or contrast sensitivity

## Key Features

### 1. Visual Patterns and Textures

Instead of relying only on colors, UI elements use distinct visual patterns:

- **Solid fills** - Basic elements
- **Dot patterns** - Secondary elements  
- **Horizontal lines** - Velocity layers
- **Vertical lines** - Sample ranges
- **Diagonal lines** - Transposition indicators
- **Cross-hatch** - Complex mappings
- **Zigzag patterns** - Special states
- **Checkerboard** - Alternative elements
- **Wave patterns** - Audio-related elements
- **Triangle patterns** - Navigation elements

### 2. Symbol Indicators

Symbolic representations complement visual patterns:

- **Status symbols**: ✓ (success), ⚠ (warning), ✗ (error), ℹ (info)
- **Musical symbols**: ♪ (note), ♯ (sharp), ♭ (flat)
- **Directional symbols**: ↑ ↓ ← → (transposition directions)
- **Shape symbols**: ● ■ ▲ ♦ ★ (categorization)
- **Velocity symbols**: pp, mp, mf, ff (dynamics)
- **Playback symbols**: ▶ (play), ⏸ (pause), ⏹ (stop)

### 3. Colorblind-Safe Palette

A carefully selected color palette based on research by Paul Tol:

- **Blue** (#0173B2) - Primary accent
- **Orange** (#DE8F05) - Secondary accent  
- **Green** (#029E73) - Success states
- **Red** (#D55E00) - Error states
- **Purple** (#CC78BC) - Special elements
- **Brown** (#CA9161) - Neutral elements
- **Pink** (#FBAFE4) - Highlighting
- **Gray** (#949494) - Disabled states
- **Yellow** (#ECE133) - Warnings
- **Light Blue** (#56B4E9) - Information

### 4. High Contrast Mode

Enhanced contrast ratios for better visibility:

- Bold text weights
- Thicker borders and outlines
- Increased size for small elements
- Enhanced focus indicators
- Stronger color differentiation

## Component-Specific Features

### Piano Keyboard

**Standard Mode:**
- Color-coded sample mapping overlays
- Gradient fills for ranges
- Colored stripes for mapped keys

**Accessible Mode:**
- Pattern overlays (dots, lines, cross-hatch) for each mapping
- Symbol indicators (●, ■, ▲, ♦) on mapped keys
- Enhanced transposition arrows with background fills
- Larger velocity layer indicators with patterns
- Pattern-based root note markers

### Sample Mapping Table

**Standard Mode:**
- Status text indicators
- Color-coded filename display

**Accessible Mode:**
- Visual indicator column with pattern icons
- Symbol-enhanced status messages
- Pattern thumbnails showing mapping identity
- Enhanced tooltips with accessibility information

### Audio Preview Widget

**Standard Mode:**
- Color-coded status text
- Standard playback buttons

**Accessible Mode:**
- Status symbols (▶ ✓ ⚠ ✗) alongside text
- Enhanced button symbols
- Accessible color coding for status messages
- Pattern-based waveform visualization

### Legend Widget

**Standard Mode:**
- Simple color bars
- Basic sample information

**Accessible Mode:**
- Pattern previews alongside colors
- Symbol indicators for each mapping
- Enhanced tooltips explaining patterns
- Larger visual elements for better visibility

## Color Vision Simulation

The application includes a color vision simulator that shows how colors appear to users with different types of color vision deficiency. This helps developers and users understand why alternative visual cues are necessary.

### Supported Vision Types:
- Normal color vision
- Protanopia (red-blind)
- Deuteranopia (green-blind) 
- Tritanopia (blue-blind)
- Protanomaly (red-weak)
- Deuteranomaly (green-weak)
- Tritanomaly (blue-weak)

## User Controls

### Accessibility Settings Panel

Users can configure accessibility options through a dedicated settings panel:

**General Settings:**
- Enable/disable colorblind-friendly mode
- Toggle high contrast mode
- Enhanced status indicators option

**Color Vision Support:**
- Select specific color vision type
- Interactive color discrimination test
- Real-time simulation preview

**Visual Indicators:**
- Enable/disable visual patterns
- Enable/disable symbol indicators  
- Adjust pattern density (30-100%)
- Configure symbol size (8-24px)

**Preview & Testing:**
- Live pattern preview
- Test current settings
- Reset to defaults option

### Quick Toggle

A global toggle button allows users to quickly switch between normal and accessible modes without diving into detailed settings.

## Technical Implementation

### Architecture

The accessibility system is built around several key components:

1. **AccessibilitySettings** - Global configuration state
2. **AccessibilityIndicator** - Creates visual indicators and patterns
3. **PatternGenerator** - Generates pattern brushes and textures
4. **ColorVisionSimulator** - Simulates color vision deficiency
5. **ThemeManager** - Integrates accessibility with the theming system

### Pattern Generation

Patterns are procedurally generated using PyQt5's painting system:

```python
# Example: Dot pattern generation
def _draw_dots(painter, size, density):
    dot_size = max(1, int(size * density * 0.3))
    spacing = max(2, int(size * 0.5))
    for x in range(0, size, spacing):
        for y in range(0, size, spacing):
            painter.drawEllipse(x, y, dot_size, dot_size)
```

### Symbol Integration

Symbols are integrated at the component level:

```python
# Example: Status symbol integration
symbol = get_status_symbol("success") if accessibility_enabled else ""
status_text = f"{symbol} Operation completed"
```

### Color Safety

All colors are tested for distinguishability across different vision types:

```python
# Test color accessibility
results = ColorVisionSimulator.test_color_accessibility(color1, color2)
# Returns dict with distinguishability for each vision type
```

## Testing

### Test Suite

A comprehensive test application (`test_accessibility.py`) demonstrates all accessibility features:

- Interactive piano keyboard with test mappings
- Color vision simulation with real-time updates
- Pattern demonstration grid
- Audio preview testing
- Live settings panel

### Running Tests

```bash
# Run the accessibility test suite
python test_accessibility.py
```

### Manual Testing Checklist

1. **Color Discrimination Test**
   - View test colors in normal mode
   - Switch between different vision types
   - Verify patterns provide clear distinction

2. **Pattern Recognition**
   - Enable accessibility mode
   - Check all UI elements have distinct patterns
   - Verify patterns are clearly visible

3. **Symbol Clarity**
   - Test with different symbol sizes
   - Verify symbols are readable at all sizes
   - Check symbol contrast against backgrounds

4. **High Contrast Mode**
   - Enable high contrast
   - Verify all text is readable
   - Check border and outline visibility

## Best Practices

### For Developers

1. **Never rely solely on color** - Always provide alternative visual cues
2. **Test with simulation** - Use the color vision simulator regularly
3. **Use semantic symbols** - Choose symbols that relate to their meaning
4. **Ensure sufficient contrast** - Follow WCAG guidelines for contrast ratios
5. **Make it configurable** - Allow users to adjust settings to their needs

### For Users

1. **Configure for your needs** - Use the settings panel to optimize the interface
2. **Test different modes** - Try various combinations to find what works best
3. **Use the simulator** - Understanding your vision type helps optimize settings
4. **Provide feedback** - Report accessibility issues or suggestions

## Future Enhancements

Potential improvements for future versions:

1. **Audio cues** - Sound feedback for important visual changes
2. **Keyboard navigation** - Full keyboard accessibility
3. **Screen reader support** - ARIA labels and descriptions
4. **Customizable patterns** - User-defined pattern library
5. **Animation controls** - Reduced motion options
6. **Font scaling** - Dynamic text size adjustment

## Standards Compliance

This implementation aims to meet or exceed:

- **WCAG 2.1 AA** - Web Content Accessibility Guidelines
- **Section 508** - US Federal accessibility requirements  
- **EN 301 549** - European accessibility standard

## Resources and References

- [Paul Tol's Colour Schemes](https://personal.sron.nl/~pault/) - Colorblind-safe palettes
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Web accessibility standards
- [Color Universal Design](https://jfly.uni-koeln.de/color/) - Color vision research
- [Accessible Colors](https://accessible-colors.com/) - Color contrast testing

## Support

For accessibility-related issues or suggestions:

1. Check the settings panel for configuration options
2. Run the test suite to isolate issues
3. Report bugs with specific vision type and settings
4. Include screenshots when possible

---

**Note**: This accessibility implementation is designed to be comprehensive but not intrusive. Users who don't need these features can simply leave them disabled, while those who benefit from them have full control over their configuration.
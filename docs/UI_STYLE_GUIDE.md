# DecentSampler Frontend UI Style Guide

## Overview
This document outlines the design system and UI/UX guidelines for the DecentSampler Frontend application. Our design philosophy emphasizes clarity, consistency, and professional aesthetics with a modern dark theme.

## Design Principles

### 1. **Clarity First**
- Every UI element should have a clear purpose
- Labels should be descriptive and avoid abbreviations
- Visual hierarchy guides users through workflows

### 2. **Consistency**
- Uniform styling across all components
- Predictable interactions and behaviors
- Standardized spacing and sizing

### 3. **Professional Aesthetics**
- Modern dark theme optimized for extended use
- Subtle animations and transitions
- Clean, uncluttered layouts

## Color Palette

### Primary Colors
- **Primary Background**: `#1a1a1a` - Main application background
- **Secondary Background**: `#252525` - Panel and input backgrounds
- **Panel Background**: `#2a2a2a` - Card and section backgrounds
- **Hover Background**: `#353535` - Interactive element hover state
- **Pressed Background**: `#303030` - Active/pressed state

### Accent Colors
- **Primary Accent**: `#4a9eff` - Primary actions and highlights
- **Accent Hover**: `#6bb3ff` - Hover state for accented elements
- **Accent Pressed**: `#3a8eee` - Pressed state for accented elements

### Status Colors
- **Success**: `#4caf50` - Successful operations
- **Warning**: `#ff9800` - Warnings and cautions
- **Error**: `#f44336` - Errors and critical issues
- **Info**: `#2196f3` - Informational messages

### Text Colors
- **Primary Text**: `#ffffff` - Main content and headers
- **Secondary Text**: `#b0b0b0` - Secondary information
- **Disabled Text**: `#666666` - Disabled state
- **Hint Text**: `#888888` - Placeholder and hints

### Border Colors
- **Default Border**: `#3a3a3a` - Standard borders
- **Hover Border**: `#4a4a4a` - Hover state borders
- **Focus Border**: `#4a9eff` - Focused input borders

## Typography

### Font Family
- Primary: "Segoe UI", Arial, sans-serif

### Font Sizes
- **H1 (Main Headers)**: 18px, bold
- **H2 (Section Headers)**: 14px, semibold (600)
- **H3 (Subsections)**: 12px, semibold (600)
- **Body**: 12px, regular (400)
- **Small**: 11px, regular (400)
- **Tiny**: 10px, regular (400)

### Font Weights
- **Bold**: 700 - Major headers
- **Semibold**: 600 - Section headers, emphasis
- **Medium**: 500 - Button text
- **Regular**: 400 - Body text
- **Light**: 300 - Not currently used

## Spacing System

Based on an 8px grid system:
- **Tiny**: 2px - Minimal spacing
- **Small**: 4px - Tight spacing
- **Medium**: 8px - Standard spacing
- **Large**: 16px - Section spacing
- **XLarge**: 24px - Major section breaks

## Component Standards

### Buttons
- **Height**: 28px (standard), 24px (small), 36px (large)
- **Border Radius**: 4px
- **Padding**: 6px 16px
- **Font**: 11px, medium weight (500)
- **States**:
  - Default: Background `#3a3a3a`, Border `#4a4a4a`
  - Hover: Background `#454545`, Border `#4a9eff`
  - Pressed: Background `#2a2a2a`, Border `#4a9eff`
  - Primary: Background `#4a9eff`, no border

### Input Fields
- **Height**: 32px
- **Border Radius**: 4px
- **Padding**: 6px 8px
- **Background**: `#252525`
- **Border**: 1px solid `#3a3a3a`
- **Focus Border**: `#4a9eff`

### Cards/Panels
- **Background**: `#2a2a2a`
- **Border**: 1px solid `#3a3a3a`
- **Border Radius**: 8px (cards), 4px (panels)
- **Padding**: 12px
- **Shadow**: Optional elevation effect

### Sliders
- **Track Height**: 6px
- **Handle Size**: 16x16px
- **Border Radius**: 50% (circular handles)
- **Colors**: Track `#252525`, Handle `#4a9eff`

### Custom Components

#### LabeledKnob
- **Size**: 48x48px (knob), 68x88px (total with label)
- **Visual Style**: Circular with value arc
- **Interaction**: Vertical drag to adjust

#### CollapsiblePanel
- **Header Height**: 32px
- **Animation**: 200ms ease-in-out
- **Icon**: ▶ (collapsed) / ▼ (expanded)

#### ParameterCard
- **Elevation**: Subtle shadow effect
- **Hover Effect**: Border color change to accent

## Layout Guidelines

### Responsive Breakpoints
- **Large**: > 1900px - Full layout
- **Medium**: 1600-1900px - Compact spacing
- **Small**: 1400-1600px - Reduced panel sizes
- **Compact**: < 1400px - Minimum viable layout

### Panel Organization
1. **Main Window**: Maximized by default
2. **Left Dock**: Sample mapping and groups
3. **Center**: Preview canvas
4. **Right Dock**: Properties panel
5. **Bottom**: Piano keyboard

### Visual Hierarchy
1. Use size and weight to establish importance
2. Group related controls with cards/panels
3. Maintain consistent alignment
4. Use whitespace to separate sections

## Interaction Patterns

### Hover Effects
- Subtle background color change
- Border highlight for focusable elements
- Cursor change to pointer for clickable items

### Focus States
- Blue accent border for inputs
- Visible focus ring for keyboard navigation
- Clear tab order through interface

### Feedback
- Visual button press animations
- Progress indicators for long operations
- Success/error state colors
- Tooltips for additional information

## Animation Guidelines

### Duration
- Micro-interactions: 100-150ms
- Panel transitions: 200-300ms
- Loading animations: Continuous

### Easing
- Standard: ease-in-out
- Enter: ease-out
- Exit: ease-in

### Types
- Opacity fades for overlays
- Scale for button presses
- Slide for panel reveals

## Accessibility

### Color Contrast
- Minimum 4.5:1 for normal text
- Minimum 3:1 for large text
- Test with color blindness simulators

### Keyboard Navigation
- All interactive elements keyboard accessible
- Visible focus indicators
- Logical tab order
- Keyboard shortcuts for common actions

### Screen Reader Support
- Descriptive labels for all controls
- Accessible names for complex widgets
- Status announcements for async operations

## Implementation Notes

### Theme System
- Centralized theme management via `theme_manager.py`
- Global stylesheet in `main_theme.qss`
- Dynamic theme switching capability

### Custom Components
- Reusable widgets in `custom_components.py`
- Consistent styling through theme integration
- Encapsulated behavior and appearance

### Best Practices
1. Always use theme colors, never hardcode
2. Apply consistent spacing using theme constants
3. Test on multiple screen sizes
4. Validate accessibility compliance
5. Document any deviations from guidelines

## Future Enhancements

### Planned Features
- Light theme variant
- User-customizable accent colors
- Advanced animation system
- Enhanced accessibility modes

### Performance Optimizations
- Lazy loading for complex panels
- Virtualized lists for large datasets
- GPU-accelerated rendering where applicable

## Conclusion

This style guide ensures a cohesive, professional user experience across the DecentSampler Frontend. By following these guidelines, we maintain consistency while allowing for future growth and enhancement of the interface.
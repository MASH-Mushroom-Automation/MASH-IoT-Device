# MASH Touchscreen UI - Assets

This directory contains fonts, icons, and images for the Kivy UI.

## Fonts

Recommended: **Roboto** family (free, open-source, excellent readability)

Download from: https://fonts.google.com/specimen/Roboto

Required files:
- `Roboto-Regular.ttf`
- `Roboto-Bold.ttf`
- `Roboto-Light.ttf`

Place in `fonts/` directory.

## Icons

Use **Material Design Icons** for consistency.

Download from: https://materialdesignicons.com/

Or use icon fonts like Material Icons.

## Images

- MASH logo (SVG or PNG)
- Mushroom graphics (optional)
- Background patterns (optional)

## Usage in Kivy

```python
# Load font
from kivy.core.text import LabelBase
LabelBase.register(name='Roboto', fn_regular='assets/fonts/Roboto-Regular.ttf')

# Load image
from kivy.uix.image import Image
logo = Image(source='assets/images/mash_logo.png')
```

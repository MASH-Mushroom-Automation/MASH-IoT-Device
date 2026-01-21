"""
MASH IoT Device - Icon Utilities
Helper functions for loading and colorizing SVG icons
"""

from pathlib import Path
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QSize


def load_svg_icon(icon_path, size: int = 24, color: str = "#FFFFFF") -> QPixmap:
    """
    Load an SVG icon and colorize it
    
    Args:
        icon_path: Path to the SVG file (str or Path object)
        size: Size of the icon in pixels
        color: Hex color code to apply to the icon
        
    Returns:
        QPixmap with the colorized icon
    """
    # Convert to Path object if string
    if isinstance(icon_path, str):
        icon_path = Path(icon_path)
    
    if not icon_path.exists():
        # Return empty pixmap if icon doesn't exist
        return QPixmap(size, size)
    
    # Load SVG
    renderer = QSvgRenderer(str(icon_path))
    
    # Create pixmap with transparency
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Render SVG to pixmap
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    # Colorize the icon
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(colored_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)
    
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(colored_pixmap.rect(), QColor(color))
    painter.end()
    
    return colored_pixmap


def create_icon(icon_path: Path, size: int = 24, color: str = "#FFFFFF") -> QIcon:
    """
    Create a QIcon from an SVG file with colorization
    
    Args:
        icon_path: Path to the SVG file
        size: Size of the icon in pixels
        color: Hex color code to apply to the icon
        
    Returns:
        QIcon with the colorized icon
    """
    pixmap = load_svg_icon(icon_path, size, color)
    return QIcon(pixmap)

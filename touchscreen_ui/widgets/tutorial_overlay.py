"""
MASH Touchscreen UI - Tutorial Overlay
Interactive first-run tutorial with sequential tooltips
"""

import json
import os
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.animation import Animation
import config


class TutorialTooltip(FloatLayout):
    """Individual tutorial tooltip with arrow and text"""
    
    def __init__(self, text, position, arrow_direction='bottom', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(300) * config.SCALE_FACTOR, dp(120) * config.SCALE_FACTOR)
        
        # Position relative to screen
        self.pos_hint = position
        
        # Tooltip container
        tooltip_box = BoxLayout(
            orientation='vertical',
            padding=dp(15) * config.SCALE_FACTOR,
            spacing=dp(10) * config.SCALE_FACTOR,
            size_hint=(1, 1)
        )
        
        # Background
        with tooltip_box.canvas.before:
            Color(*self._hex_to_rgb('#4CAF50'), 0.95)
            self.bg_rect = Rectangle(size=tooltip_box.size, pos=tooltip_box.pos)
        
        tooltip_box.bind(size=lambda i, v: setattr(self.bg_rect, 'size', i.size))
        tooltip_box.bind(pos=lambda i, v: setattr(self.bg_rect, 'pos', i.pos))
        
        # Text
        text_label = Label(
            text=text,
            font_size=config.FONTS['size_body'],
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        text_label.bind(size=text_label.setter('text_size'))
        tooltip_box.add_widget(text_label)
        
        self.add_widget(tooltip_box)
        
        # Start with opacity 0 for fade-in animation
        self.opacity = 0
    
    def show(self):
        """Fade in tooltip"""
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self)
    
    def hide(self, callback=None):
        """Fade out tooltip"""
        anim = Animation(opacity=0, duration=0.3)
        if callback:
            anim.bind(on_complete=callback)
        anim.start(self)
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))


class TutorialOverlay(FloatLayout):
    """Tutorial overlay system with sequential tooltips"""
    
    def __init__(self, dashboard_screen, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_screen = dashboard_screen
        self.current_step = 0
        self.config_file = 'data/device_state.json'
        
        # Semi-transparent dark overlay
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.overlay_rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_overlay, pos=self._update_overlay)
        
        # Tutorial steps (position, text)
        self.tutorial_steps = [
            {
                'text': 'Monitor live levels of CO₂, Temperature, and Humidity.\nAim for the "Optimal" indicator.',
                'position': {'center_x': 0.5, 'center_y': 0.6},
                'arrow': 'bottom'
            },
            {
                'text': 'Toggle your fans and humidifier manually\nif the AI suggests an override.\nFind them in the Controls menu.',
                'position': {'center_x': 0.5, 'center_y': 0.4},
                'arrow': 'bottom'
            },
            {
                'text': 'Browse through Alerts for history,\nAI for growth insights,\nand Settings for device config.',
                'position': {'x': dp(100) * config.SCALE_FACTOR, 'center_y': 0.5},
                'arrow': 'left'
            },
            {
                'text': 'Need more help?\nVisit the Help page for maintenance tips\nand tutorials.',
                'position': {'x': dp(100) * config.SCALE_FACTOR, 'center_y': 0.3},
                'arrow': 'left'
            }
        ]
        
        # Current tooltip
        self.current_tooltip = None
        
        # Navigation buttons
        self.button_container = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(dp(300) * config.SCALE_FACTOR, dp(60) * config.SCALE_FACTOR),
            spacing=dp(15) * config.SCALE_FACTOR,
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        
        # Skip button
        self.skip_btn = Button(
            text='Skip Tutorial',
            size_hint=(0.5, 1),
            background_color=self._hex_to_rgb('#333333') + (1,),
            color=(1, 1, 1, 1),
            font_size=config.FONTS['size_small']
        )
        self.skip_btn.bind(on_press=self._skip_tutorial)
        self.button_container.add_widget(self.skip_btn)
        
        # Next button
        self.next_btn = Button(
            text='Next',
            size_hint=(0.5, 1),
            background_color=self._hex_to_rgb('#4CAF50') + (1,),
            color=(1, 1, 1, 1),
            font_size=config.FONTS['size_body'],
            bold=True
        )
        self.next_btn.bind(on_press=self._next_step)
        self.button_container.add_widget(self.next_btn)
        
        self.add_widget(self.button_container)
        
        # Show first step
        self._show_step(0)
    
    def _show_step(self, step_index):
        """Show tutorial step"""
        if step_index >= len(self.tutorial_steps):
            self._complete_tutorial()
            return
        
        self.current_step = step_index
        step = self.tutorial_steps[step_index]
        
        # Remove previous tooltip
        if self.current_tooltip:
            self.remove_widget(self.current_tooltip)
        
        # Create new tooltip
        self.current_tooltip = TutorialTooltip(
            text=step['text'],
            position=step['position'],
            arrow_direction=step.get('arrow', 'bottom')
        )
        
        self.add_widget(self.current_tooltip)
        self.current_tooltip.show()
        
        # Update button text for last step
        if step_index == len(self.tutorial_steps) - 1:
            self.next_btn.text = 'Finish'
    
    def _next_step(self, instance):
        """Go to next tutorial step"""
        self._show_step(self.current_step + 1)
    
    def _skip_tutorial(self, instance):
        """Skip tutorial"""
        self._complete_tutorial()
    
    def _complete_tutorial(self):
        """Complete tutorial and mark as done"""
        # Update device state
        self._update_device_state({'isTutorialDone': True})
        
        # Remove overlay from dashboard
        if self.parent:
            self.parent.remove_widget(self)
    
    def _update_device_state(self, updates):
        """Update device state configuration"""
        try:
            # Load current state
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    state = json.load(f)
            else:
                state = {}
            
            # Apply updates
            state.update(updates)
            
            # Save
            with open(self.config_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"Error updating device state: {e}")
    
    def _update_overlay(self, instance, value):
        """Update overlay rectangle"""
        self.overlay_rect.size = instance.size
        self.overlay_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

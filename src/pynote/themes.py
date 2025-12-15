# src/pynote/themes.py
"""
Theme definitions for PyNote editor.
"""

LIGHT_THEME = {
    'bg': '#FFFFFF',
    'fg': '#000000',
    'select_bg': '#316AC5',
    'select_fg': '#FFFFFF',
    'insert_bg': '#000000',
    'gutter_bg': '#F0F0F0',
    'gutter_fg': '#666666',
    'status_bg': '#E0E0E0',
    'status_fg': '#000000',
    'button_hover': '#CCCCCC',
}

DARK_THEME = {
    'bg': '#1E1E1E',
    'fg': '#D4D4D4',
    'select_bg': '#264F78',
    'select_fg': '#FFFFFF',
    'insert_bg': '#FFFFFF',
    'gutter_bg': '#252526',
    'gutter_fg': '#858585',
    'status_bg': '#a4b0be',
    'status_fg': '#000000',
    'button_hover': '#7f8fa6',
}


def get_theme(name='light'):
    """
    Get theme configuration by name.
    
    Args:
        name: Theme name ('light' or 'dark')
    
    Returns:
        dict: Theme configuration
    """
    if name.lower() == 'dark':
        return DARK_THEME.copy()
    return LIGHT_THEME.copy()


def apply_theme(widget, theme):
    """
    Apply theme to a text widget.
    
    Args:
        widget: Tkinter Text widget
        theme: Theme dictionary
    """
    widget.configure(
        bg=theme['bg'],
        fg=theme['fg'],
        selectbackground=theme['select_bg'],
        selectforeground=theme['select_fg'],
        insertbackground=theme['insert_bg'],
    )

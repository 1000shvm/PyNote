# src/pynote/main.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from . import themes, utils

APP_TITLE = "PyNote"


class PyNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('800x600')
        
        self.settings = utils.load_settings()
        self.current_theme = self.settings.get('theme', 'light')
        
        self._filepath = None
        self._create_icons()
        self._create_widgets()
        self._create_menu()
        self._bind_shortcuts()
        self._apply_theme()

    def _create_widgets(self):
        # Top bar for theme toggle
        self.top_bar = tk.Frame(self)
        self.top_bar.pack(side='top', fill='x')
        self.theme_btn = tk.Button(self.top_bar, command=self.toggle_theme, bd=0, padx=10)
        self.theme_btn.pack(side='right', padx=5, pady=2)
        self.theme_btn.bind('<Enter>', self._on_theme_btn_hover)
        self.theme_btn.bind('<Leave>', self._on_theme_btn_leave)

        # Gutter for line numbers
        self.gutter = tk.Canvas(self, width=40, highlightthickness=0)
        self.gutter.pack(side='left', fill='y')

        # Text widget with scrollbar
        self.text = tk.Text(self, wrap='word', undo=True)
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=self._on_text_scroll)
        self.vsb.pack(side='right', fill='y')
        self.text.pack(side='left', fill='both', expand=True)

        # status bar
        self.status = tk.StringVar()
        self.status.set('Ln 1, Col 0 | Words: 0 | Chars: 0')
        status_bar = ttk.Label(self, textvariable=self.status, anchor='w', style='Status.TLabel')
        status_bar.pack(side='bottom', fill='x')

        # update cursor position
        self.text.bind('<KeyRelease>', self._update_status)
        self.text.bind('<ButtonRelease>', self._update_status)
        self.text.bind('<Configure>', lambda e: self._redraw_line_numbers())

    def _create_icons(self):
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        self.icons = {}
        icon_files = {
            'new': 'new.png',
            'open': 'open.png',
            'save': 'save.png',
            'save_as': 'save_as.png',
            'exit': 'exit.png'
        }

        for key, filename in icon_files.items():
            base, ext = os.path.splitext(filename)
            theme_filename = f"{base}_dark{ext}" if self.current_theme == 'dark' else filename
            path = os.path.join(assets_dir, theme_filename)
            
            is_fallback = False
            if not os.path.exists(path) and self.current_theme == 'dark':
                path = os.path.join(assets_dir, filename)
                is_fallback = True
            
            self.icons[key] = None
            if os.path.exists(path):
                try:
                    img = tk.PhotoImage(file=path)
                    factor = max(img.width() // 16, img.height() // 16)
                    if factor > 1:
                        img = img.subsample(factor, factor)
                    if is_fallback:
                        img = self._invert_image(img)
                    self.icons[key] = img
                except Exception:
                    pass

        self.icon_new = self.icons['new']
        self.icon_open = self.icons['open']
        self.icon_save = self.icons['save']
        self.icon_save_as = self.icons['save_as']
        self.icon_exit = self.icons['exit']

    def _invert_image(self, img):
        try:
            inverted = tk.PhotoImage(width=img.width(), height=img.height())
            for x in range(img.width()):
                for y in range(img.height()):
                    if not img.transparency_get(x, y):
                        r, g, b = img.get(x, y)
                        inverted.put(f'#{255-r:02x}{255-g:02x}{255-b:02x}', (x, y))
            return inverted
        except Exception:
            return img

    def _create_menu(self):
        menu = tk.Menu(self)
        self.filemenu = tk.Menu(menu, tearoff=0)
        self.filemenu.add_command(label='New', command=self.new_file, image=self.icon_new, compound='left', accelerator='Ctrl+N')
        self.filemenu.add_command(label='Open', command=self.open_file, image=self.icon_open, compound='left')
        self.filemenu.add_command(label='Save', command=self.save_file, image=self.icon_save, compound='left')
        self.filemenu.add_command(label='Save As', command=self.save_as, image=self.icon_save_as, compound='left')
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Exit', command=self.quit, image=self.icon_exit, compound='left')
        menu.add_cascade(label='File', menu=self.filemenu)
        
        self.config(menu=menu)

    def _bind_shortcuts(self):
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-n>', lambda e: self.new_file())
        self.bind('<Control-z>', lambda e: self.text.event_generate('<<Undo>>'))
        self.bind('<Control-y>', lambda e: self.text.event_generate('<<Redo>>'))

    def new_file(self):
        if self._confirm_discard():
            self.text.delete('1.0', tk.END)
            self._filepath = None
            self.title(APP_TITLE)
            self._update_status()

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            filetypes=[('Text Files', '*.txt;*.md;*.py'), ('All Files', '*.*')]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.text.delete('1.0', tk.END)
                self.text.insert('1.0', data)
                self._filepath = path
                self.title(f"{APP_TITLE} - {path}")
                self._update_status()
            except Exception as e:
                messagebox.showerror('Error', f'Failed to open file: {str(e)}')

    def save_file(self):
        if self._filepath:
            try:
                with open(self._filepath, 'w', encoding='utf-8') as f:
                    f.write(self.text.get('1.0', tk.END))
                self.text.edit_modified(False)
                messagebox.showinfo('Saved', 'File saved successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt;*.md;*.py'), ('All Files', '*.*')]
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.text.get('1.0', tk.END))
                self._filepath = path
                self.title(f"{APP_TITLE} - {path}")
                self.text.edit_modified(False)
                messagebox.showinfo('Saved', 'File saved successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')

    def _on_text_scroll(self, *args):
        self.vsb.set(*args)
        self._redraw_line_numbers()

    def _redraw_line_numbers(self):
        self.gutter.delete('all')
        theme = themes.get_theme(self.current_theme)
        
        try:
            start_idx = self.text.index("@0,0")
            end_idx = self.text.index(f"@0,{self.text.winfo_height()}")
        except tk.TclError:
            return

        start_line = int(start_idx.split('.')[0])
        end_line = int(end_idx.split('.')[0])

        for line in range(start_line, end_line + 2):
            dline = self.text.dlineinfo(f"{line}.0")
            if dline:
                y = dline[1]
                self.gutter.create_text(35, y, anchor='ne', text=str(line), 
                                      fill=theme['gutter_fg'], font=self.text.cget('font'))

    def _update_status(self, event=None):
        idx = self.text.index(tk.INSERT).split('.')
        line = idx[0]
        col = idx[1]
        
        content = self.text.get('1.0', tk.END)
        words = utils.count_words(content)
        chars = utils.count_chars(content)
        self.status.set(f'Ln {line}, Col {col} | Words: {words} | Chars: {chars}')
        self._redraw_line_numbers()

    def _confirm_discard(self):
        if self.text.edit_modified():
            resp = messagebox.askyesnocancel(
                'Unsaved changes',
                'You have unsaved changes. Save before continuing?'
            )
            if resp is None:
                return False
            if resp:
                self.save_file()
        return True

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.settings['theme'] = self.current_theme
        utils.save_settings(self.settings)
        self._create_icons()
        self._create_menu()
        self._apply_theme()

    def _apply_theme(self):
        theme = themes.get_theme(self.current_theme)
        themes.apply_theme(self.text, theme)
        
        self.configure(bg=theme['bg'])
        self.top_bar.configure(bg=theme['bg'])
        self.gutter.configure(bg=theme['gutter_bg'])
        
        # Update button
        btn_text = 'Light' if self.current_theme == 'dark' else 'Dark'
        self.theme_btn.configure(
            text=btn_text,
            bg=theme['status_bg'],
            fg=theme['status_fg'],
            activebackground=theme['select_bg'],
            activeforeground=theme['select_fg']
        )
        
        # Configure styles
        style = ttk.Style()
        style.configure('Status.TLabel', background=theme['status_bg'], foreground=theme['status_fg'])
        style.configure("Vertical.TScrollbar", background=theme['status_bg'], troughcolor=theme['gutter_bg'], arrowcolor=theme['fg'])
        
        # Configure menus
        self.filemenu.configure(
            bg=theme['bg'],
            fg=theme['fg'],
            activebackground=theme['select_bg'],
            activeforeground=theme['select_fg']
        )
        self._redraw_line_numbers()

    def _on_theme_btn_hover(self, event):
        theme = themes.get_theme(self.current_theme)
        self.theme_btn.configure(bg=theme['button_hover'])

    def _on_theme_btn_leave(self, event):
        theme = themes.get_theme(self.current_theme)
        self.theme_btn.configure(bg=theme['status_bg'])


if __name__ == '__main__':
    app = PyNoteApp()
    app.mainloop()

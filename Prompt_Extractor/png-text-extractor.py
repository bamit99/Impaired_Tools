import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import struct
import re
from PIL import Image, ImageTk

def read_png_chunks(file_path):
    chunks = []
    with open(file_path, 'rb') as f:
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")
        while True:
            try:
                length = struct.unpack('>I', f.read(4))[0]
                chunk_type = f.read(4)
                data = f.read(length)
                f.seek(4, 1)  # Skip CRC
                chunks.append((chunk_type, data))
                if chunk_type == b'IEND':
                    break
            except struct.error:
                break
    return chunks

def extract_stable_diffusion_metadata(file_path):
    chunks = read_png_chunks(file_path)
    for chunk_type, data in chunks:
        if chunk_type == b'tEXt':
            try:
                key, value = data.split(b'\0', 1)
                if key == b'parameters':
                    return value.decode('utf-8', errors='replace')
            except:
                pass
    return None

def format_metadata(metadata):
    parts = metadata.split("Negative prompt:", 1)
    
    if len(parts) > 1:
        prompt = parts[0].strip()
        rest = "Negative prompt:" + parts[1]
    else:
        match = re.search(r'\b\w+:', metadata)
        if match:
            split_index = match.start()
            prompt = metadata[:split_index].strip()
            rest = metadata[split_index:]
        else:
            prompt = metadata.strip()
            rest = ""
    
    formatted_rest = re.sub(r'([^,\s]+):', r'\n\1:', rest)
    return prompt, formatted_rest.strip()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stable Diffusion PNG Metadata Explorer")
        self.geometry("1400x800")
        self.dark_mode = False
        self.thumbnail_size = (100, 100)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main PanedWindow
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.grid(row=0, column=0, sticky="nsew")

        # Left panel with folder tree
        left_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(left_panel, weight=1)

        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        ttk.Button(left_panel, text="Browse", command=self.browse_folder).grid(row=0, column=0, pady=(0, 5), sticky="ew")

        self.tree = ttk.Treeview(left_panel)
        self.tree.heading('#0', text='Folder Explorer', anchor='w')
        self.tree.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)

        # Right PanedWindow
        right_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(right_paned, weight=2)

        # Middle panel with thumbnails
        middle_panel = ttk.Frame(right_paned)
        right_paned.add(middle_panel, weight=1)

        middle_panel.grid_rowconfigure(0, weight=1)
        middle_panel.grid_columnconfigure(0, weight=1)

        self.thumbnail_canvas = tk.Canvas(middle_panel)
        self.thumbnail_canvas.grid(row=0, column=0, sticky="nsew")

        thumbnail_scrollbar = ttk.Scrollbar(middle_panel, orient="vertical", command=self.thumbnail_canvas.yview)
        thumbnail_scrollbar.grid(row=0, column=1, sticky="ns")
        self.thumbnail_canvas.configure(yscrollcommand=thumbnail_scrollbar.set)

        self.thumbnail_frame = ttk.Frame(self.thumbnail_canvas)
        self.thumbnail_canvas.create_window((0, 0), window=self.thumbnail_frame, anchor="nw")

        self.thumbnail_frame.bind("<Configure>", self.on_frame_configure)

        # Right panel
        right_panel = ttk.Frame(right_paned)
        right_paned.add(right_panel, weight=1)

        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Image preview
        self.preview_label = ttk.Label(right_panel)
        self.preview_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Prompt display and copy button
        self.prompt_text = tk.Text(right_panel, wrap=tk.WORD, height=3)
        self.prompt_text.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        ttk.Button(right_panel, text="Copy Prompt", command=self.copy_prompt).grid(row=1, column=1, padx=(5, 0), sticky="ne")

        # Rest of metadata display
        self.result_text = tk.Text(right_panel, wrap=tk.WORD)
        self.result_text.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Dark mode toggle
        ttk.Button(self, text="Toggle Dark Mode", command=self.toggle_dark_mode).grid(row=1, column=0, pady=5)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_tree(folder_path)

    def populate_tree(self, path):
        self.tree.delete(*self.tree.get_children())
        self.tree.insert('', 'end', path, text=path, open=True)
        self.process_directory(path)

    def process_directory(self, parent):
        for item in os.listdir(parent):
            full_path = os.path.join(parent, item)
            if os.path.isdir(full_path):
                self.tree.insert(parent, 'end', full_path, text=item, open=False)
                self.tree.insert(full_path, 'end', full_path + '|dummy', text='')
            elif item.lower().endswith('.png'):
                self.tree.insert(parent, 'end', full_path, text=item)

    def open_node(self, event):
        selected_item = self.tree.focus()
        children = self.tree.get_children(selected_item)
        if children and self.tree.item(children[0])['text'] == '':
            self.tree.delete(children[0])
            self.process_directory(selected_item)
        self.display_thumbnails(selected_item)

    def item_selected(self, event):
        selected_item = self.tree.focus()
        if os.path.isfile(selected_item) and selected_item.lower().endswith('.png'):
            self.display_metadata(selected_item)
            self.display_image_preview(selected_item)
        elif os.path.isdir(selected_item):
            self.display_thumbnails(selected_item)

    def display_thumbnails(self, directory):
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        for item in os.listdir(directory):
            if item.lower().endswith('.png'):
                full_path = os.path.join(directory, item)
                try:
                    img = Image.open(full_path)
                    img.thumbnail(self.thumbnail_size)
                    photo = ImageTk.PhotoImage(img)
                    btn = ttk.Button(self.thumbnail_frame, image=photo, command=lambda p=full_path: self.on_thumbnail_click(p))
                    btn.image = photo
                    btn.grid(row=row, column=col, padx=5, pady=5)
                    col += 1
                    if col > 4:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error loading thumbnail for {item}: {e}")

        self.thumbnail_frame.update_idletasks()
        self.thumbnail_canvas.config(scrollregion=self.thumbnail_canvas.bbox("all"))

    def on_thumbnail_click(self, file_path):
        self.display_metadata(file_path)
        self.display_image_preview(file_path)

    def display_image_preview(self, file_path):
        try:
            img = Image.open(file_path)
            img.thumbnail((300, 300))  # Adjust size as needed
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo)
            self.preview_label.image = photo
        except Exception as e:
            print(f"Error displaying preview for {file_path}: {e}")

    def on_frame_configure(self, event):
        self.thumbnail_canvas.configure(scrollregion=self.thumbnail_canvas.bbox("all"))

    def display_metadata(self, file_path):
        try:
            metadata = extract_stable_diffusion_metadata(file_path)
            if metadata:
                prompt, rest = format_metadata(metadata)
                self.prompt_text.delete(1.0, tk.END)
                self.prompt_text.insert(tk.END, prompt)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, rest)
            else:
                messagebox.showinfo("No Metadata", "No Stable Diffusion metadata found in the selected PNG file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def copy_prompt(self):
        self.clipboard_clear()
        self.clipboard_append(self.prompt_text.get(1.0, tk.END).strip())
        messagebox.showinfo("Copied", "Prompt copied to clipboard!")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg_color = '#2b2b2b' if self.dark_mode else 'SystemButtonFace'
        fg_color = 'white' if self.dark_mode else 'SystemButtonText'
        style = ttk.Style()
        if self.dark_mode:
            style.theme_use('clam')
            style.configure(".", background=bg_color, foreground=fg_color)
            style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color)
            style.map('Treeview', background=[('selected', '#4a6984')])
            style.configure("TFrame", background=bg_color)
            style.configure("TButton", background=bg_color, foreground=fg_color)
            style.configure("TLabel", background=bg_color, foreground=fg_color)
        else:
            style.theme_use('default')
        self.configure(bg=bg_color)
        self.prompt_text.configure(bg=bg_color, fg=fg_color)
        self.result_text.configure(bg=bg_color, fg=fg_color)
        self.thumbnail_canvas.configure(bg=bg_color)

if __name__ == "__main__":
    app = App()
    app.mainloop()

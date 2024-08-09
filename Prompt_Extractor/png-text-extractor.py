import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import struct
import re

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
        self.geometry("1200x700")
        self.create_widgets()
        self.dark_mode = False

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        left_panel = ttk.Frame(self)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
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

        right_panel = ttk.Frame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        self.prompt_text = tk.Text(right_panel, wrap=tk.WORD, height=3)
        self.prompt_text.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        ttk.Button(right_panel, text="Copy Prompt", command=self.copy_prompt).grid(row=0, column=1, padx=(5, 0), sticky="ne")

        self.result_text = tk.Text(right_panel, wrap=tk.WORD)
        self.result_text.grid(row=1, column=0, columnspan=2, sticky="nsew")

        ttk.Button(self, text="Toggle Dark Mode", command=self.toggle_dark_mode).grid(row=1, column=0, columnspan=2, pady=5)

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

    def item_selected(self, event):
        selected_item = self.tree.focus()
        if os.path.isfile(selected_item) and selected_item.lower().endswith('.png'):
            self.display_metadata(selected_item)

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
        bg_color = '#2b2b2b' if self.dark_mode else 'white'
        fg_color = 'white' if self.dark_mode else 'black'
        style = ttk.Style()
        if self.dark_mode:
            style.theme_use('clam')
            style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color)
            style.map('Treeview', background=[('selected', '#4a6984')])
        else:
            style.theme_use('default')
        self.configure(bg=bg_color)
        self.prompt_text.configure(bg=bg_color, fg=fg_color)
        self.result_text.configure(bg=bg_color, fg=fg_color)

if __name__ == "__main__":
    app = App()
    app.mainloop()

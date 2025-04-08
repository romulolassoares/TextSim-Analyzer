import tkinter as tk
from tkinter import filedialog

def select_files():
    files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
    if files:
        for file in files:
            file_listbox.insert(tk.END, file)

root = tk.Tk()
root.title("Seleção de Arquivos")

# Frame para os arquivos selecionados
file_frame = tk.Frame(root)
file_frame.pack(padx=10, pady=10)

# Lista de arquivos selecionados
file_listbox = tk.Listbox(file_frame, selectmode=tk.MULTIPLE, width=50, height=5)
file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar para a lista de arquivos
file_scrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL)
file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Ligação da lista com a scrollbar
file_listbox.config(yscrollcommand=file_scrollbar.set)
file_scrollbar.config(command=file_listbox.yview)

# Botão para selecionar arquivos
select_button = tk.Button(root, text="Selecionar Arquivos", command=select_files)
select_button.pack(pady=10)

# Dropdown de seleção única
options = ["Opção 1", "Opção 2", "Opção 3"]
selected_option = tk.StringVar(root)
selected_option.set(options[0])
option_menu = tk.OptionMenu(root, selected_option, *options)
option_menu.pack(pady=10)

# Dropdown de multiseleção
multi_options = ["Multiseleção 1", "Multiseleção 2", "Multiseleção 3", "Multiseleção 4"]
selected_multi_options = tk.StringVar(root)
selected_multi_options.set([])
multi_option_menu = tk.OptionMenu(root, selected_multi_options, *multi_options, command=lambda x: print(selected_multi_options.get()))
multi_option_menu.pack(pady=10)

# Botão de execução
execute_button = tk.Button(root, text="Executar", command=lambda: print("Executando..."))
execute_button.pack(pady=20)

root.mainloop()

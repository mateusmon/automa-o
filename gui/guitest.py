import tkinter as tk
from tkinter import ttk

long_text = "Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral.Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral. Evidentemente, a necessidade de renovação processual obstaculiza a apreciação da importância do sistema de participação geral."

root = tk.Tk()
root.config(bg="black")
text = tk.Text(root, bg="black", fg="#d9d9d9", font=("Arial", 12), wrap="word", insertbackground="white", highlightthickness=0)
scrollbar = ttk.Scrollbar(root, command=text.yview)

text.configure(yscrollcommand=scrollbar.set)


text.insert("end", long_text)
text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
scrollbar.pack(side="right", fill="y")

root.mainloop()
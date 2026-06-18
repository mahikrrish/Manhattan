import customtkinter

def button_callback():
    print("Button pressed")

app = customtkinter.CTk()
app.title("Manhattan")
app.geometry("1000x1000")

button = customtkinter.CTkButton(app, text='Analyze', command=button_callback)
button.grid(row=0, column=0, padx=100, pady=350, sticky ="ew")
app.grid_columnconfigure(0, weight=1)
app.mainloop()
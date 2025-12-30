from tkinter import*
from time import*

def update():
    time_string = strftime("%I:%M:%S %p")                  # %I is for hour M for mins S sec
    time_label.config(text=time_string)                    # print the time in string format 
    
    day_string = strftime("%A")
    day_label.config(text=day_string)
    
    date_string = strftime("%B %d, %Y")
    date_label.config(text=date_string)
    
    window.after(1000, update)
    
window = Tk()

time_label = Label(window, font= ("Arial", 50), fg= "green", bg= "black")
time_label.pack()

day_label = Label(window, font=("Ink free", 25), fg="dark blue", bg="Grey")
day_label.pack()

date_label = Label(window, font=("ink free", 25))
date_label.pack()

update()                 # iterable function update for every sec 

window.mainloop()     
        
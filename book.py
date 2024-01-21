#Referenced ChatGPT
import tkinter as tk
import requests
import json

def surprise_me():
    response = requests.get('http://127.0.0.1:5000/surprise-me')
    recommendations = json.loads(response.text)
    formatted_recommendations = "\n".join([f"{key}: {value}" for book in recommendations for key, value in book.items()])
    recommendations_text.set(formatted_recommendations)

# Create the main window
window = tk.Tk()
window.title("Book Recommendations App")

# Create and pack widgets
surprise_button = tk.Button(window, text="Surprise Me", command=surprise_me)
surprise_button.pack()

recommendations_text = tk.StringVar()
recommendations_label = tk.Label(window, textvariable=recommendations_text)
recommendations_label.pack()

# Start the Tkinter event loop
window.mainloop()

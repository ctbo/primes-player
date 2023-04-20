import tkinter as tk
import os
import random
from carddict import cardDict

class CardGameGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Card Game")

        self.card_images_folder = 'resources'
        self.card_backs = [f"{i}" for i in cardDict.keys()]
        self.card_fronts = [f"{number}({symbol})" for number, symbols in cardDict.items() for symbol in symbols]
        self.hand = random.sample(self.card_fronts, 5)
        self.opponent_hand = random.sample(self.card_backs, 5)
        self.selected_cards = []

        self.load_card_images()
        self.create_widgets()

    def load_card_images(self):
        self.card_image_objects = {}
        for card in self.card_backs + self.card_fronts:
            image_path = os.path.join(self.card_images_folder, f"{card}.png")
            self.card_image_objects[card] = tk.PhotoImage(file=image_path)

    def create_widgets(self):
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill='both', expand=True)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky='nsew')

        self.label1 = tk.Label(self.left_frame, text="Opponent's cards:")
        self.label1.pack(pady=5)

        self.opponent_cards_frame = tk.Frame(self.left_frame)
        self.opponent_cards_frame.pack(pady=5)

        self.create_opponent_card_labels()

        self.label2 = tk.Label(self.left_frame, text="Your cards:")
        self.label2.pack(pady=5)

        self.cards_frame = tk.Frame(self.left_frame)
        self.cards_frame.pack(pady=5)

        self.create_card_checkbuttons()

        self.play_button = tk.Button(self.left_frame, text="Play selected cards", command=self.play_cards)
        self.play_button.pack(pady=5)

        self.next_turn_button = tk.Button(self.left_frame, text="Next Turn", command=self.replace_cards)
        self.next_turn_button.pack(pady=5)

        self.quit_button = tk.Button(self.left_frame, text="Quit", command=self.master.quit)
        self.quit_button.pack(pady=5)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky='nsew')

        self.log_label = tk.Label(self.right_frame, text="Game Log:")
        self.log_label.pack(pady=5)

        self.scrollbar = tk.Scrollbar(self.right_frame)
        self.scrollbar.pack(side='right', fill='y')

        self.log_text = tk.Text(self.right_frame, wrap='word', yscrollcommand=self.scrollbar.set)
        self.log_text.pack(expand=True, fill='both')
        self.scrollbar.config(command=self.log_text.yview)

        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def create_opponent_card_labels(self):
        self.opponent_card_labels = []
        for card in self.opponent_hand:
            card_label = tk.Label(self.opponent_cards_frame, image=self.card_image_objects[card])
            card_label.pack(side='left')
            self.opponent_card_labels.append(card_label)

    def create_card_checkbuttons(self):
        self.card_vars = [tk.BooleanVar() for _ in self.hand]

        self.card_checkbuttons = []
        for i, card in enumerate(self.hand):
            card_frame = tk.Frame(self.cards_frame)
            card_frame.pack(side='left')

            card_label = tk.Label(card_frame, image=self.card_image_objects[card])
            card_label.pack()

            check_button = tk.Checkbutton(card_frame, variable=self.card_vars[i], onvalue=True, offvalue=False)
            check_button.pack()
            self.card_checkbuttons.append(check_button)

    def play_cards(self):
        self.selected_cards = [card for card, var in zip(self.hand, self.card_vars) if var.get()]
        self.log_message(f"Selected cards: {', '.join(self.selected_cards)}")

    def replace_cards(self):
        # Clear the current card labels and checkbuttons
        for card_label in self.opponent_card_labels:
            card_label.destroy()
        for check_button in self.card_checkbuttons:
            check_button.master.destroy()

        # Replace the hands with new sets of cards
        n = random.randint(3, 10)
        self.hand = random.sample(self.card_fronts, n)
        self.opponent_hand = random.sample(self.card_backs, n)

        # Create the new card labels and checkbuttons for the updated hands
        self.create_opponent_card_labels()
        self.create_card_checkbuttons()

    def log_message(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message+'\n')
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

def main():
    root = tk.Tk()
    gui = CardGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

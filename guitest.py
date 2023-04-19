# this code was written by GPT-4

import tkinter as tk
import os
import random

class CardGameGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Card Game")

        self.card_images_folder = 'card_images'
        self.all_cards = ["AS", "2H", "3D", "4C", "5H", "6D", "7C", "8H", "9D", "10C"]  # Add more cards as needed
        self.hand = random.sample(self.all_cards, 5)
        self.opponent_hand = random.sample(self.all_cards, 5)
        self.selected_cards = []

        self.load_card_images()
        self.create_widgets()

    def load_card_images(self):
        self.card_image_objects = {}
        for card in self.all_cards:
            image_path = "1.png" # os.path.join(self.card_images_folder, f"{card}.png")
            self.card_image_objects[card] = tk.PhotoImage(file=image_path)

    def create_widgets(self):
        self.label1 = tk.Label(self.master, text="Opponent's cards:")
        self.label1.pack()

        self.opponent_cards_frame = tk.Frame(self.master)
        self.opponent_cards_frame.pack()

        self.create_opponent_card_labels()

        self.label2 = tk.Label(self.master, text="Your cards:")
        self.label2.pack()

        self.cards_frame = tk.Frame(self.master)
        self.cards_frame.pack()

        self.create_card_checkbuttons()

        self.play_button = tk.Button(self.master, text="Play selected cards", command=self.play_cards)
        self.play_button.pack()

        self.next_turn_button = tk.Button(self.master, text="Next Turn", command=self.replace_cards)
        self.next_turn_button.pack()

        self.quit_button = tk.Button(self.master, text="Quit", command=self.master.quit)
        self.quit_button.pack()

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
            check_button = tk.Checkbutton(self.cards_frame, image=self.card_image_objects[card], variable=self.card_vars[i], onvalue=True, offvalue=False)
            check_button.pack(side='left')
            self.card_checkbuttons.append(check_button)

    def play_cards(self):
        self.selected_cards = [card for card, var in zip(self.hand, self.card_vars) if var.get()]
        print("Selected cards:", self.selected_cards)

    def replace_cards(self):
        # Clear the current card labels and checkbuttons
        for card_label in self.opponent_card_labels:
            card_label.destroy()
        for check_button in self.card_checkbuttons:
            check_button.destroy()

        # Replace the hands with new sets of cards
        self.hand = random.sample(self.all_cards, random.randint(3, 10))
        self.opponent_hand = random.sample(self.all_cards, random.randint(3, 10))

        # Create the new card labels and checkbuttons for the updated hands
        self.create_opponent_card_labels()
        self.create_card_checkbuttons()

def main():
    root = tk.Tk()
    gui = CardGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

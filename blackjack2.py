########################################################## Blackjack ###########################################################
# -*- coding: utf-8 -*-
# Submitted by : Sheetal Bongale
# Python script simulates a simple command-line Blackjack game implemented using Python and Object Oriented Programming concepts
# System Requirements: Python 3.8 (Python3)
################################################################################################################################

import random
import time
import pygame

clock = pygame.time.Clock()
clock.tick(30)  # Limit to 30 frames per second


# initialize board
pygame.init()
WIDTH, HEIGHT = 800, 600
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (50, 50, 150)
BUTTON_HOVER = (100, 100, 200)
CARD_COLOR = (255, 255, 255)
CARD_TEXT_COLOR = (0, 0, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack GUI")
font = pygame.font.Font(None, 36)
card_font = pygame.font.Font(None, 24)

bankroll = 100  # Starting balance
bet = 0  # Initialize the bet amount

def draw_screen(player_hand=None, dealer_hand=None, show_dealer_hidden=True, show_cards=True, playing=True):
    """
    Handles drawing the entire screen, including the bankroll, cards, and scores.
    If `show_cards` is False, hides the cards and scores.
    """
    # Fill the background
    screen.fill(GREEN)

    # Draw bankroll in the corner
    draw_bankroll()

    if show_cards:
        # Draw cards
        draw_cards(dealer_hand, x_start=50, y_position=50, centered=True, hide_first=show_dealer_hidden)
        draw_cards(player_hand, x_start=50, y_position=400, centered=True)

        # Draw scores
        draw_scores(player_hand, dealer_hand, playing)

    # Update the display
    pygame.display.update()


def draw_wager_message():
    """Displays a message asking the player to choose their wager."""
    wager_font = pygame.font.Font(None, 36)
    message_text = "How much would you like to wager on this hand?"
    message_surf = wager_font.render(message_text, True, WHITE)
    message_rect = message_surf.get_rect(center=(WIDTH / 2, HEIGHT // 2 - 40))  # Position above the buttons
    screen.blit(message_surf, message_rect)

def draw_click_to_wager_message():
    """Displays a message above the red button prompting the player to click."""
    message_font = pygame.font.Font(None, 24)  # Smaller font for the message
    message_text = "Click to wager"
    message_surf = message_font.render(message_text, True, WHITE)
    message_rect = message_surf.get_rect(center=(WIDTH // 2, HEIGHT - 155))  # Position just above the red button
    screen.blit(message_surf, message_rect)

def draw_bankroll():
    """Displays the player's bankroll in the top-left corner of the screen."""
    bankroll_font = pygame.font.Font(None, 40)
    bankroll_text = f"Bankroll: ${bankroll}"
    bankroll_surf = bankroll_font.render(bankroll_text, True, WHITE)
    screen.blit(bankroll_surf, (10, 10))  # Top-left corner


# button class for pygame
class Button:
    def __init__(self, text, pos):
        self.text = text
        self.rect = pygame.Rect(pos[0], pos[1], 100, 50)

    def draw(self):
        """Draws the button on the screen."""
        color = BUTTON_HOVER if self.rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        text_surf = font.render(self.text, True, WHITE)
        screen.blit(text_surf, (self.rect.x + (self.rect.width - text_surf.get_width()) // 2,
                                self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            print(f"{self.text} button clicked!")  # Temporary debug print
            return True
        return False


# Define the updated wager buttons
chip_1_button = Button("$1", (WIDTH // 2 - 250, HEIGHT // 2))  # Leftmost button
chip_5_button = Button("$5", (WIDTH // 2 - 150, HEIGHT // 2))
chip_10_button = Button("$10", (WIDTH // 2 - 50, HEIGHT // 2))
chip_25_button = Button("$25", (WIDTH // 2 + 50, HEIGHT // 2))
chip_50_button = Button("$50", (WIDTH // 2 + 150, HEIGHT // 2))
# Buttons for "Hit" and "Stand"
hit_button = Button("Hit", (WIDTH - 150, HEIGHT - 150))  # Bottom-right corner, higher
stand_button = Button("Stand", (WIDTH - 150, HEIGHT - 80))  # Bottom-right corner, lower
double_button = Button("Double", (WIDTH - 150, HEIGHT - 220))  # Positioned directly above Hit/Stand buttons


class RoundButton:
    def __init__(self, pos):
        self.total = 0
        self.rect = pygame.Rect(pos[0] - 50, pos[1] - 50, 100, 100)  # Circle bounds
        self.color = (200, 0, 0)  # Red color

    def draw(self):
        """Draw the round button."""
        pygame.draw.ellipse(screen, self.color, self.rect)
        pygame.draw.ellipse(screen, WHITE, self.rect, 3)  # White border
        text_surf = font.render(f"${self.total}", True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def update_total(self, amount):
        """Update the total, ensuring it does not exceed the bankroll."""
        global bankroll
        if self.total + amount > bankroll:
            self.total = bankroll  # Cap the total to the bankroll amount
        else:
            self.total += amount

# Instantiate the round button
round_button = RoundButton((WIDTH // 2, HEIGHT - 80))  # Positioned closer to the bottom

class ClearBetButton:
    """A smaller circular button for clearing the wager total."""
    def __init__(self, pos, radius=20):
        self.pos = pos
        self.radius = radius

    def draw(self):
        """Draw the clear bet button."""
        pygame.draw.circle(screen, (0, 0, 0), self.pos, self.radius)  # Black circle
        text = font.render("X", True, WHITE)
        text_rect = text.get_rect(center=self.pos)
        screen.blit(text, text_rect)

    def is_clicked(self, event):
        """Check if the clear bet button is clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            dx, dy = mouse_x - self.pos[0], mouse_y - self.pos[1]
            return (dx ** 2 + dy ** 2) <= self.radius ** 2  # Check if click is within circle radius
        return False

clear_bet_button = ClearBetButton((WIDTH // 2 + 50, HEIGHT - 70))  # Positioned slightly offset bottom-right of the main red button

# Modify the Event Loop to Include Clear Bet Functionality
wager_total = 0  # Track the wager total

suits = ("Spades", "Clubs", "Hearts", "Diamonds")
ranks = (
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
    "A",
)
values = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 11,
}


# CLASS DEFINTIONS:


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return self.rank + " of " + self.suit


class Deck:
    def __init__(self, num_decks=5):  # Default to 5 decks
        self.num_decks = num_decks
        self.deck = []  # Start with an empty list
        for _ in range(self.num_decks):  # Add multiple decks
            for suit in suits:
                for rank in ranks:
                    self.deck.append(Card(suit, rank))

    def __str__(self):
        deck_comp = ""  # Start with an empty string
        for card in self.deck:
            deck_comp += "\n " + card.__str__()  # Add each Card object's print string
        return "The deck has:" + deck_comp

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        return self.deck.pop()


class Hand:
    def __init__(self):
        self.cards = []  # start with an empty list as we did in the Deck class
        self.value = 0  # start with zero value
        self.aces = 0  # add an attribute to keep track of aces

    def add_card(self, card):
        self.cards.append(card)
        self.value += values[card.rank]
        if card.rank == "A":
            self.aces += 1  # add to self.aces

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1


# FUNCTION DEFINITIONS:


def hit(deck, hand):
    hand.add_card(deck.deal())
    hand.adjust_for_ace()


def hit_or_stand(deck, hand):
    global playing

    while True:
        x = input("\nWould you like to Hit or Stand? Enter [h/s] ")

        if x[0].lower() == "h":
            hit(deck, hand)  # hit() function defined above

        elif x[0].lower() == "s":
            print("Player stands. Dealer is playing.")
            playing = False

        else:
            print("Sorry, Invalid Input. Please enter [h/s].")
            continue
        break

# checks for blackjack
def is_blackjack(hand):
    """Returns True if the hand is a blackjack (value = 21 with exactly 2 cards)."""
    return hand.value == 21 and len(hand.cards) == 2


# creates pygame cards
# Show blue-backed cards for the betting phase
def draw_cards(hand, x_start, y_position, centered=False, hide_first=False, reveal_all=False):
    card_width, card_height = 80, 120
    spacing = 20

    # Calculate centered alignment if requested
    if centered:
        total_width = len(hand.cards) * (card_width + spacing) - spacing
        x_position = (WIDTH - total_width) / 2
    else:
        x_position = x_start

    for index, card in enumerate(hand.cards):
        # Face-down card if hide_first is True and reveal_all is False
        if hide_first and index == 0 and not reveal_all:
            pygame.draw.rect(screen, (0, 0, 255), (x_position, y_position, card_width, card_height))  # Blue fill
            pygame.draw.rect(screen, BLACK, (x_position, y_position, card_width, card_height), 2)  # Black border
        else:
            # Draw the card's face
            pygame.draw.rect(screen, CARD_COLOR, (x_position, y_position, card_width, card_height))  # White fill
            pygame.draw.rect(screen, BLACK, (x_position, y_position, card_width, card_height), 2)  # Black border

            # Determine text color based on suit
            text_color = (255, 0, 0) if card.suit in ["Hearts", "Diamonds"] else (0, 0, 0)

            # Draw card rank in the center
            rank_text = card.rank
            rank_font = pygame.font.Font(None, 40)  # Adjusted font size
            rank_surf = rank_font.render(rank_text, True, text_color)
            rank_rect = rank_surf.get_rect(center=(x_position + card_width / 2, y_position + card_height / 2))
            screen.blit(rank_surf, rank_rect)

            # Draw suit symbol in the top-left corner
            suit_font = pygame.font.Font(None, 20)  # Smaller font for suits
            suit_text = card.suit
            suit_surf = suit_font.render(suit_text, True, text_color)
            screen.blit(suit_surf, (x_position + 5, y_position + 5))

        # Increment x_position for the next card
        x_position += card_width + spacing


def get_display_value(hand):
    """Returns a string representation of the hand value, e.g., '6/16' for hands with an ace."""
    if hand.aces > 0 and hand.value <= 21:
        # Display both possible values (e.g., '6/16') if the hand contains an ace
        soft_value = hand.value - 10  # Count one ace as 1 instead of 11
        if soft_value <= 21:  # Only display soft total if valid
            return f"{soft_value}/{hand.value}"
    # Otherwise, just return the total value
    return str(hand.value)


def display_result(message):
    result_font = pygame.font.Font(None, 80)  # Larger font for results
    result_surf = result_font.render(message, True, WHITE)
    result_rect = result_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    pygame.draw.rect(screen, BLACK, result_rect.inflate(20, 20))  # Background box for visibility
    screen.blit(result_surf, result_rect)
    pygame.display.update()
    pygame.time.delay(2000)  # Keep the result on screen for 2 seconds



# updates pygame scores
def draw_scores(player_hand, dealer_hand, playing):
    score_font = pygame.font.Font(None, 50)  # Font for the score text

    # Dealer score: Show only the upcard’s value if the game is ongoing; otherwise show the full score
    if playing:  # Game is ongoing
        dealer_score_text = f"Dealer: {values[dealer_hand.cards[1].rank]}"  # Show only the value of the dealer's upcard
    else:  # Game is over, show full dealer hand value
        dealer_score_text = f"Dealer: {get_display_value(dealer_hand)}"

    dealer_score_surf = score_font.render(dealer_score_text, True, BLACK)
    dealer_score_rect = dealer_score_surf.get_rect(center=(WIDTH / 2, 30))
    screen.blit(dealer_score_surf, dealer_score_rect)

    # Player score: Always show the full value of the hand
    player_score_text = f"Player: {get_display_value(player_hand)}"
    player_score_surf = score_font.render(player_score_text, True, BLACK)
    player_score_rect = player_score_surf.get_rect(center=(WIDTH / 2, 550))
    screen.blit(player_score_surf, player_score_rect)




def show_some(player, dealer):
    print("\nPlayer's Hand:", *player.cards, sep="\n ")
    print("Player's Hand =", player.value)
    print("\nDealer's Hand:")
    print(" <card hidden>")
    print("", dealer.cards[1])


def show_all(player, dealer):
    print("\nPlayer's Hand:", *player.cards, sep="\n ")
    print("Player's Hand =", player.value)
    print("\nDealer's Hand:", *dealer.cards, sep="\n ")
    print("Dealer's Hand =", dealer.value)


def player_busts(player, dealer):
    print("\n--- Player busts! ---")


def player_wins(player, dealer):
    print("\n--- Player has blackjack! You win! ---")


def dealer_busts(player, dealer):
    print("\n--- Dealer busts! You win! ---")


def dealer_wins(player, dealer):
    print("\n--- Dealer wins! ---")


def push(player, dealer):
    print("\nIts a tie!")

# Create & shuffle the deck, deal two cards to each player
deck = Deck()
deck.shuffle()

player_hand = Hand()
player_hand.add_card(deck.deal())
player_hand.add_card(deck.deal())

dealer_hand = Hand()
dealer_hand.add_card(deck.deal())
dealer_hand.add_card(deck.deal())


bet = 0  # Reset the bet for each round
running = True

while running:
    # Reset deck and hands for a new round
    deck = Deck(num_decks=6)  # Use 6 decks
    deck.shuffle()
    player_hand = Hand()
    dealer_hand = Hand()
    player_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())

    # Display the wager selection screen
    betting = True
    # Display the wager selection screen
    betting = True
    while betting:
        # Draw the static background and message
        screen.fill(GREEN)
        draw_wager_message()
        draw_bankroll()

        # Draw wager buttons
        chip_1_button.draw()
        chip_5_button.draw()
        chip_10_button.draw()
        chip_25_button.draw()
        chip_50_button.draw()

        # Draw the red round button showing the accumulated wager
        round_button.draw()

        # Draw the "Click to wager" message
        draw_click_to_wager_message()

        # Draw the clear bet button
        clear_bet_button.draw()

        # Update the screen
        pygame.display.update()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                betting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Update the round button total based on which chip button is clicked
                if chip_1_button.is_clicked(event):
                    round_button.update_total(1)
                elif chip_5_button.is_clicked(event):
                    round_button.update_total(5)
                elif chip_10_button.is_clicked(event):
                    round_button.update_total(10)
                elif chip_25_button.is_clicked(event):
                    round_button.update_total(25)
                elif chip_50_button.is_clicked(event):
                    round_button.update_total(50)

                # Clear the total if the clear bet button is clicked
                if clear_bet_button.is_clicked(event):
                    round_button.total = 0

                # Confirm the wager when the red button is clicked
                if round_button.rect.collidepoint(event.pos):
                    bet = round_button.total
                    if bet > 0:  # Only proceed if there's a bet placed
                        betting = False  # Exit the betting loop

    # Deduct the bet from the bankroll
    if bet > bankroll:
        display_result("Insufficient Funds!")  # Show insufficient funds
        continue  # Skip to the next round
    else:
        bankroll -= bet

    # Redraw the screen with the new hands
    draw_screen(player_hand, dealer_hand, show_dealer_hidden=True, show_cards=True)

    # Check for blackjack immediately after dealing
    if is_blackjack(player_hand) or is_blackjack(dealer_hand):
        draw_screen(player_hand, dealer_hand, show_dealer_hidden=False)

        if is_blackjack(player_hand) and is_blackjack(dealer_hand):
            display_result("It's a Tie!")  # Both have blackjack
            bankroll += bet  # Return the bet
        elif is_blackjack(player_hand):
            display_result("Blackjack! Player Wins!")
            bankroll += int(bet * 2.5)  # Payout 3:2 for blackjack
        elif is_blackjack(dealer_hand):
            display_result("Dealer Blackjack! Dealer Wins!")
        continue  # Move to the next round

    # Gameplay loop
    playing = True
    while playing:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                playing = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hit_button.is_clicked(event):
                    hit(deck, player_hand)  # Player hits
                    draw_screen(player_hand, dealer_hand, show_dealer_hidden=True, show_cards=True, playing=playing)
                    pygame.display.update()
                    if player_hand.value > 21:
                        time.sleep(0.65)
                        display_result("Player Busts! Dealer Wins!")
                        playing = False  # End the round
                elif stand_button.is_clicked(event):
                    playing = False  # Player stands
                elif double_button.is_clicked(event):
                    # Double the wager or use remaining bankroll
                    additional_bet = min(bet, bankroll)
                    bet += additional_bet
                    bankroll -= additional_bet

                    # Deal one card to the player and end their turn
                    hit(deck, player_hand)
                    draw_screen(player_hand, dealer_hand, show_dealer_hidden=True, show_cards=True, playing=False)
                    pygame.display.update()
                    time.sleep(0.65)  # Small pause for visual clarity

                    # Check if the player busts after doubling
                    if player_hand.value > 21:
                        display_result("Player Busts! Dealer Wins!")
                    playing = False  # End the player's turn

        # Redraw the screen only if necessary
        draw_screen(player_hand, dealer_hand, show_dealer_hidden=True, show_cards=True, playing=playing)

        # Draw buttons only once
        hit_button.draw()
        stand_button.draw()
        double_button.draw()

        # Update only the regions where buttons are drawn to prevent flickering
        pygame.display.update([hit_button.rect, stand_button.rect, double_button.rect])

    # Dealer's turn
    if player_hand.value <= 21:  # Only play the dealer's turn if the player hasn't busted
        while dealer_hand.value < 17:
            hit(deck, dealer_hand)  # Dealer hits until reaching 17
            draw_screen(player_hand, dealer_hand, show_dealer_hidden=False, show_cards=True, playing=False)
            pygame.display.update()  # Force a GUI update after each card is dealt
            pygame.time.delay(500)  # Brief pause for visual clarity

        # Final screen update after dealer's turn
        draw_screen(player_hand, dealer_hand, show_dealer_hidden=False, show_cards=True, playing=False)

        # Determine the winner
        if dealer_hand.value > 21:
            time.sleep(0.35)
            display_result("Dealer Busts! Player Wins!")
            bankroll += bet * 2
        elif dealer_hand.value > player_hand.value:
            display_result("Dealer Wins!")
        elif dealer_hand.value < player_hand.value:
            display_result("Player Wins!")
            bankroll += bet * 2
        else:
            display_result("It's a Tie!")
            bankroll += bet  # Return the bet

# Quit Pygame when done
pygame.quit()

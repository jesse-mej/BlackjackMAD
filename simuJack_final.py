import random
import time
import pygame
import statistics

# Pygame initialization
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack GUI")
clock = pygame.time.Clock()

# Colors
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (50, 50, 150)
BUTTON_HOVER = (100, 100, 200)
CARD_COLOR = (255, 255, 255)
CARD_TEXT_COLOR = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)
card_font = pygame.font.Font(None, 24)

# extra settings to be initialized
bankroll = 100
bet = 0
starting_bankroll = 0
hands_played = 0

# created for cards, taken from original
suits = ("Spades", "Clubs", "Hearts", "Diamonds")
ranks = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
values = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11
}


# CLASS DEFINTIONS (Card and Deck and Hand taken from original, Button classes added with help of
# ChatGPT):


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.deck = []
        for _ in range(self.num_decks):
            for suit in suits:
                for rank in ranks:
                    self.deck.append(Card(suit, rank))

    def __str__(self):
        return "The deck has:" + "".join(f"\n {card}" for card in self.deck)

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
            self.aces += 1  # Add to self.aces
        self.adjust_for_ace()  # Ensure Ace adjustment happens immediately

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def __str__(self):
        return ", ".join(str(card) for card in self.cards)


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
            return True
        return False


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


class ClearBetButton:

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


def hit(deck, hand):
    """Adds a card to the player's hand, adjusts if the card happens to be an Ace"""
    hand.add_card(deck.deal())
    hand.adjust_for_ace()


def is_blackjack(hand):
    """Returns True if the hand is a blackjack (value = 21 with exactly 2 cards)."""
    return hand.value == 21 and len(hand.cards) == 2


def determine_result(player_hand, dealer_hand, bankroll, bet):
    """Determines the result of the game and updates the bankroll."""
    if dealer_hand.value > 21 or player_hand.value > dealer_hand.value:
        result = "Win"
        bankroll += bet * 2  # Winning payout
    elif player_hand.value == dealer_hand.value:
        result = "Push"
        bankroll += bet  # Add the bet back on a push
    else:
        result = "Lose"
    return result, bankroll


def print_hand_results(hands_played, result, player_hand, dealer_hand, bankroll, bet, doubled=False):
    """Prints the full results of a hand in a single-line format."""
    player_cards = ", ".join([str(card) for card in player_hand.cards])
    dealer_cards = ", ".join([str(card) for card in dealer_hand.cards])

    # Add "(Doubled)" to the bet if it was doubled
    bet_info = f"${bet}"
    if doubled:
        bet_info += " (Doubled)"

    print(
        f"Hand {hands_played + 1}: {result} | "
        f"Bet: {bet_info} | Updated Bankroll: ${bankroll} | "
        f"Player's Hand: [{player_cards}] (Score: {player_hand.value}) | "
        f"Dealer's Hand: [{dealer_cards}] (Score: {dealer_hand.value})"
    )


def play_dealer_turn(deck, dealer_hand):
    """Plays the dealer's turn according to dealer rules."""
    while dealer_hand.value < 17:
        dealer_hand.add_card(deck.deal())


def get_display_value(hand):
    """Returns the hand's value for PyGame."""
    # Start with the current total value
    total = hand.value

    # Adjust for aces
    soft_total = total
    for _ in range(hand.aces):
        if soft_total > 21:
            soft_total -= 10  # Convert one ace from 11 to 1 if the total exceeds 21

    # Display both soft and hard totals if the hand contains aces
    if hand.aces > 0 and soft_total != total:
        return f"{soft_total}/{total}"  # Soft and hard totals
    return str(total)  # Single total if no aces or no adjustment needed


def result_message(result):
    """Returns the appropriate message based on the result for PyGame."""
    if result == "Win":
        return "Player Wins!"
    elif result == "Lose":
        return "Dealer Wins!"
    elif result == "Push":
        return "It's a Tie!"
    elif result == "Bust":
        return "Player Busts!"
    return ""


def show_message(message):
    """Displays the result message on the screen."""
    display_result(message)  # Shows the message on screen
    pygame.time.delay(2000)  # Delay for visibility


def simulate_player_turn(deck, player_hand, dealer_upcard, bankroll, bet):
    """Simulates the player's turn using basic strategy."""
    doubled = False  # Tracks if the player doubled
    while player_hand.value <= 21:
        action = basic_strategy(player_hand, dealer_upcard)
        if action == "Hit":
            player_hand.add_card(deck.deal())
        elif action == "Double" and len(player_hand.cards) == 2 and bankroll >= bet:
            bankroll -= bet
            bet *= 2
            player_hand.add_card(deck.deal())
            doubled = True  # Mark that the player doubled
            break  # Doubling ends the player's turn
        else:  # Stand
            break

    return bankroll, bet, doubled


def draw_screen(player_hand=None, dealer_hand=None, show_dealer_hidden=True, show_cards=True, playing=True):
    """Draws the entire screen, including the bankroll, cards, and scores."""
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
    """Asks the player to choose their wager."""
    wager_font = pygame.font.Font(None, 36)
    message_text = "How much would you like to wager on this hand?"
    message_surf = wager_font.render(message_text, True, WHITE)
    message_rect = message_surf.get_rect(center=(WIDTH / 2, HEIGHT // 2 - 40))  # Position above the buttons
    screen.blit(message_surf, message_rect)


def draw_click_to_wager_message():
    """Prompts player to click wager"""
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


# Create the betting buttons
chip_1_button = Button("$1", (WIDTH // 2 - 250, HEIGHT // 2))  # Leftmost button
chip_5_button = Button("$5", (WIDTH // 2 - 150, HEIGHT // 2))
chip_10_button = Button("$10", (WIDTH // 2 - 50, HEIGHT // 2))
chip_25_button = Button("$25", (WIDTH // 2 + 50, HEIGHT // 2))
chip_50_button = Button("$50", (WIDTH // 2 + 150, HEIGHT // 2))
# Create the hit, stand, and double buttons
hit_button = Button("Hit", (WIDTH - 150, HEIGHT - 150))  # Bottom-right corner, higher
stand_button = Button("Stand", (WIDTH - 150, HEIGHT - 80))  # Bottom-right corner, lower
double_button = Button("Double", (WIDTH - 150, HEIGHT - 220))  # Positioned directly above Hit/Stand buttons
# Create the End Session button
end_session_button = Button("End Session", (WIDTH - 150, HEIGHT - 100))  # Bottom-right of the betting screen

# Define the main menu buttons, hardcoded in width and x position
play_blackjack_button = Button("Play Blackjack", (WIDTH // 2 - 150, HEIGHT // 2 - 50))  # Centered on the screen
run_simulation_button = Button("Run Simulations", (WIDTH // 2 - 150, HEIGHT // 2 + 50))  # Below the first button
play_blackjack_button.rect.width = 250  # Wider for "Play Blackjack"
run_simulation_button.rect.width = 250  # Wider for "Run Simulations"
play_blackjack_button.rect.x = (WIDTH - play_blackjack_button.rect.width) // 2
run_simulation_button.rect.x = (WIDTH - run_simulation_button.rect.width) // 2


def basic_strategy(player_hand, dealer_upcard):
    """Uses basic blackjack strategy to determine if the player should hit, stand, or double their bet."""
    dealer_upcard_value = values[dealer_upcard.rank]
    total = player_hand.value

    # Soft hand (contains Ace counted as 11)
    if player_hand.aces > 0 and total <= 21:
        # Soft total adjustments for strategy
        if total >= 19:
            return "Stand"
        elif total == 18:
            return "Double" if 2 <= dealer_upcard_value <= 6 else "Stand" if dealer_upcard_value in [7, 8] else "Hit"
        elif total == 17:
            return "Double" if 3 <= dealer_upcard_value <= 6 else "Hit"
        elif total in [16, 15]:
            return "Double" if 4 <= dealer_upcard_value <= 6 else "Hit"
        elif total in [14, 13]:
            return "Double" if 5 <= dealer_upcard_value <= 6 else "Hit"

    # Hard hand (no Ace counted as 11 or Ace adjusted to 1)
    if total >= 17:
        return "Stand"
    elif 13 <= total <= 16:
        return "Stand" if 2 <= dealer_upcard_value <= 6 else "Hit"
    elif total == 12:
        return "Stand" if 4 <= dealer_upcard_value <= 6 else "Hit"
    elif total == 11:
        return "Double"
    elif total == 10:
        return "Double" if 2 <= dealer_upcard_value <= 9 else "Hit"
    elif total == 9:
        return "Double" if 3 <= dealer_upcard_value <= 6 else "Hit"
    else:
        return "Hit"


def draw_simulation_menu():
    """Draws the simulation menu screen."""
    screen.fill(GREEN)  # Background color
    question_font = pygame.font.Font(None, 40)
    button_font = pygame.font.Font(None, 30)
    question_text = "What simulation do you want to run?"
    question_surf = question_font.render(question_text, True, WHITE)
    question_rect = question_surf.get_rect(center=(WIDTH // 2, HEIGHT // 6))  # Position above buttons
    screen.blit(question_surf, question_rect)

    # Updated button texts and order
    simulation_texts = [
        "Reverse Martingale",
        "Martingale",
        "Half Up",
        "Oscar's System",
        "Simple Basic Strategy"
    ]

    # Dynamic button positions
    button_height = 50
    button_margin = 20  # Space between buttons vertically
    row_start_y = HEIGHT // 3 + 50  # Shift all buttons down by 50 pixels
    col_positions = [WIDTH // 4, 3 * WIDTH // 4]  # x-positions for columns (1/4 and 3/4 of the screen)

    buttons = []
    for i, text in enumerate(simulation_texts):
        # Calculate button dimensions based on text width
        text_surface = button_font.render(text, True, WHITE)
        button_width = max(text_surface.get_width() + 40, 200)  # Add padding around text

        if i < 4:  # Top two rows
            col = i % 2  # 0 for left, 1 for right
            row = i // 2  # Integer division for row index
            x = col_positions[col]
            y = row_start_y + row * (button_height + button_margin)
        else:  # Bottom row for "Simple Basic Strategy"
            x = WIDTH // 2
            y = row_start_y + 2 * (button_height + button_margin)  # Place below the first two rows

        # Create and draw the button
        button = Button(text, (x - button_width // 2, y))
        button.rect.width = button_width
        button.rect.height = button_height
        button.draw()
        buttons.append(button)

    pygame.display.update()  # Update the display with the new layout

    return buttons


def display_simulation_results(results):
    """Displays the results of the simulation on a new screen by taking in the results parameter."""
    running_results_screen = True

    while running_results_screen:
        screen.fill(GREEN)  # Background color
        result_font = pygame.font.Font(None, 60)

        # Results data
        median_hands_text = f"Median Hands to Bankruptcy: {results['median_hands_to_bankruptcy']:.2f}"
        median_bankroll_text = f"Median Max Bankroll: ${results['median_max_bankroll']:.2f}"

        # Display results
        median_hands_surf = result_font.render(median_hands_text, True, WHITE)
        median_bankroll_surf = result_font.render(median_bankroll_text, True, WHITE)

        median_hands_rect = median_hands_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        median_bankroll_rect = median_bankroll_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

        screen.blit(median_hands_surf, median_hands_rect)
        screen.blit(median_bankroll_surf, median_bankroll_rect)

        pygame.display.update()

        # Wait for user to close or reset
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running_results_screen = False
                pygame.quit()
                quit()


def handle_simulation_menu():
    """Runs the chosen simulation based on the button clicked using run_multiple_simulations."""
    simulation_buttons = draw_simulation_menu()

    running_simulation_menu = True
    while running_simulation_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in simulation_buttons:
                    if button.is_clicked(event):
                        # Get bankroll, unit size, and number of simulations
                        bankroll, unit_size, num_simulations = simulation_setup(button.text)

                        if button.text == "Simple Basic Strategy":
                            results = run_multiple_simulations(bankroll, unit_size, num_simulations,
                                                               run_basic_strategy_simulation)
                            display_simulation_results(results)
                            running_simulation_menu = False
                        elif button.text == "Martingale":
                            results = run_multiple_simulations(bankroll, unit_size, num_simulations,
                                                               martingale_strategy)
                            display_simulation_results(results)
                            running_simulation_menu = False
                        elif button.text == "Reverse Martingale":
                            results = run_multiple_simulations(bankroll, unit_size, num_simulations,
                                                               reverse_martingale_strategy)
                            display_simulation_results(results)
                            running_simulation_menu = False
                        elif button.text == "Half Up":
                            results = run_multiple_simulations(bankroll, unit_size, num_simulations, half_up_strategy)
                            display_simulation_results(results)
                            running_simulation_menu = False
                        elif button.text == "Oscar's System":
                            results = run_multiple_simulations(bankroll, unit_size, num_simulations,
                                                               oscars_system_strategy)
                            display_simulation_results(results)
                            running_simulation_menu = False


def run_multiple_simulations(bankroll, unit_size, num_simulations, strategy_func):
    """Runs a simulation multiple times and calculates median hands to bankruptcy and max bankroll."""
    hands_list = []
    max_bankroll_list = []

    for sim in range(1, num_simulations + 1):
        # Check if `strategy_func` is a full simulation function
        if strategy_func == run_basic_strategy_simulation:
            # Run directly if it's a simulation function
            results = strategy_func(bankroll, unit_size, print_hands=(num_simulations == 1))
        else:
            # Otherwise, treat it as a strategy function
            results = run_simulation_with_strategy(bankroll, unit_size, strategy_func,
                                                   print_hands=(num_simulations == 1))

        hands_list.append(results["hands_played"])
        max_bankroll_list.append(results["max_bankroll"])

        # Print per-simulation results for multiple simulations
        if num_simulations > 1:
            print(
                f"Simulation {sim}: Hands to Bankruptcy = {results['hands_played']}, "
                f"Max Bankroll = ${results['max_bankroll']:.2f}"
            )

    # Calculate medians
    median_hands = statistics.median(hands_list)
    median_max_bankroll = statistics.median(max_bankroll_list)

    return {
        "median_hands_to_bankruptcy": median_hands,
        "median_max_bankroll": median_max_bankroll,
    }


def run_simulation_with_strategy(bankroll, unit_size, strategy_func, print_hands=True):
    """Runs simulation with betting strategy until the bankroll is empty."""

    hands_played = 0
    max_bankroll = bankroll
    win_streak = 0
    lose_streak = 0
    total_wins = 0
    last_result = None

    while bankroll > 0:  # Run until bankroll is depleted
        # Initialize deck and hands for a new round
        deck = Deck(num_decks=6)
        deck.shuffle()
        player_hand = Hand()
        dealer_hand = Hand()
        player_hand.add_card(deck.deal())
        player_hand.add_card(deck.deal())
        dealer_hand.add_card(deck.deal())
        dealer_hand.add_card(deck.deal())

        # Get the bet amount using the strategy function
        bet = strategy_func(bankroll, unit_size, win_streak, lose_streak, last_result, total_wins)
        if bankroll < bet:
            bet = bankroll  # Bet the remaining bankroll if less than the calculated bet
        bankroll -= bet
        doubled = False  # Track whether the bet was doubled

        # Check for blackjack immediately after dealing
        if is_blackjack(player_hand) or is_blackjack(dealer_hand):
            if is_blackjack(player_hand) and is_blackjack(dealer_hand):
                result = "Push"
                bankroll += bet  # Return the bet for a push
            elif is_blackjack(player_hand):
                result = "Blackjack"
                win_streak += 1
                lose_streak = 0
                total_wins += 1
                bankroll += bet * 2.5  # Correct 3:2 payout for Blackjack
            elif is_blackjack(dealer_hand):
                result = "Lose"  # Dealer wins
                lose_streak += 1
                win_streak = 0
            if print_hands:
                print_hand_results(hands_played, result, player_hand, dealer_hand, bankroll, bet)
            hands_played += 1
            continue  # Skip to the next round

        # Play player's turn
        bankroll, bet, doubled = simulate_player_turn(deck, player_hand, dealer_hand.cards[0], bankroll, bet)

        # Check if player busts
        if player_hand.value > 21:
            result = "Lose"
            lose_streak += 1
            win_streak = 0
        else:
            # Dealer's turn
            play_dealer_turn(deck, dealer_hand)

            # Determine the result
            if dealer_hand.value > 21 or player_hand.value > dealer_hand.value:
                result = "Win"
                bankroll += bet * 2  # Winning payout includes doubled bets
                win_streak += 1
                total_wins += 1
                lose_streak = 0
            elif player_hand.value == dealer_hand.value:
                result = "Push"
                bankroll += bet  # Return the bet amount on a push
            else:
                result = "Lose"
                lose_streak += 1
                win_streak = 0

        max_bankroll = max(max_bankroll, bankroll)

        # Print per-hand results only if print_hands is True
        if print_hands:
            print_hand_results(hands_played, result, player_hand, dealer_hand, bankroll, bet, doubled)

        hands_played += 1
        last_result = result

    return {
        "hands_played": hands_played,
        "max_bankroll": max_bankroll,
    }


def run_basic_strategy_simulation(bankroll, unit_size, print_hands=True):
    """Runs basic strategy simulation witt a never-changing bet size"""
    hands_played = 0
    max_bankroll = bankroll

    while bankroll > 0:  # Continue until the bankroll is depleted
        # Initialize and reshuffle the deck for each hand
        deck = Deck(num_decks=6)
        deck.shuffle()

        # Deal initial hands
        player_hand = Hand()
        dealer_hand = Hand()
        player_hand.add_card(deck.deal())
        player_hand.add_card(deck.deal())
        dealer_hand.add_card(deck.deal())
        dealer_hand.add_card(deck.deal())

        # Place the bet
        bet = unit_size
        if bankroll < unit_size:
            bet = bankroll  # Bet the remaining bankroll if it's less than the unit size
        bankroll -= bet

        # Check for blackjack immediately after dealing
        if is_blackjack(player_hand) or is_blackjack(dealer_hand):
            if is_blackjack(player_hand) and is_blackjack(dealer_hand):
                result = "Push"
                bankroll += bet  # Return the bet for a push
            elif is_blackjack(player_hand):
                result = "Blackjack"
                bankroll += bet * 2.5  # Correct 3:2 payout for Blackjack
            elif is_blackjack(dealer_hand):
                result = "Lose"  # Dealer wins
            if print_hands:
                print_hand_results(hands_played, result, player_hand, dealer_hand, bankroll, bet)
            hands_played += 1
            continue  # Skip to the next round

        # Play player's turn
        while player_hand.value <= 21:
            action = basic_strategy(player_hand, dealer_hand.cards[0])
            if action == "Hit":
                player_hand.add_card(deck.deal())
            elif action == "Double" and len(player_hand.cards) == 2 and bankroll >= bet:
                bankroll -= bet
                bet *= 2
                player_hand.add_card(deck.deal())
                break  # Doubling ends the player's turn
            else:  # Stand
                break

        # Check if player busts
        if player_hand.value > 21:
            result = "Lose"
        else:
            # Dealer's turn
            while dealer_hand.value < 17:
                dealer_hand.add_card(deck.deal())

            # Determine the result
            if dealer_hand.value > 21 or player_hand.value > dealer_hand.value:
                result = "Win"
                bankroll += bet * 2  # Player wins
            elif player_hand.value == dealer_hand.value:
                result = "Push"
                bankroll += bet  # Push
            else:
                result = "Lose"

        max_bankroll = max(max_bankroll, bankroll)

        # Print results only if print_hands is True
        if print_hands:
            print_hand_results(hands_played, result, player_hand, dealer_hand, bankroll, bet)

        hands_played += 1

    return {
        "hands_played": hands_played,
        "max_bankroll": max_bankroll,
    }


def reverse_martingale_strategy(bankroll, unit_size, win_streak, lose_streak, last_result, total_wins, streak_cap=4):
    """Determines the next bet using the Reverse Martingale strategy"""
    """Defined from great.com article: For every win along a streak, you double your stake. You get to choose how long your 
    predetermined streak will be (in this case 4) and how much your initial bet will cost."""

    # Start with the initial unit size
    current_bet = unit_size

    if last_result == "Lose" or win_streak == 0 or win_streak >= streak_cap:
        # Reset to the initial unit size on a loss, streak cap, or no streak
        current_bet = unit_size
    elif last_result == "Push":
        # Maintain the same bet on a push
        pass  # The current bet remains unchanged
    else:
        # Progressively increase the bet on a win, doubling based on streak
        current_bet = unit_size * (2 ** win_streak)

    # Ensure the bet does not exceed the bankroll
    current_bet = min(current_bet, bankroll)

    return current_bet


def martingale_strategy(bankroll, unit_size, win_streak, lose_streak, last_result, total_wins):
    """Determines the next bet using the Martingale strategy"""
    """Defined from great.com article: ou start at your minimum wager (let’s say you’re starting at $10, the common minimum 
    bet in blackjack). After every loss, you double your wager. So, if you’d started betting with $10, then you’d bet 
    $20, then $40, then $80, and so on if you kept losing. If you do win a hand, you restart the entire process and 
    bet that $10 minimum on the next hand."""

    # Start with the initial unit size
    current_bet = unit_size
    if lose_streak > 0:
        # Double the bet for each loss in the streak
        current_bet = unit_size * (2 ** lose_streak)
    elif last_result == "Push":
        # Maintain the same bet on a push
        pass  # The current_bet remains unchanged
    # Cap the bet to the available bankroll
    current_bet = min(current_bet, bankroll)
    return current_bet


def half_up_strategy(bankroll, unit_size, win_streak, lose_streak, last_result, total_wins):
    """Determines the next bet using the Half Up strategy"""
    """Defined from great.com article: You start with a flat bet, and you bet the same amount until you win two consecutive 
    hands. Then you’ll increase your bet by 50% of your initial stake."""
    if last_result == "Lose" or win_streak < 2:
        # Start over at the initial unit size if a loss occurs or win streak < 2
        return min(unit_size, bankroll)
    else:
        # Increase the bet by 50% of the initial unit size after two consecutive wins
        next_bet = unit_size + int(unit_size * 0.5 * (win_streak - 1))  # Incremental bet increase
        # caps the bet to available bankroll
        return min(next_bet, bankroll)


def oscars_system_strategy(bankroll, unit_size, win_streak, lose_streak, last_result, total_wins):
    """Determines the next bet using the Oscar's System strategy"""
    """Defined from great.com article: You simply continue to add another unit to every wager if you win or stick to the same 
    amount if you lose (you do not revert back to your original bet)."""
    first_bet = unit_size

    # Ensure the bet does not exceed the bankroll, the bet will equal the original unit + an extra unit for every winning bet
    return min(first_bet + (total_wins * first_bet), bankroll)


def simulation_setup(simulation_name):
    """Displays a setup screen to ask the user how they want to run their simulation."""
    input_active = [False, False, False]  # Track active input boxes for each question
    user_inputs = ["", "", ""]  # Store inputs for bankroll, unit size, and number of simulations
    questions = [
        "Enter your starting bankroll:",
        "Enter your unit size:",
        "How many simulations to run:"
    ]
    input_boxes = [
        pygame.Rect(WIDTH // 2 - 200, HEIGHT // 3 + (i * 100), 400, 50) for i in range(3)
    ]
    confirm_button = Button(
        "Confirm",
        (WIDTH // 2 - 50, HEIGHT // 2 + 150)  # Adjust position to account for the extra input
    )

    setup_running = True
    while setup_running:
        screen.fill(GREEN)  # Clear the screen

        # Draw simulation name at the top
        title_font = pygame.font.Font(None, 60)
        title_surf = title_font.render(simulation_name, True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 6))  # Position at the top
        screen.blit(title_surf, title_rect)

        # Display questions and input boxes
        font = pygame.font.Font(None, 40)
        for i, question in enumerate(questions):
            question_surf = font.render(question, True, WHITE)
            question_rect = question_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 20 + (i * 100)))
            screen.blit(question_surf, question_rect)

            # Draw input boxes
            pygame.draw.rect(screen, WHITE, input_boxes[i], 2)
            input_text = font.render(user_inputs[i], True, WHITE)
            screen.blit(input_text, (input_boxes[i].x + 10, input_boxes[i].y + 10))

        # Draw the confirm button
        confirm_button.draw()

        pygame.display.update()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if confirm button is clicked
                if confirm_button.is_clicked(event):
                    if all(user_inputs):  # Ensure all fields are filled
                        try:
                            # Convert bankroll, unit size, and number of simulations to float or int
                            bankroll = float(user_inputs[0])
                            unit_size = float(user_inputs[1])
                            num_simulations = int(user_inputs[2])
                            return bankroll, unit_size, num_simulations
                        except ValueError:
                            print("Invalid input. Please enter valid numbers.")
                # Check if input boxes are clicked
                for i, box in enumerate(input_boxes):
                    if box.collidepoint(event.pos):
                        input_active = [False] * 3  # Deactivate other input boxes
                        input_active[i] = True
            elif event.type == pygame.KEYDOWN:
                for i in range(3):
                    if input_active[i]:
                        if event.key == pygame.K_RETURN:
                            input_active[i] = False  # Deactivate input on Enter
                        elif event.key == pygame.K_BACKSPACE:
                            user_inputs[i] = user_inputs[i][:-1]  # Remove last character
                        else:
                            user_inputs[i] += event.unicode  # Add typed character


def draw_main_menu():
    """Draws the main menu screen in PyGame."""
    screen.fill(GREEN)  # Background color
    title_font = pygame.font.Font(None, 60)
    title_text = "Welcome to SimuJack! Pick one!"
    title_surf = title_font.render(title_text, True, WHITE)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))  # Position title above buttons
    screen.blit(title_surf, title_rect)

    # Draw buttons for different options
    play_blackjack_button.draw()
    run_simulation_button.draw()
    pygame.display.update()


def get_starting_bankroll():
    """Gameplay screen where user inputs their starting bankroll."""
    input_active = True  # Track whether the input box is active
    user_text = ""  # Store the user's input

    # Input box dimensions
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)

    while input_active:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to confirm
                    if user_text.isdigit() and int(user_text) > 0:  # Ensure valid input
                        return int(user_text)
                    else:
                        user_text = ""  # Clear invalid input
                elif event.key == pygame.K_BACKSPACE:  # Remove the last character
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode  # Append typed character to input

        # Draw the input screen
        screen.fill(GREEN)
        title_font = pygame.font.Font(None, 60)
        input_font = pygame.font.Font(None, 40)

        # Display instructions
        title_text = "Enter your starting bankroll:"
        title_surf = title_font.render(title_text, True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(title_surf, title_rect)

        # Draw the input box
        pygame.draw.rect(screen, WHITE, input_box, 2)  # Box outline
        text_surface = input_font.render(user_text, True, WHITE)  # Render input text
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))  # Display text
        input_box.w = max(200, text_surface.get_width() + 20)  # Adjust box width dynamically

        # Update the screen
        pygame.display.update()


# Add the main menu loop, for when the file in first run
in_main_menu = True
while in_main_menu:
    draw_main_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_blackjack_button.is_clicked(event):
                bankroll = get_starting_bankroll()  # Get the player's starting bankroll
                starting_bankroll = bankroll  # Store the starting bankroll
                in_main_menu = False  # Exit the main menu loop and start the game
                running = True
                break
            elif run_simulation_button.is_clicked(event):
                handle_simulation_menu()  # Call the simulation menu handler

# Create the round button for betting
round_button = RoundButton((WIDTH // 2, HEIGHT - 80))  # Positioned closer to the bottom

clear_bet_button = ClearBetButton(
    (WIDTH // 2 + 50, HEIGHT - 70))  # Positioned slightly offset bottom-right of the main red button

# Modify the Event Loop to Include Clear Bet Functionality
wager_total = 0  # Track the wager total


# FUNCTION DEFINITIONS:

def display_result(message):
    """Displays the result of the hand on the screen."""
    # Set font size dynamically based on message length
    if len(message) > 20:  # Example threshold for long messages
        result_font = pygame.font.Font(None, 60)  # Smaller font for longer text
    else:
        result_font = pygame.font.Font(None, 80)  # Default larger font

    result_surf = result_font.render(message, True, WHITE)
    result_rect = result_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    pygame.draw.rect(screen, BLACK, result_rect.inflate(20, 20))  # Background box for visibility
    screen.blit(result_surf, result_rect)
    pygame.display.update()
    pygame.time.delay(2000)  # Keep the result on screen for 2 seconds


# updates pygame scores
def draw_scores(player_hand, dealer_hand, playing, is_blackjack=False):
    """Shows the player and dealer scores on the PyGame, updated live."""
    score_font = pygame.font.Font(None, 50)

    # Dealer score: Show the full score when blackjack occurs
    if is_blackjack or not playing:  # Game is over or blackjack occurred
        dealer_score_text = f"Dealer: 21" if is_blackjack else f"Dealer: {get_display_value(dealer_hand)}"
    else:  # Ongoing game, show only the upcard’s value
        dealer_score_text = f"Dealer: {values[dealer_hand.cards[1].rank]}"

    dealer_score_surf = score_font.render(dealer_score_text, True, BLACK)
    dealer_score_rect = dealer_score_surf.get_rect(center=(WIDTH / 2, 30))
    screen.blit(dealer_score_surf, dealer_score_rect)

    # Player score: Always show the full value
    player_score_text = f"Player: {get_display_value(player_hand)}"
    player_score_surf = score_font.render(player_score_text, True, BLACK)
    player_score_rect = player_score_surf.get_rect(center=(WIDTH / 2, 550))
    screen.blit(player_score_surf, player_score_rect)


# creates pygame cards
def draw_cards(hand, x_start, y_position, centered=False, hide_first=False, reveal_all=False):
    """Draws the cards in PyGame during the gameplay version of the code"""
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


def show_end_screen():
    """Displays the end screen with session statistics."""
    running_end_screen = True

    # Calculate stats
    net_gain = bankroll - starting_bankroll
    gain_text = f"Net Gain: +${net_gain}" if net_gain >= 0 else f"Net Loss: -${abs(net_gain)}"
    stats_text = f"You played {hands_played} hands."
    final_bankroll_text = f"You finished with ${bankroll} in your bankroll."

    while running_end_screen:
        screen.fill((0, 0, 255))  # Fill the screen with blue
        end_font = pygame.font.Font(None, 60)
        stats_font = pygame.font.Font(None, 40)

        # Display "Session Ended" message
        end_text = "Session Ended. Thank you for playing!"
        end_surf = end_font.render(end_text, True, WHITE)
        end_rect = end_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        screen.blit(end_surf, end_rect)

        # Display final bankroll
        bankroll_surf = stats_font.render(final_bankroll_text, True, WHITE)
        bankroll_rect = bankroll_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(bankroll_surf, bankroll_rect)

        # Display number of hands played
        stats_surf = stats_font.render(stats_text, True, WHITE)
        stats_rect = stats_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(stats_surf, stats_rect)

        # Display net gain/loss
        gain_surf = stats_font.render(gain_text, True, WHITE)
        gain_rect = gain_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(gain_surf, gain_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running_end_screen = False
                pygame.quit()
                quit()


# main gameplay loop:

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
while running:
    # Initialize deck and hands for a new round
    deck = Deck(num_decks=6)
    deck.shuffle()
    player_hand = Hand()
    dealer_hand = Hand()
    player_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())

    # Handle betting phase
    betting = True
    while betting:
        screen.fill(GREEN)
        draw_wager_message()
        draw_bankroll()

        chip_1_button.draw()
        chip_5_button.draw()
        chip_10_button.draw()
        chip_25_button.draw()
        chip_50_button.draw()
        round_button.draw()
        clear_bet_button.draw()
        end_session_button.draw()
        draw_click_to_wager_message()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                betting = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
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
                if clear_bet_button.is_clicked(event):
                    round_button.total = 0
                if round_button.rect.collidepoint(event.pos) and round_button.total > 0:
                    bet = round_button.total
                    betting = False
                if end_session_button.is_clicked(event):
                    show_end_screen()
                    pygame.quit()
                    quit()

    # Deduct bet and update bankroll
    if bet > bankroll:
        display_result("Insufficient Funds!")
        continue
    bankroll -= bet

    # Check for blackjack immediately after dealing
    draw_screen(player_hand, dealer_hand, show_dealer_hidden=True, show_cards=True)
    if is_blackjack(player_hand) or is_blackjack(dealer_hand):
        draw_screen(player_hand, dealer_hand, show_dealer_hidden=False, show_cards=True)
        if is_blackjack(player_hand) and is_blackjack(dealer_hand):
            result = "Push"
            bankroll += bet
        elif is_blackjack(player_hand):
            result = "Blackjack"
            bankroll += int(bet * 2.5)  # 3:2 payout
        elif is_blackjack(dealer_hand):
            result = "Lose"
        # Print the result
        print_hand_results(hands_played, result, player_hand, dealer_hand, bankroll, bet)
        hands_played += 1
        continue  # Skip to the next round

    # Player's turn
    playing = True
    player_busted = False
    while playing:
        draw_screen(player_hand, dealer_hand, show_dealer_hidden=True, show_cards=True)
        hit_button.draw()
        stand_button.draw()
        double_button.draw()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                playing = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hit_button.is_clicked(event):
                    hit(deck, player_hand)
                    draw_screen(player_hand, dealer_hand, show_dealer_hidden=True, show_cards=True)
                    if player_hand.value > 21:
                        player_busted = True
                        time.sleep(0.65)
                        show_message("Player Busts! Dealer Wins!")
                        playing = False  # End the round
                elif stand_button.is_clicked(event):
                    playing = False  # Player chooses to stand
                elif double_button.is_clicked(event):
                    if bankroll >= bet:
                        bankroll -= bet
                        bet *= 2
                        hit(deck, player_hand)
                        draw_screen(player_hand, dealer_hand, show_dealer_hidden=True, show_cards=True)
                        if player_hand.value > 21:
                            player_busted = True
                            show_message("Player Busts! Dealer Wins!")
                        playing = False  # Double ends the player's turn

    # Dealer's turn (only if player hasn't busted)
    if not player_busted:
        while dealer_hand.value < 17:
            hit(deck, dealer_hand)
            draw_screen(player_hand, dealer_hand, show_dealer_hidden=False, show_cards=True, playing=False)
            pygame.display.update()
            pygame.time.delay(500)

        # Final update for dealer's hand
        draw_screen(player_hand, dealer_hand, show_dealer_hidden=False, show_cards=True, playing=False)

        # Determine the result and display the appropriate message
        result, bankroll = determine_result(player_hand, dealer_hand, bankroll, bet)
        show_message(result_message(result))
    else:
        result = "Bust"  # Lock the result as "Bust" for the print statement

    print_hand_results(hands_played, result, player_hand, dealer_hand, bankroll, bet)

    # Increment hands played and check for bankruptcy
    hands_played += 1
    if bankroll <= 0:
        show_end_screen()
        pygame.quit()
        quit()

pygame.quit()

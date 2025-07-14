import keyboard
import time
import random

# --- Configuration ---
# The key to press to toggle the script on and off
ACTIVATION_KEY = '`' 

# The list of keys the script will press randomly
KEYS_TO_PRESS = ['w', 'a', 's', 'd']

# The delay between key presses, in seconds.
# The script will wait a random amount of time between MIN_DELAY and MAX_DELAY.
MIN_DELAY = 10
MAX_DELAY = 25
# ---------------------


# This variable will track whether the script is active or not
is_active = False

def toggle_script():
    """Toggles the active state of the script."""
    global is_active
    is_active = not is_active
    if is_active:
        print("Anti-AFK script ACTIVED. Press '`' again to pause.")
    else:
        print("Anti-AFK script PAUSED. Press '`' again to resume.")

# Set up a hotkey to call the toggle_script function when the activation key is pressed
keyboard.add_hotkey(ACTIVATION_KEY, toggle_script)

print(f"Simple Anti-AFK Script started.")
print(f"Press '{ACTIVATION_KEY}' to toggle the script on or off.")
print("Press Ctrl+C in this window to exit the script completely.")

# Main loop
while True:
    try:
        # If the script is not active, just wait a moment and check again
        if not is_active:
            time.sleep(0.1)
            continue

        # If the script IS active, choose a random key from our list
        key_to_press = random.choice(KEYS_TO_PRESS)
        
        print(f"Status: ACTIVE. Pressing '{key_to_press}'...")
        
        # Press and release the chosen key
        keyboard.press_and_release(key_to_press)
        
        # Wait for a random duration before the next key press
        sleep_duration = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"Sleeping for {sleep_duration:.2f} seconds...")
        time.sleep(sleep_duration)

    except KeyboardInterrupt:
        # This allows you to stop the script gracefully by pressing Ctrl+C
        print("\nScript terminated by user.")
        break
    except Exception as e:
        # Catch any other potential errors
        print(f"\nAn error occurred: {e}")
        break
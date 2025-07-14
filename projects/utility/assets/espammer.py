import keyboard
import time
import threading
import os

# --- Global variables to control state ---
spamming_active = False
program_running = True  # Controls the main loop and spamming thread loop

# Lock for thread-safe access to spamming_active if it were more complex
# toggle_lock = threading.Lock() # Not strictly necessary here

def toggle_spamming_state():
    """
    Called when F5 is pressed. Toggles the spamming state.
    """
    global spamming_active
    spamming_active = not spamming_active
    if spamming_active:
        print("Spamming 'e' ENABLED. (Press F5 to disable)")
    else:
        print("Spamming 'e' DISABLED. (Press F5 to enable)")

def spam_loop():
    """
    This function runs in a separate thread and performs the "e" key spamming.
    """
    global program_running
    global spamming_active
    
    print("Spamming thread started.")
    while program_running:
        current_spam_state = spamming_active

        if current_spam_state:
            keyboard.write('e')
            time.sleep(0.1)
        else:
            time.sleep(0.01) 
    print("Spamming thread stopping.")

def quit_application_on_ctrl(event):
    """
    Called when any key is pressed. If it's a 'ctrl' key, it quits.
    The 'event' argument is a KeyboardEvent object.
    """
    global program_running
    if event.name == 'ctrl' or event.name == 'left ctrl' or event.name == 'right ctrl':
        if program_running: 
            print(f"'{event.name}' pressed. Forcing program quit...")
            program_running = False
            
            # Unhooking might be good practice, but os._exit makes it mostly moot.
            # try:
            #     keyboard.unhook_all()
            # except Exception:
            #     pass # Ignore errors during forceful shutdown
            
            os._exit(0) # Forcefully terminate the entire process.

# --- Main part of the script ---
if __name__ == "__main__":
    print("Spam Toggler Initialized.")
    print("- Press F5 to toggle 'e' spamming (0.1s interval).")
    print("- Press ANY Ctrl key (Left or Right) to quit the program.")
    print("\nNOTE: On Linux, you might need to run with 'sudo'.")
    print("NOTE: On macOS, grant accessibility permissions if needed.\n")

    keyboard.add_hotkey('f5', toggle_spamming_state, suppress=False)

    # Corrected line: Use on_press for a global key listener
    keyboard.on_press(quit_application_on_ctrl, suppress=False)
    
    spam_worker_thread = threading.Thread(target=spam_loop, daemon=True)
    spam_worker_thread.start()

    try:
        while program_running:
            time.sleep(0.1) 
    except KeyboardInterrupt:
        print("\nCtrl+C detected in console. Exiting program...")
        program_running = False
    finally:
        if program_running:
            program_running = False
        
        if spam_worker_thread.is_alive():
            print("Waiting for spamming thread to finish...")
            spam_worker_thread.join(timeout=0.5)
        
        # Unhooking here might not always run if os._exit was called
        # keyboard.unhook_all() 
        print("Program terminated.")
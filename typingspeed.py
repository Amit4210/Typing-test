import curses
from curses import wrapper
import time
import random


def start_screen(stdscr):
    stdscr.clear()
    stdscr.addstr("Welcome to the Typing Test!")
    stdscr.addstr("\nPress any key to begin!")
    stdscr.refresh()
    stdscr.getkey()


def display_text(stdscr, target, current, wpm=0):
    stdscr.addstr(0, 0, target)
    stdscr.addstr(1, 0, f"WPM: {wpm}")

    for i, char in enumerate(current):
        if i < len(target):
            correct_char = target[i]
            color = curses.color_pair(1) if char == correct_char else curses.color_pair(2)
            stdscr.addstr(0, i, char, color)


def load_text():
    try:
        with open("text.txt", "r", encoding='utf-8') as f:
            lines = f.readlines()
            # Filter out the empty lines
            lines = [line.strip() for line in lines if line.strip()]
            if not lines:
                return "The quick brown fox jumps over the lazy dog."
            text = random.choice(lines)
            # Clean the text: remove extra whitespace, normalize spaces
            text = ' '.join(text.split())
            return text
    except FileNotFoundError:
        return "The quick brown fox jumps over the lazy dog."  # replacement text


def wpm_test(stdscr):
    target_text = load_text()
    current_text = []
    wpm = 0
    start_time = time.time()
    stdscr.nodelay(True)
    curses.curs_set(0)  # hide the cursor

    while True:
        time_elapsed = max(time.time() - start_time, 1)
        wpm = round((len(current_text) / (time_elapsed / 60)) / 5)

        for line_num in range(7): # only clears the lines we're about to update, avoids flicker
            stdscr.move(line_num, 0)
            stdscr.clrtoeol()

        display_text(stdscr, target_text, current_text, wpm)

        # Check completion - this is the key fix
        if len(current_text) >= len(target_text):
            typed_text = "".join(current_text)
            if typed_text == target_text:
                # Calculate final WPM
                final_time = time.time() - start_time
                final_wpm = round((len(target_text) / (final_time / 60)) / 5)
                stdscr.addstr(6, 0, f"TEST COMPLETED! Final WPM: {final_wpm}")
                stdscr.refresh()
                stdscr.nodelay(False)
                curses.curs_set(1)
                return final_wpm
            elif len(current_text) == len(target_text):
                # Show mismatch
                stdscr.addstr(6, 0, "Mismatch detected - continue typing or backspace to fix")

        stdscr.refresh()

        try:
            key = stdscr.getkey()
        except curses.error:
            continue

        if ord(key) == 27:  # ESC key
            curses.curs_set(1)
            return 0

        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(current_text) > 0:
                current_text.pop()
        elif len(key) == 1 and key.isprintable():
            # Allow typing beyond target length for debugging
            current_text.append(key)


def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    start_screen(stdscr)
    while True:
        final_wpm = wpm_test(stdscr)
        stdscr.clear()
        if final_wpm > 0:
            stdscr.addstr(1, 0, f"Congratulations! You completed the test!")
            stdscr.addstr(2, 0, f"Your final WPM: {final_wpm}")
            stdscr.addstr(4, 0, "Press any key to try again or ESC to quit.")
        else:
            stdscr.addstr(2, 0, "Test cancelled. Press any key to try again or ESC to quit.")
        stdscr.refresh()
        key = stdscr.getkey()
        if ord(key) == 27:
            break


wrapper(main)
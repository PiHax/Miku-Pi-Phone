from PIL import Image, ImageDraw, ImageFont
from ST7735 import ST7735
import RPi.GPIO as GPIO
from time import sleep, strftime
import os

# GPIO Button Setup
buttons = {
    "up": 17,
    "down": 27,
    "select": 22,
    "back": 23
}
GPIO.setmode(GPIO.BCM)
for pin in buttons.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# LCD Setup
lcd = ST7735(port=0, cs=0, dc=25, backlight=18, rotation=90, spi_speed_hz=4000000)
lcd.begin()

# Fonts and Screen Setup
font = ImageFont.load_default()
menu_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
screen_width, screen_height = 128, 128

# Menu Options
menu_options = ["Clock", "Gallery", "Settings"]
current_option = 0
current_screen = "menu"
gallery_images = []
gallery_index = 0

# Load Gallery Images
image_folder = "/home/pi/miku_gallery"
if os.path.exists(image_folder):
    gallery_images = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(".jpg")]

def render_menu():
    """Renders the main menu."""
    image = Image.new('RGB', (screen_width, screen_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    for i, option in enumerate(menu_options):
        color = (255, 255, 255) if i == current_option else (100, 100, 100)
        draw.text((10, 20 + i * 30), option, fill=color, font=menu_font)
    lcd.display(image)

def render_clock():
    """Displays the current time."""
    while current_screen == "Clock":
        image = Image.new('RGB', (screen_width, screen_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        current_time = strftime("%H:%M:%S")
        draw.text((10, 50), current_time, fill=(255, 255, 255), font=menu_font)
        lcd.display(image)
        sleep(1)

def render_gallery():
    """Displays images from the gallery."""
    global gallery_index
    if not gallery_images:
        image = Image.new('RGB', (screen_width, screen_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((10, 50), "No Images", fill=(255, 255, 255), font=menu_font)
        lcd.display(image)
        sleep(2)
        return

    while current_screen == "Gallery":
        img = Image.open(gallery_images[gallery_index])
        img = img.resize((screen_width, screen_height))
        lcd.display(img)

        # Wait for navigation input
        button = button_pressed()
        if button == "up":
            gallery_index = (gallery_index - 1) % len(gallery_images)
        elif button == "down":
            gallery_index = (gallery_index + 1) % len(gallery_images)
        elif button == "back":
            break

def button_pressed():
    """Detects which button is pressed."""
    for name, pin in buttons.items():
        if GPIO.input(pin) == GPIO.LOW:
            sleep(0.2)  # Debounce
            return name
    return None

# Main Loop
try:
    while True:
        if current_screen == "menu":
            render_menu()
            button = button_pressed()
            if button == "up":
                current_option = (current_option - 1) % len(menu_options)
            elif button == "down":
                current_option = (current_option + 1) % len(menu_options)
            elif button == "select":
                current_screen = menu_options[current_option]
            elif button == "back":
                pass  # Do nothing

        elif current_screen == "Clock":
            render_clock()
            current_screen = "menu"

        elif current_screen == "Gallery":
            render_gallery()
            current_screen = "menu"

        elif current_screen == "Settings":
            # Add settings functionality here
            image = Image.new('RGB', (screen_width, screen_height), color=(0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.text((10, 50), "Settings Placeholder", fill=(255, 255, 255), font=menu_font)
            lcd.display(image)
            sleep(2)
            current_screen = "menu"

except KeyboardInterrupt:
    GPIO.cleanup()

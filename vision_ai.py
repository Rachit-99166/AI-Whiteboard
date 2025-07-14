from google import genai
import time
from google.genai import types
from PIL import Image
import pyautogui
import os
from dotenv import load_dotenv


class ScreenAnalyzer:
    def __init__(self):
        """Initialize the ScreenAnalyzer with the GenAI client."""
        load_dotenv()
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY"),
            http_options={"api_version": "v1alpha"},
        )

    @staticmethod
    def capture_screen():
        """Captures a screenshot and saves it as a JPEG file."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot_{timestamp}.jpeg"
        screenshot = pyautogui.screenshot()
        screenshot = screenshot.convert("RGB")
        screenshot.save(filename, format="JPEG")
        return filename

    @staticmethod
    def load_and_resize_image(image_path):
        """Loads and resizes the image to maintain aspect ratio."""
        with Image.open(image_path) as img:
            aspect_ratio = img.height / img.width
            new_height = int(img.width * aspect_ratio)
            return img.resize((img.width, new_height), Image.Resampling.LANCZOS)

    def analyze_screen(self, prompt):
        """Analyzes the screen based on a screenshot and prompt."""
        screen_path = self.capture_screen()
        screen = self.load_and_resize_image(screen_path)
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[prompt, screen],
            config=types.GenerateContentConfig(
                system_instruction="Only give the output of White Board. Ignore the other part of screen.",
            ),
        )
        return response.text

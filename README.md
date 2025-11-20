⌨️ Typing Speed Tester Application

This is a standalone desktop application built using Python and Tkinter designed to help users improve their typing speed and accuracy. The application offers a clean interface, light/dark theme options, and automatic scoring.

✨ Features

Timed Tests: Each test runs for a fixed duration of 5 minutes (300 seconds).

Difficulty Levels: Choose between EASY, MEDIUM, and HARD sentences, sourced from the included sample.txt file (covering topics like Physics, Biology, Math, etc.).

Live Scoring: Calculates and displays Words Per Minute (WPM) as you type.

Visual Feedback: Colors text instantly: green for correct characters, red for errors, and gray for extra characters.

Automatic Restart: After the time expires or you complete the sentence, a results popup appears, and a new test starts immediately upon closing the popup.

Theming: Toggle between Light and Dark modes.

📥 Installation and Setup (For Users)

Since this application is bundled into a single executable file (speed-test.exe), you do not need to install Python to run it.

Step 1: Download the Application Files

Download the speed-test.exe executable file for your operating system (typically found in the dist folder).

Download the sample.txt file, which contains all the testing sentences.

Step 2: Set Up the Directory

Create a dedicated folder for the application (e.g., TypingTester).

Place both speed-test.exe and sample.txt into this folder.

Step 3: Run the Application

Double-click the speed-test.exe file to launch the application.

💻 How to Use the Application

1. Starting the Test

When you first open the app, it is in a "Ready" state.

Select Difficulty: Use the dropdown menu at the top center to choose your difficulty level (EASY, MEDIUM, or HARD).

Click "Start Test": Press the Start Test button at the bottom center. A new, random sentence, corresponding to the selected difficulty, will load into the top text box.

2. Typing and Monitoring

Start Typing: Click inside the bottom input box (where the cursor is) and begin typing the sentence displayed above it.

Automatic Timer Start: The 5-minute timer only begins counting down when you press the first typing key.

Visual Feedback: The text you type will be colored:

Green Text: Correct characters match the source text.

Red Text: Incorrectly typed characters.

Live WPM: Your Words Per Minute (WPM) score will update live in the top-right box.

3. Test Completion and Results

The test ends immediately upon the timer reaching 0:00 or when you successfully complete the entire target sentence.

When the test ends, a popup window will display your final results, including:

Duration: How long the test ran in seconds.

Net WPM: Your final calculated Words Per Minute (WPM).

Character Errors: The total number of incorrect characters typed.

4. Continuous Testing

After reviewing your results, close the popup window.

The application will automatically load a new, random sentence and reset the timer, allowing you to quickly begin your next practice session.

5. Manually Resetting the Test

If you wish to stop a test midway, click the "Reset Test" button (which replaces the "Start Test" button while a test is running). This will clear your input and prepare the app for a new test.
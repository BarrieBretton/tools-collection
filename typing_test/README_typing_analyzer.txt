Typing Insight Lab

Files:
- typing_analyzer_app.html  -> single-file local web app

Run locally:
1. Open a terminal in the folder containing the file.
2. Start a local server:
   python -m http.server 8000
3. Open:
   http://localhost:8000/typing_analyzer_app.html

Notes:
- History and highscores are stored in your browser via localStorage.
- Use "Copy share summary" for a short clipboard-ready summary.
- Use "Copy share link" to create a URL that imports a report into the same app.
- Use "Export report JSON" for a portable report artifact.
- Use "Copy latest report JSON" to paste analysis elsewhere.

Metric definitions:
- Gross WPM: all typed non-backspace characters / 5 / minute.
- Net WPM: correctly aligned characters / 5 / minute.
- Strict correct words: completed words that exactly match the target word.
- Accuracy: correctly aligned characters divided by typed non-backspace characters.
- Consistency: lower volatility in rolling WPM samples gives a higher score.
- Score: weighted blend of net WPM, accuracy, and consistency.

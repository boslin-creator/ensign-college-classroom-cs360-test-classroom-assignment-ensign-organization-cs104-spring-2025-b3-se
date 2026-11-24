# Lab

**You will use the putting_python_to_work.py file to write your code**

In this lab, you will ask the user for the radius of a circle. You will then calculate the diameter, circumference, and area of that circle. Those values will then be printed out for the user.

The formulas you will need for this lab are the following:

- \( d = 2 \times r \): Diameter is twice the radius.
- \( c = 2 \times \pi \times r \): Circumference is two times Pi (\( \pi \approx 3.14 \)) times the radius.
- \( \text{Area} = \pi \times r^2 \): Area is Pi times the radius squared.

The key to writing good computer programs (i.e., code) is to plan out the process (i.e., algorithm) first, using pseudo-code and/or a flowchart. Before you write one line of Python code for this lab, plan it out using a flowchart.

Once you do write code, add comments to each line to indicate what is being accomplished in that line.

Click the terminal in the codespace and type `pytest` to test your code.

## Assistant ManagePro

The optional web assistant runs locally in your browser. Install the project
dependencies, set your Anthropic API key in PowerShell, then start the server:

```powershell
python -m pip install requests
$env:ANTHROPIC_API_KEY = "your-key"
python web_app.py
```

The app opens at `http://127.0.0.1:8000` on the computer and is also reachable
from an iPhone connected to the same Wi-Fi network at the local address printed
by the server. Keep the terminal window open while using it; press `Ctrl+C`
there to stop the server. The API key stays in the Python process and should
not be added to the HTML or committed to the repository.

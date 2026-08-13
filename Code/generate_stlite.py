import os

# Read the Streamlit app code
with open("Code/streamlit_app.py", "r") as f:
    app_code = f.read()

# Escape backticks for JavaScript template literals
escaped_code = app_code.replace("`", "\\`").replace("${", "\\${")

# Stlite HTML Template
html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>Streaming Marketplace Dashboard</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.58.0/build/stlite.css"
    />
    <style>
      /* Ensure the page takes up the full browser screen */
      html, body, #root {{
        margin: 0;
        padding: 0;
        height: 100%;
        background-color: #0e1117;
      }}
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.58.0/build/stlite.js"></script>
    <script>
      stlite.mount({{
        requirements: ["plotly", "pandas"],
        entrypoint: "streamlit_app.py",
        files: {{
          "streamlit_app.py": `{escaped_code}`,
          "cleaned_reelgood.csv": {{
            url: "cleaned_reelgood.csv"
          }}
        }}
      }}, document.getElementById("root"));
    </script>
  </body>
</html>
"""

# Write to Code/index.html
with open("Code/index.html", "w") as f:
    f.write(html_content)

print("Generated Code/index.html successfully for GitHub Pages deployment!")

Working at the Energy Information Administration (EIA), you might want to create a Sphinx theme that reflects the organization's branding and information architecture. Here's a step-by-step guide with sample code to create a Sphinx theme:

### Step 1: Set Up Your Sphinx Project

1. **Install Sphinx:**
   Ensure Sphinx is installed. If not, install it using pip:
   ```bash
   pip install sphinx
   ```

2. **Create a New Sphinx Project:**
   If you haven't already, initialize a new Sphinx project:
   ```bash
   sphinx-quickstart
   ```
   Follow the prompts to set up your project.

### Step 2: Create Your Theme Directory

1. **Theme Directory Structure:**
   Inside your Sphinx project, create a directory for your theme, say `eia_theme`. The structure should look like this:
   ```
   docs/  # Your Sphinx project
   ├── eia_theme/
   │   ├── static/
   │   │   ├── css/
   │   │   └── js/
   │   └── templates/
   │       └── layout.html
   └── conf.py
   ```

### Step 3: Develop the Theme

1. **Base Template:**
   Create a `layout.html` file inside the `templates` directory. This file will extend the basic layout provided by Sphinx.

   ```html
   <!-- eia_theme/templates/layout.html -->
   {% extends "!layout.html" %}

   {% block styles %}
   {{ super() }}
   <link rel="stylesheet" href="{{ pathto('_static/css/eia_style.css', 1) }}">
   {% endblock %}
   ```

2. **CSS File:**
   Create a CSS file `eia_style.css` in the `static/css/` directory. Add your custom styles here.

   ```css
   /* eia_theme/static/css/eia_style.css */
   body {
       font-family: Arial, sans-serif;
       color: #333333;
   }
   /* Add more custom styles */
   ```

3. **JavaScript (Optional):**
   If you need custom JavaScript, add it to the `static/js/` directory and link it in your `layout.html`.

### Step 4: Configure the Theme in Sphinx

1. **Update conf.py:**
   In your Sphinx project’s `conf.py`, set your custom theme:

   ```python
   # conf.py
   html_theme = 'eia_theme'
   html_theme_path = ['eia_theme']
   ```

### Step 5: Build and Test Your Theme

1. **Build Your Documentation:**
   From your Sphinx project directory, run:
   ```bash
   make html
   ```
   This generates the HTML documentation with your custom theme.

2. **Test Your Theme:**
   Open the generated HTML files in a browser to see your new theme in action. Ensure that it reflects EIA's branding and is user-friendly.

### Step 6: Iterate and Refine

1. **Iterate:**
   Based on your testing, iterate over your design. Update your templates, CSS, and JavaScript as needed.

2. **Responsive Design:**
   Ensure your theme is responsive and accessible, considering different devices and accessibility standards.

### Step 7: Document and Package (Optional)

1. **Document Your Theme:**
   Create a README or documentation explaining how to use your theme, especially if you plan to share it with other departments or teams.

2. **Package Your Theme:**
   If you wish to distribute your theme, package it as a Python package with a `setup.py` file.

### Additional Tips

- **EIA Branding:** Incorporate EIA's color scheme, typography, and logo to maintain brand consistency.
- **Performance:** Optimize your CSS and JavaScript for performance, especially for large documentation projects.
- **Feedback:** Gather feedback from colleagues and users to continuously improve the theme.

This guide provides a basic framework to start creating a custom Sphinx theme. Depending on your specific needs and the complexity of your documentation, you may need to delve deeper into Sphinx's theming capabilities.
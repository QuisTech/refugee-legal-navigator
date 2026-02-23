import pathlib

base = pathlib.Path(r'C:\Users\Administrator\Downloads\refugee-legal-navigator\webapp')

files = {}

files['postcss.config.js'] = (
    "export default {\n"
    "  plugins: {\n"
    "    tailwindcss: {},\n"
    "    autoprefixer: {},\n"
    "  },\n"
    "}\n"
)

files['tailwind.config.js'] = (
    "export default {\n"
    "  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],\n"
    "  theme: { extend: {} },\n"
    "  plugins: [],\n"
    "}\n"
)

files['index.html'] = (
    "<!DOCTYPE html>\n"
    "<html lang=\"en\">\n"
    "  <head>\n"
    "    <meta charset=\"UTF-8\" />\n"
    "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
    "    <title>Refugee Legal Navigator | Amazon Nova</title>\n"
    "    <script src=\"https://cdn.tailwindcss.com\"></script>\n"
    "    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
    "&family=Outfit:wght@600;700&display=swap\" rel=\"stylesheet\">\n"
    "    <style>body{font-family:Inter,sans-serif;background:#000;color:white}"
    "h1,h2,h3,h4{font-family:Outfit,sans-serif}</style>\n"
    "  </head>\n"
    "  <body>\n"
    "    <div id=\"root\"></div>\n"
    "    <script type=\"module\" src=\"/src/main.jsx\"></script>\n"
    "  </body>\n"
    "</html>\n"
)

files['src/main.jsx'] = (
    "import React from 'react'\n"
    "import ReactDOM from 'react-dom/client'\n"
    "import App from './App.jsx'\n"
    "import './index.css'\n"
    "\n"
    "ReactDOM.createRoot(document.getElementById('root')).render(\n"
    "  <React.StrictMode>\n"
    "    <App />\n"
    "  </React.StrictMode>,\n"
    ")\n"
)

files['src/index.css'] = (
    "@tailwind base;\n"
    "@tailwind components;\n"
    "@tailwind utilities;\n"
    "\n"
    ".glass {\n"
    "  background: rgba(255,255,255,0.05);\n"
    "  backdrop-filter: blur(10px);\n"
    "  border: 1px solid rgba(255,255,255,0.1);\n"
    "}\n"
    "\n"
    ".bg-dot-pattern {\n"
    "  background-image: radial-gradient(rgba(255,255,255,0.1) 1px, transparent 1px);\n"
    "  background-size: 20px 20px;\n"
    "}\n"
)

for name, content in files.items():
    p = base / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    print(f'OK: {name}')

print('All done')

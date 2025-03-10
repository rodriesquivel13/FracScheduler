from flask import Flask, render_template
import os

app = Flask(__name__, template_folder="C:\\Users\\Rodrigo Esquivel\\OneDrive - TERRA VITAL\\Rodrigo Esquivel\\Documentos\\ARCHIVOS\\ANALÍTICA\\SEASCAPE\\CALENDARIO DE FRACCIONES\\codigo\\templates")

@app.route("/")
def home():
    # Print the current template folder Flask is using
    print("Template folder:", app.template_folder)
    
    # Try to manually check if the template file exists
    template_path = os.path.join(app.template_folder, "chango.html")
    if not os.path.exists(template_path):
        print(f"Template not found at {template_path}")
        return "Error: Template not found!", 500

    return render_template("chango.html")

if __name__ == "__main__":
    print("Flask is running!")
    app.run(debug=True)
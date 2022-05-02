from data_satrapy import create_app


app = create_app()

app.app_context().push()

print("RIGHT AFTER CONTEXT PUSH")

if __name__ == "__main__":
    app.run(debug=True)

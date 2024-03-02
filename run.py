from soundbridge import create_app
from dotenv import load_dotenv

load_dotenv()

app = create_app()
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
import uvicorn
from streamview.app import app


def main():
    uvicorn.run("streamview.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()

import server
from config import DefaultConfig

application = server.create_app(DefaultConfig)

if __name__ == "__main__":
    application.run()


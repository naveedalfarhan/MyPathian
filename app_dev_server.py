from config import DevServerConfig
import server

application = server.create_app(DevServerConfig)

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8081)


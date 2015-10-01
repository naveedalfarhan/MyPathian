from config import ProdServerConfig
import server

application = server.create_app(ProdServerConfig)

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8081)


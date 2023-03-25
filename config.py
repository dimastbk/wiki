from pydantic import BaseSettings


class Config(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_PORT: int = 3306

    DB_REPLICA_HOST: str

    DB_GKGN_HOST: str
    DB_GKGN_NAME: str

    @property
    def SQLALCHEMY_BASE_URI(self) -> str:
        return "mysql://{user}:{password}@{host}:{port}/".format(
            user=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_GKGN_HOST,
            port=self.DB_PORT,
        )

    def SQLALCHEMY_DATABASE_URI(self, database: str = None) -> str:
        if database:
            return self.SQLALCHEMY_BASE_URI + self.DB_USER + "__" + database
        else:
            return self.SQLALCHEMY_BASE_URI + self.DB_GKGN_NAME

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PREFIX = "dimabot:cache:{}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Config()

from src.config import Settings


def test_cors_origins_split():
    settings = Settings(cors_origins="http://a.test,http://b.test")
    assert settings.cors_origins == ["http://a.test", "http://b.test"]

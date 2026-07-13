from dan.core.config import DANConfig


class TestDANConfig:
    def test_default_config(self):
        config = DANConfig()
        assert config.core.threshold == 1.0
        assert config.core.log_level == "INFO"
        assert config.interpret.name == "ollama"
        assert config.reason.name == "ollama"

    def test_from_file_nonexistent(self):
        config = DANConfig.from_file("/nonexistent/path.yaml")
        assert config.core.threshold == 1.0

    def test_save_and_load(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config = DANConfig()
        config.core.threshold = 2.5
        config.interpret.model = "custom-model"
        config.save(config_path)

        loaded = DANConfig.from_file(config_path)
        assert loaded.core.threshold == 2.5
        assert loaded.interpret.model == "custom-model"

    def test_from_dict_partial(self):
        data = {
            "core": {"threshold": 3.0},
        }
        config = DANConfig._from_dict(data)
        assert config.core.threshold == 3.0
        # Defaults preserved
        assert config.interpret.name == "ollama"

    def test_ensure_dirs(self, tmp_path):
        config = DANConfig()
        config.memory.long_term_path = str(tmp_path / "memory")
        config.skills.store_path = str(tmp_path / "skills")
        config.ensure_dirs()
        assert (tmp_path / "memory").is_dir()
        assert (tmp_path / "skills").is_dir()

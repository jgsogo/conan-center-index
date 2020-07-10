from conans import ConanFile, tools
import os


class TestPackgeConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self):
            self.run("ndk-build --version", run_environment=True)

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class FreelingConan(ConanFile):
    name = "freeling"

    description = "FreeLing is a C++ library providing language analysis functionalities" \
                  " (morphological analysis, named entity detection, PoS-tagging, parsing," \
                  " Word Sense Disambiguation, Semantic Role Labelling, etc.) for a variety" \
                  " of languages (English, Spanish, Portuguese, Italian, French, German," \
                  " Russian, Catalan, Galician, Croatian, Slovene, among others)."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://nlp.lsi.upc.edu/freeling/"
    license = "GNU Affero General Public License"
    topics = ("nlp", )
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "traces": [True, False],
        "warnings": [True, False],
        "xpressive": [True, False],
        "embeddings": [True, False],
        "java_api": [True, False],
        "python2_api": [True, False],
        "python3_api": [True, False],
        "perl_api": [True, False],
    }
    default_options = {
        'shared': False,
        'traces': False,
        'warnings': True,
        'xpressive': False,
        'embeddings': False,
        'java_api': False,
        'python2_api': False,
        'python3_api': False,
        'perl_api': False,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        self.requires.add("boost/1.72.0")
        self.requires.add("icu/64.2")

    def configure(self):
        if self.options.java_api or self.options.python2_api or self.options.python3_api:
            raise ConanInvalidConfiguration("To compile the APIs it requires SWIG (not available in Conan Center)")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('{0}-{1}'.format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["TRACES:BOOL"] = self.options.traces
        cmake.definitions["WARNINGS:BOOL"] = self.options.warnings
        cmake.definitions["XPRESSIVE:BOOL"] = self.options.xpressive
        cmake.definitions["EMBEDDINGS:BOOL"] = self.options.embeddings
        cmake.definitions["JAVA_API:BOOL"] = self.options.java_api
        cmake.definitions["PYTHON2_API:BOOL"] = self.options.python2_api
        cmake.definitions["PYTHON3_API:BOOL"] = self.options.python3_api
        cmake.definitions["PERL_API:BOOL"] = self.options.perl_api
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        #cmake.install()

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

import sys
import os
from cx_Freeze import setup, Executable

# ----------------------------------------------------------
# Config
# ----------------------------------------------------------
CONFIG_NUMPY = True
CONFIG_PYVISA = True
CONFIG_IPYTHON = False

# ----------------------------------------------------------
# Env detect
# ----------------------------------------------------------
Windows = sys.platform == "win32"

# add base_prefix for Python2.7
sys.base_prefix = getattr(sys, "base_prefix", sys.prefix)

# ----------------------------------------------------------
# Module Libs Include
# ----------------------------------------------------------
packaging_libs = ["packaging",
            "packaging.utils",
            "packaging.markers",
            "packaging._compat",
            "packaging.version",
            "packaging.specifiers",
            "packaging._structures",
            "packaging.requirements",
            ]
base_libs = ["atexit", "appdirs"] + packaging_libs

# --------------------------------------
if CONFIG_NUMPY:
    numpy_libs = dict(
        full = ["numpy"],
        condense = [
            "numpy.core._methods",
            "numpy.lib.format"
        ]
    )

# --------------------------------------
if CONFIG_IPYTHON:
    ipython_libs = dict(
        full = ["IPython", "qtconsole"],
        condense = [
            "IPython",
            "qtconsole.inprocess",
            "qtconsole.rich_ipython_widget"
        ]
    )

    # Fixup for Forzen apps, copy files need by IPython ,ipywidgets
    ipy_static = []
    from IPython.html import DEFAULT_STATIC_FILES_PATH
    custom = os.path.join('ipy-data', 'custom')
    for fname in ('custom.js', 'custom.css'):
        src = os.path.join(DEFAULT_STATIC_FILES_PATH, 'custom', fname)
        dest = os.path.join(custom, fname)
        ipy_static.append((src, dest))

    ipy_static.append(('README_STARTUP', os.path.join('ipy-data', 'profile', 'README_STARTUP')))

# --------------------------------------
if CONFIG_PYVISA:
    pyvisa_libs = dict(
        full = ["pyvisa", "pyvisa-py"]
    )
    pyvisa_libs["condense"] = pyvisa_libs["full"]

# ----------------------------------------------------------
# Other Config
# ----------------------------------------------------------
excludes = ["PyQt"]

include_msvcr = True

include_files = dict(
    linux = [],
    windows = [],
)

# ----------------------------------------------------------
# Conbine Option
# ----------------------------------------------------------
options = dict(
    build_exe = dict(
        includes = [],
        include_files = [],
        excludes = [],
    )
)

build_exe = options["build_exe"]

# --------------------------------------
# include libs
build_exe["includes"].extend(base_libs)
if CONFIG_IPYTHON:
    build_exe["includes"].extend(ipython_libs["condense"])

if CONFIG_NUMPY:
    build_exe["includes"].extend(numpy_libs["condense"])

if CONFIG_PYVISA:
    build_exe["includes"].extend(pyvisa_libs["condense"])

# --------------------------------------
# excludes libs
build_exe["excludes"].extend(excludes)

# --------------------------------------
# include_files
build_exe["include_files"].extend(
    include_files["windows"] if Windows else include_files["linux"])

if CONFIG_IPYTHON:
    build_exe["include_files"].extend(ipy_static)

if Windows:
    build_exe["include_msvcr"] = include_msvcr


base = "Win32GUI" if Windows else None
executables = [Executable("tool.py", base = base)]

print "========================================"
print "Log Config"
print "base = %s" % (base)
for k, v in build_exe.iteritems():
    print(k, v)
print "========================================"

setup(
    name = ["CredoDebugTool"],
    version = "0.0",
    description = "",
    executables = executables,
    options = options,
)

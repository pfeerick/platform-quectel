# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from bin_bc66 import makeHDR, makeCFG

def bc66_header(target, source, env):
    makeHDR( source[0].path )
    makeCFG( source[0].path )

def bc66_init(env):
    TOOL_DIR = env.PioPlatform().get_package_dir("tool-opencpu")
    CORE = env.BoardConfig().get("build.core") # "bc66"
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "opencpu", CORE)
    env.Append(
        CPPDEFINES=[ "CORE_"+CORE.upper(),  "_REENT_SMALL" ], # -D
        CPPPATH=[ # -I
            CORE_DIR,
            join(CORE_DIR, "include"),
            join(CORE_DIR, "ril", "inc"),
            join(CORE_DIR, "fota", "inc"),        
        ],
        CFLAGS=[
            "-mcpu=cortex-m4",
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16",
            "-fsingle-precision-constant",        
            "-mthumb",
            "-mthumb-interwork", 
            "-mlong-calls",       
            "-std=c99",
            "-c", "-g", "-Os",
            "-fno-builtin",         
            "-ffunction-sections",
            "-fdata-sections",
            "-fno-strict-aliasing",
            "-fno-common", 
            "-Wall",
            "-Wp,-w",               
            "-Wstrict-prototypes",                  
            "-Wno-implicit-function-declaration",
        ],

        LINKFLAGS=[        
            "-mcpu=cortex-m4",
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16",
            "-mthumb",
            "-mthumb-interwork",   
            "-nostartfiles",     
            "-Rbuild",        
            "-Wl,--gc-sections,--relax",
            "-Wl,-wrap=malloc",
            "-Wl,-wrap=calloc",
            "-Wl,-wrap=realloc",
            "-Wl,-wrap=free"   
        ],   
        LIBPATH=[CORE_DIR],
        LDSCRIPT_PATH=join(CORE_DIR, "linkscript.ld"), 
        LIBS=[ "gcc", "m", "app_start" ], 

        BUILDERS = dict(
            ElfToBin = Builder(
                action=env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O",
                    "binary",
                    "$SOURCES",
                    "$TARGET"
                ]), "Building $TARGET"),
                suffix=".dat"
            ),    

            MakeHeader = Builder( # Add Mediatek Header
                action = bc66_header, 
                suffix = ".bin"
            )        
        ), # dict

        UPLOADER=join(TOOL_DIR, CORE, "$PLATFORM", "coda"), 
        UPLOADERFLAGS=[ '"$BUILD_DIR/${PROGNAME}.cfg"', "--UART", "$UPLOAD_PORT", "-d" ],
        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS',

    ) # env.Append    

    libs = []
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework"),
            join( CORE_DIR ),
    ))
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "ril"),
            join(CORE_DIR, "ril", "src")
    ))
    env.Append( LIBS = libs )
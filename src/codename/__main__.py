import argparse
import sys
from colorama import Fore, init as colorama_init
from .cache import Cache
from .generator import Generator
from .config import Config


CONFIG_PATH_FLAG = '--config-path'
PROFILE_FLAG = '--profile'
PROFILE_FLAG_SHORT = '-p'
COUNT_FLAG = '--count'
COUNT_FLAG_SHORT = '-c'
TRY_COUNT_FLAG = '--try-count'
SORT_FLAG = '--sort'
SORT_FLAG_SHORT = '-s'
LIST_ALL_FLAG = '--list-all'
LIST_PROFILES_FLAG = '--list-profiles'
CLEAR_CACHE_FLAG = '--clear-cache'
QUIET_FLAG = '--quiet'
QUIET_FLAG_SHORT = '-q'

# TODO rewrite messages
PROGRAM_MESSAGE = 'Generate a code name list from the Wikipedia.'
CONFIG_PATH_FLAG_MESSAGE = 'a path to the configuration directory'
PROFILE_FLAG_MESSAGE = 'a profile name'
COUNT_FLAG_MESSAGE = 'a length of the generated list'
TRY_COUNT_FLAG_MESSAGE = 'a maximum number of tries of generating a valid ' \
    'code name'
SORT_FLAG_MESSAGE = ''
LIST_ALL_FLAG_MESSAGE = 'list all code names for the profile (must be a code ' \
    'name list)'
LIST_PROFILES_FLAG_MESSAGE = 'list available profiles'
CLEAR_CACHE_FLAG_MESSAGE = 'clear the cache'
QUIET_FLAG_MESSAGE = 'do not print additional messages (useful in scripts)'

CONFIG_CHANGED_MESSAGE = '{}The configuration has changed. Please run the ' \
    'program with the {} flag to clear the cache.{}'.format(
        Fore.YELLOW, CLEAR_CACHE_FLAG, Fore.RESET)
CACHE_CLEARED_MESSAGE = '{}The cache has been cleared.{}'.format(
    Fore.GREEN, Fore.RESET)

CONFIG_VERSION_CACHE_KEY = 'config_version'


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description=PROGRAM_MESSAGE, add_help=False)
    arg_parser.add_argument(
        '--help', '-h', action='help', help='show this help message and exit')
    arg_parser.add_argument(
        CONFIG_PATH_FLAG,
        type=str,
        nargs=1,
        default='../config/',
        help=CONFIG_PATH_FLAG_MESSAGE)
    arg_parser.add_argument(
        PROFILE_FLAG,
        PROFILE_FLAG_SHORT,
        type=str,
        nargs=1,
        default='main',
        help=PROFILE_FLAG_MESSAGE)
    arg_parser.add_argument(
        COUNT_FLAG,
        COUNT_FLAG_SHORT,
        type=int,
        nargs=1,
        default=10,
        help=COUNT_FLAG_MESSAGE)
    arg_parser.add_argument(
        TRY_COUNT_FLAG,
        type=int,
        nargs=1,
        default=64,
        help=TRY_COUNT_FLAG_MESSAGE)
    arg_parser.add_argument(
        SORT_FLAG,
        SORT_FLAG_SHORT,
        action='store_const',
        const=True,
        default=False,
        help=SORT_FLAG_MESSAGE)
    arg_parser.add_argument(
        LIST_ALL_FLAG,
        action='store_const',
        const=True,
        default=False,
        help=LIST_ALL_FLAG_MESSAGE)
    arg_parser.add_argument(
        LIST_PROFILES_FLAG,
        action='store_const',
        const=True,
        default=False,
        help=LIST_PROFILES_FLAG_MESSAGE)
    arg_parser.add_argument(
        CLEAR_CACHE_FLAG,
        action='store_const',
        const=True,
        default=False,
        help=CLEAR_CACHE_FLAG_MESSAGE)
    arg_parser.add_argument(
        QUIET_FLAG,
        QUIET_FLAG_SHORT,
        action='store_const',
        const=True,
        default=False,
        help=QUIET_FLAG_MESSAGE)
    return arg_parser.parse_args()


def get_simple_value(value):
    if isinstance(value, list):
        return value[0]
    return value


def main():
    colorama_init()
    args = parse_args()
    try:
        config = Config(get_simple_value(args.config_path))
        config.load()
        if args.list_profiles:
            profile_name_list = config.get_profile_name_list()
            profile_name_list.sort()
            for profile_name in profile_name_list:
                print(profile_name)
            sys.exit(0)
    except Config.ConfigException as e:
        print('\r{}{}{}'.format(Fore.RED, e, Fore.RESET), file=sys.stderr)
        if e.source_exception:
            print(e.source_exception, file=sys.stderr)
        sys.exit(1)
    cache = Cache(config.get_cache_directory())
    try:
        if args.clear_cache:
            cache.clear()
            if not args.quiet:
                print(CACHE_CLEARED_MESSAGE)
            sys.exit()
        if not args.quiet:
            config_version = cache.read(CONFIG_VERSION_CACHE_KEY)
            if config_version and config_version != config.get_version():
                print(CONFIG_CHANGED_MESSAGE)
        cache.write(CONFIG_VERSION_CACHE_KEY, config.get_version())
    except Cache.CacheException as e:
        print('\r{}{}{}'.format(Fore.RED, e, Fore.RESET), file=sys.stderr)
        if e.source_exception:
            print(e.source_exception, file=sys.stderr)
        sys.exit(2)
    generator = Generator(
        config,
        cache,
        get_simple_value(args.try_count),
        get_simple_value(args.quiet))
    try:
        code_name_list = None
        if args.list_all:
            code_name_list = generator.generate_all(
                get_simple_value(args.profile))
        else:
            code_name_list = generator.generate(
                get_simple_value(args.profile), get_simple_value(args.count))
        if args.sort:
            code_name_list.sort()
        for code_name in code_name_list:
            print(code_name)
    except Generator.GeneratorException as e:
        print('\r{}{}{}'.format(Fore.RED, e, Fore.RESET), file=sys.stderr)
        if e.source_exception:
            print(e.source_exception, file=sys.stderr)
        sys.exit(3)


main()

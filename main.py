import argparse
import yaml
import app

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", type=str, help="config file for transfer (full path please)", required=True)

    args = parser.parse_args()
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=Loader)

    logger = app.setup_logging(list(config)[0])

    try:
        app.run(config, logger)
    except Exception as e:
        logger.error("move failed:", str(e))

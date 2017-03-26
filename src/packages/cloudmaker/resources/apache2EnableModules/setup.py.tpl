import logging
import cloudmakerutils

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    modules = [{% for module in currentDroplet.currentSetupStep.modules -%}'{{ module}}'{%if not loop.last -%},{%- endif %}{%- endfor %}]
    cloudmakerutils.apache2EnableModules(modules)

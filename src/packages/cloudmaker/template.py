import jinja2
import logging

def renderTemplate(templateDir, templateName, target, templateArgs):
    jinja2Env = jinja2.Environment(loader=jinja2.FileSystemLoader(templateDir))
    template = jinja2Env.get_template(templateName)
    template.stream(templateArgs).dump(target)
    logging.info('rendered {0} to {1}'.format(templateName, target))

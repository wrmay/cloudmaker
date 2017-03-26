import logging
import subprocess
import cloudmakerutils

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    {% if currentDroplet.currentSetupStep.debconfSelections %}
    {% for selection in currentDroplet.currentSetupStep.debconfSelections %}
    cloudmakerutils.debconfSetSelections('{{ selection.package }}', '{{ selection.question }}', '{{ selection.questionType }}', '{{ selection.answer }}')
    {% endfor %}
    {% endif %}
    {% for package in currentDroplet.currentSetupStep.packages %}
    cloudmakerutils.aptInstall('{{ package }}')
    {% endfor %}


import json
import os

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def find_and_replace_placeholders(template_data, input_data):
    scenario_text = input_data[0]['scenario']
    choice_text = input_data[0]['choice']
    entities = input_data[0]['entities'].split(',')
    outcomes = input_data[0]['outcomes']

    for element in template_data['SurveyElements']:
        if element['Element'] == 'SQ':
            if 'Payload' in element and 'QuestionText' in element['Payload']:
                question_text = element['Payload']['QuestionText']
                if 'SCENARIO_TEXT' in question_text:
                    element['Payload']['QuestionText'] = question_text.replace('SCENARIO_TEXT', scenario_text)
                if 'CHOICE_TEXT' in question_text:
                    element['Payload']['QuestionText'] = question_text.replace('CHOICE_TEXT', choice_text)

        if element['Element'] == 'BL' and 'Payload' in element:
            for block_id, block in element['Payload'].items():
                if 'LoopingOptions' in block:
                    for outcome_index, outcome in enumerate(outcomes, start=1):
                        block['LoopingOptions']['Static'][str(outcome_index)]['1'] = outcome

        if element['Element'] == 'SQ' and 'Payload' in element and 'Choices' in element['Payload']:
            for entity_index, entity in enumerate(entities, start=1):
                if str(entity_index) in element['Payload']['Choices']:
                    element['Payload']['Choices'][str(entity_index)]['Display'] = entity

    return template_data

def update_looping_options(template_data, input_data):
    outcomes = input_data[0]['outcomes']

    for element in template_data['SurveyElements']:
        if element['Element'] == 'BL':
            payload = element.get('Payload', {})
            for block_id, block in payload.items():
                if block.get('Description') == 'outcome_block':
                    looping_options = block.get('Options', {}).get('LoopingOptions', {}).get('Static', {})
                    for idx, outcome in enumerate(outcomes, start=1):
                        looping_options[str(idx)] = {"1": outcome}
                    block['Options']['LoopingOptions']['Static'] = looping_options

    return template_data

def update_survey_name(template_data, input_file):
    input_filename = os.path.splitext(os.path.basename(input_file))[0]
    survey_name = "Annotation Validation Study [{}]".format(input_filename)
    if 'SurveyEntry' in template_data:
        template_data['SurveyEntry']['SurveyName'] = survey_name
    return template_data

def update_consent_question(template_data):
    for element in template_data['SurveyElements']:
        if element['Element'] == 'SQ':
            if element['Payload']['QuestionDescription'].startswith("CONSENT You are being asked"):
                # Update the question description
                element['Payload']['QuestionDescription'] = "CONSENT You are being asked to take part in a research study. Before you decide to participate in..."

                # Update the choices
                element['Payload']['Choices'] = {
                    "4": {
                        "Display": "I have read the consent form and agree to participate."
                    },
                    "5": {
                        "Display": "I do not agree to participate."
                    }
                }

                # Update the choice order if necessary
                element['Payload']['ChoiceOrder'] = ["4", "5"]
                break  # Assuming there's only one consent question

    return template_data

def update_specific_question(template_data):
    for element in template_data['SurveyElements']:
        if element['Element'] == 'SQ' and element['Payload']['QuestionDescription'].startswith("Given the above scenario and action choice, how likely is this outcome to occur?"):
            element['Payload']['Choices'] = {"1": {"Display": "&nbsp;"}}
            element['Payload']['ChoiceOrder'] = ["1"]
            break
    return template_data

def update_real_world_experience_question(template_data):
    for element in template_data['SurveyElements']:
        if element['Element'] == 'SQ' and element['Payload']['QuestionDescription'].startswith("Your task is to read a piece of text describing one person's real-world experience."):
            element['Payload']['Choices'] = {
                "1": {"Display": "Mary"},
                "2": {"Display": "Lamb"},
                "3": {"Display": "Snow"},
                "4": {"Display": "School"}
            }
            element['Payload']['ChoiceOrder'] = ["1", "2", "3", "4"]
            break
    return template_data

def update_template_with_multiple_inputs(template_file, input_files, output_directory):
    original_template_data = load_json_file(template_file)
    
    for input_file in input_files:
        template_data = original_template_data.copy()  # Work on a copy for each input file
        input_data = load_json_file(input_file)

        updated_data = find_and_replace_placeholders(template_data, input_data)
        updated_data_with_outcomes = update_looping_options(updated_data, input_data)
        updated_data_with_name = update_survey_name(updated_data_with_outcomes, input_file)
        updated_data_consent = update_consent_question(updated_data_with_name)
        updated_data_specific = update_specific_question(updated_data_consent)
        final_updated_data = update_real_world_experience_question(updated_data_specific)
        
        input_filename = os.path.basename(input_file)
        output_filename = "Formatted_" + input_filename
        output_file = os.path.join(output_directory, output_filename)
        
        with open(output_file, 'w') as file:
            json.dump(final_updated_data, file, indent=4)

# Paths to files and directories
template_file = '/Users/emreturan/Desktop/Annotation_Validation_Study_template.json'
input_files = ['/Users/emreturan/Desktop/qualtrics_scenarios_0_choice_1.json','/Users/emreturan/Desktop/qualtrics_scenarios_1_choice_2.json']
output_directory = '/Users/emreturan/Desktop/surveypipeline/'

update_template_with_multiple_inputs(template_file, input_files, output_directory)


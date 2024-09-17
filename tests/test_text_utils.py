import text_utils
import errors
import constants
import unittest
import config_models

def test_process_text(qtbot):

    # simple replacement
    text_processing = config_models.TextProcessing()
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Simple)
    rule.source = 'word_a'
    rule.target = 'word_b'
    text_processing.add_text_replacement_rule(rule)

    assert text_utils.process_text('sentence word_a word_c', text_processing) == 'sentence word_b word_c'

    # regex replacement
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule.source = '\(etw \+D\)'
    rule.target = 'etwas +Dativ'
    text_processing.add_text_replacement_rule(rule)

    assert text_utils.process_text('unter (etw +D)', text_processing) == 'unter etwas +Dativ'
    assert text_utils.process_text('<b>unter</b> (etw +D)', text_processing) == 'unter etwas +Dativ'


def test_replacement_regexp_error(qtbot):
    
    # regex replacement with error
    text_processing = config_models.TextProcessing()
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule.source = 'yoyo)'
    rule.target = 'rep'
    text_processing.add_text_replacement_rule(rule)

    testcase_instance = unittest.TestCase()
    testcase_instance.assertRaises(errors.TextReplacementError, text_utils.process_text, 'yoyo', text_processing)


    text_processing = config_models.TextProcessing()
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule.source = None
    rule.target = None
    text_processing.add_text_replacement_rule(rule)

    testcase_instance = unittest.TestCase()
    testcase_instance.assertRaises(errors.TextReplacementError, text_utils.process_text, 'yoyo', text_processing)    

def test_process_text_rules(qtbot):
    # by default, html processing enabled
    text_processing = config_models.TextProcessing()
    assert text_utils.process_text('word1<br/>word2', text_processing) == 'word1word2'
    # disable html processing
    text_processing.html_to_text_line = False
    text_processing.ssml_convert_characters = False
    assert text_utils.process_text('word1<br/>word2', text_processing) == 'word1<br/>word2'

    # add a replacement rule which targets the HTML tag
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Simple)
    rule.source = '<br/>'
    rule.target = ' linebreak '
    text_processing.add_text_replacement_rule(rule)
    text_processing.html_to_text_line = True
    # the expected replacement is not done, because text replacement rules have run after HTML replacement
    assert text_utils.process_text('word1<br/>word2', text_processing) == 'word1word2'
    text_processing.run_replace_rules_after = False
    # now, our replacement rules will run first
    assert text_utils.process_text('word1<br/>word2', text_processing) == 'word1 linebreak word2'

    # SSML replacements
    text_processing = config_models.TextProcessing()
    text_processing.ssml_convert_characters = True
    assert text_utils.process_text('patients age < 30', text_processing) == 'patients age &lt; 30'
    assert text_utils.process_text('M&A', text_processing) == 'M&amp;A'
    text_processing.ssml_convert_characters = False
    assert text_utils.process_text('patients age < 30', text_processing) == 'patients age < 30'


def test_regex_backref(qtbot):
    text_processing = config_models.TextProcessing()
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule.source = '(.*)\s+\((.*)\)'
    rule.target = '\\2 \\1'
    text_processing.add_text_replacement_rule(rule)

    source_text = 'word1 (word2)'
    expected_result = 'word2 word1'
    assert text_utils.process_text(source_text, text_processing) == expected_result

def test_regex_ignore_case_default(qtbot):
    text_processing = config_models.TextProcessing()
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule.source = 'abc'
    rule.target = 'def'
    text_processing.add_text_replacement_rule(rule)

    source_text = 'ABC123'
    expected_result = 'ABC123'
    assert text_utils.process_text(source_text, text_processing) == expected_result    

def test_regex_ignore_case(qtbot):
    text_processing = config_models.TextProcessing()
    text_processing.ignore_case = True
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule.source = 'abc'
    rule.target = 'def'
    text_processing.add_text_replacement_rule(rule)

    source_text = 'ABC123'
    expected_result = 'def123'
    assert text_utils.process_text(source_text, text_processing) == expected_result    


def test_strip_brackets(qtbot):
    text_processing = config_models.TextProcessing()

    text_processing.strip_brackets = False
    assert text_utils.process_text('word1 (word2)', text_processing) == 'word1 (word2)'

    text_processing.strip_brackets = True
    text_processing.html_to_text_line = False
    assert text_utils.process_text('word1 (word2)', text_processing) == 'word1 '
    assert text_utils.process_text('word1 [word2]', text_processing) == 'word1 '
    assert text_utils.process_text('word1 [word2][word3]', text_processing) == 'word1 '
    assert text_utils.process_text('word1[word2]', text_processing) == 'word1'
    assert text_utils.process_text('word1 {word2}', text_processing) == 'word1 '
    assert text_utils.process_text('word1 <word2>', text_processing) == 'word1 '
    assert text_utils.process_text('word1 <word2>(word3)[word4]', text_processing) == 'word1 '
    assert text_utils.process_text('word1 (word2) word3 (word4)', text_processing) == 'word1  word3 '
    assert text_utils.process_text('word1 [word2] word3 [word4]', text_processing) == 'word1  word3 '
    assert text_utils.process_text('word1 {word2} word3 {word4}', text_processing) == 'word1  word3 '
    assert text_utils.process_text('word1 <word2> word3 <word4>', text_processing) == 'word1  word3 '
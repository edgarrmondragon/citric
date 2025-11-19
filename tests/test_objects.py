from citric.objects import Question, QuestionGroup, Survey


def test_survey_to_xml_basic():
    survey = Survey(
        sid=123456,
        admin="Test Admin",
        adminemail="test@example.com",
        surveyls_title="Test Survey",
        languages=["en"],
        question_groups=[
            QuestionGroup(
                group_name="Test Group 1",
                description="Description for Test Group 1",
                questions=[
                    Question(title="Q1", question="Question 1 text"),
                    Question(title="Q2", question="Question 2 text"),
                ],
            ),
        ],
    )
    xml_output = survey.to_xml()
    assert "<LimeSurveyDocType>Survey</LimeSurveyDocType>" in xml_output
    assert "<group_name><![CDATA[Test Group 1]]></group_name>" in xml_output
    assert "<question><![CDATA[Question 1 text]]></question>" in xml_output
    assert "<admin><![CDATA[Test Admin]]></admin>" in xml_output
    assert "<adminemail><![CDATA[test@example.com]]></adminemail>" in xml_output
    assert "<surveyls_title><![CDATA[Test Survey]]></surveyls_title>" in xml_output
    assert "<language><![CDATA[en]]></language>" in xml_output

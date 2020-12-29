# Moodle Maker

Tools for generating Moodle Quizzes for import into moodle.

## Components

The following components will be developed:

1. **MoodleXMLBuilder** A set of classes for programmatically generating moodle quiz questions and outputing them as Moodle XML.
2. **MooQuizMarkdown** A markdown type spec for writing quizzes in plain text
3. **MooQuizMarkdownParser** A parser for reading in MooQuizMarkdown files and converting them to XML
4. **PhysicsQuestionGenerators** A set of classes for generating typical physics problems.

## To Dos:

###MoodleXMLBuilder

First attempt already made, can make quizzes with MC and Numerical Questions. 
* Add multiple answers to Numerical Questions
* Add other Question Types
* Add CDATA and format specification attributes
* Add additional undocumented attributes seen in output
* Try with Markdown and MathJax

###MooQuizMarkdown

* Create spec for each question type


%QUESTION:
%TYPE:numerical
%TEXT:



%ANSWER:
%TOLERANCE:
%

Abandoned this idea in preferance to 

###MooQuizMarkdownParser

* Test python-markdown parser for main text bits




* Look into base64 image conversion
* Inlining SVG
* Control spec
* Roll your own?

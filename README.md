# MooDown


## A streamlined markdown workflow for Moodle quiz creation

Moodle is a powerful opensource learning platform. It can do many great things but creating quizzes in Moodle is arduous. Even a simple multiple choice question requires filling in multiple boxes. Adding images, getting settings right, all require many steps. *MooDown* is an attempt to simplify matters. With MooDown you write your quizzes in your favorite text editor using a variant of the Markdown format, gather your images into the same folder or directory, then run a simple python script which will compile them into the Moodle XML format for simple one-file import into the Moodle question bank.

## Installation and requirements

MooDown was written in Python 3 and requires a standard Python installation. In particular it requires the packages: *markdown*, *lxml*, *base64*, *pathlib* and *re*.

## Features and limiatations

MooDown can handle all the Moodle question types except, for the moment, _matching_. Partial credit answers and answer-specific feedback are possible. Question text can contain formatting through standard markdown syntax and embedded images and equations in LaTeX / MathJax format. At present LaTeX / MathJax has some glitches in multiple choice answers and images are not supported in multiple choice answer texts. Cloze format questions must be entered verbatam using the [Cloze format](https://tinyurl.com/y4rzv8xw "Cloze format specification").
MathJax sections must be escaped:
~~~
\\\( y = a x^2 + b x + c \\\)
~~~
At the moment _general feedback_, options related to multiple attempts like penalties etc are not implemented. Neither are quiz-level options such as category tags. Description "questions" are also not supported. MooDown prepares questions for loading into the question bank and these options are more for when you are designing the quiz itself.

## Usage

To run MooDown from the command line run
~~~
python MooDown.py quizfile.md
~~~
The program will output the file '''quizfile.xml''' to the same directory. At the present this is a rough beta so there is little by the way of error checking or helpful messages - check your questions after import before opening them to students!

The XML file can be imported into Moodle by going to "import questions" option under Quiz Bank and choosing Moodle XML as the import file type. The questions will then be available to be added to Quizzes.

## Writing quizzes

Quizzes use the markdown format. For a review of the format itself take a look at this [Markdown cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Here-Cheatsheet "Markdown cheatsheet"). In the context of MooDown your document must have the following structure

A first level heading starts a question and the heading text will be the name of the question
~~~
# Question Name
~~~

Next you can put the text of the question in standard markdown format.

~~~
Why did James Hoyland create *MooDown*?
~~~

Question text can contain any standard markdown formatting for emphesis, lists etc. I cannot contain level 1 headings as this starts a new question. It can contain level 2 headings as long as they don't begin with the letters _ANS_ or _CLOZE_ as they have special meaning.

The answer section is started by a second level header, the text of which must begin with _ANS_ (not case sensitive)

~~~
## Answer
~~~

### Multiple choice

The answer section determines the question type. For a multiple choice question enter a numbered list.

~~~
1. For the betterment of humanity
2. Because he was too lazy to use the online editor
3. As a procrastination technique to avoid real work
4. For giggles
~~~

With no further options the first answer is assumed correct and all others incorrect. Answer shuffling should be enabled by default on import.

If you want another answer to be correct you can specify by using the \# symbol at the end of the line and the frction number

~~~
1. For the betterment of humanity
2. Because he was too lazy to use the online editor #100
3. As a procrastination technique to avoid real work #50
4. For giggles
~~~

In the example above example answer 2 is correct and answer 3 is partially correct. Moodle requires at least one answer be 100% correct. Setting a fraction for any answer overrides the first answer correct default so you will have to manually put in #100 for the first answer if you want it correct. Instead of writing #100 you can use #* as a shortcut.

Only single selection multi-choice is supported at the moment.


Feedback can be added for individual answers using text in double quotes after the answer.

~~~
1. For the betterment of humanity "Are you kidding me?"
2. Because he was too lazy to use the online editor "Obvs" #100
3. As a procrastination technique to avoid real work "Well kinda" #50
4. For giggles "No, he's a serious academic - really!"
~~~

Feedback is a bit limited at the moment - just plain text. Note feedback has to come before question mark fraction.

### True-false

True false is the same as multiple choice except the first answer must be either true or false (not case-sensitive)

~~~
# A TF question

MooDown is just what we've all been looking for.

## Ans

1. True
~~~

Note the first answer is alway correct in true-false any other answers are ignored. The second answer will automatically be the opposite of the first. Fraction specifications are also ignored. You can put in answer feedback as with multiple choice. The only reason to put in a second line is to give wrong answer feedback e.g.

~~~
# A TF question

MooDown is just what we've all been looking for.

## Ans

1. True "Damn strait"
2. "Get outa here"
~~~

Note the numbers and the quotes on the wrong answer feedback are required. If you put in an answer on 2 it will be ignored as will any subsiquent answers.

### Numerical questions

Numerical answers are given via an unorderd list.

~~~
# Hard math question

What is \(2+2\)

## Answer

* 4
~~~

A bulleted list is indicated by the asterisk at the beginning of the line. This is required even if there is only one answer. Multiple answers can be provided to allow individual feedback on specific wrong answers or partial credit.

~~~
# Hard math question

What is \(2+2\)

## Answer

* 4 
* 3
* 2
~~~

Again by default the first answer is correct and all others are wrong and score zero. Feedback is and partial credit exactly as with multichoice

~~~
# Hard math question

What is \(2+2\)

## Answer

* 4 "Correct!" #100
* 3 "Close" #50
* 2 "Um. No"
~~~

For numerical questions you can also specify a tolerance. This is done with a value in curly braces after the answer

~~~
# Hard math question

What is \(2+2\)

## Answer

* 4 {0.5} "Correct!" #100
* 3 "Close" #50
* 2 "Um. No"
~~~

For more details on how the tolerancing works in Moodle check out the Moodle specification. Answers in numerical questions are checked to see if they are valid numbers, if not the question is interpreted as a short answer question.

### Short Answers

Short answer questions take a single short word or phrase as the answer. In MooDown you code them just like a numerical question but the answers are non-numerical.

~~~
# A short answer question

What word or phrase comes to mind when thinking of MooDown?

## answer

* Wonderful
~~~

Again feedback and partial credit answers can be given. For short answer questions it can be useful to have more than one correct answer to allow for small variations in students correct answers.


~~~
# A short answer question

What word or phrase comes to mind when thinking of MooDown?

## answer

* Wonderful "You're too kind" #100
* Life-changing "You're welcome" #100
* Life changing "Thanks!" #100
* Adequate "Rude" #50
~~~

### Cloze questions

Cloze questions use a special format to embed questions within a body of text. This can be used for multipart questions or fill in the blank type questions. You create cloze questions by inserting special codes inside the actual question text. To indicate a cloze question include a second level header right after the question name:

~~~
## cloze
~~~

This is not case sensitive. There is no answer section in a cloze question and a second level header matching an answer section will just be formatted as part of the question text if you use it.

### Essay question

Essay question is the default. If no other question type has been established, MooDown will assume it's an essay question. Essay questions must be manually marked. There is at present no options implement for essay questions such as specifying hand in method etc. No answer section is needed.

~~~
# Ode to MooDown

Write an essay on the wonders of MooDown. Make specific reference to its many positive qualities.

~~~

## Internals

MooDown reads in the source which if you've followed the guide above will be a standard well-formed markdown document. Python parses the markdown into a flat HTML document which is then post-processed by searching for level 1 headers and then interpreting the contents. Question text (before the answer section) is essentially kept in the HTML format as parsed. However, img tags are scanned and images opened and embedded in the question text as base-64 encoded data (currently only PNG and JPG are supported). In future SVG will be embedded directly. Question text section is wrapped in CDATA tags. This is essential for correct import when the question text contains HTML.
Feedback and answers are not processed into CDATA tags at present and so cannot contain more complex HTML thought they seem to cope with simple emphesis etc.

# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 13:16:46 2020

@author: James Donaldson Hoyland

MIT License

Copyright (c) 2020 James Donaldson Hoyland

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from markdown import markdown
from lxml import etree as et
from pathlib import Path
import re
import base64
import os
import argparse

# Puts the text in a div element - thought I would use it more, didn't really need a function

def wrapDiv(tx):
    
    return "<div>" + tx + "</div>" 

def wrapSpan(tx):
    
    return "<span>" + tx + "</span>"


def ElementWithText(name,text,textname='text',CDATA=True):

    el = et.Element(name)

    elText = et.SubElement(el,textname)

    if CDATA:
        elText.text = et.CDATA(text)
    else:
        elText.text = text

    return el

def SubElementWithText(parent,name,text,textname='text',CDATA=True):

    el = ElementWithText(name,text,textname,CDATA)

    parent.append(el)

    return el


# Extracts mark fraction from end of answer lines
# Returns None if no fraction found.

def getFraction(txt):
    
    match = re.findall(r'\#(\*|\d{1,3})$',txt)
    
    frac = 0
    
    if len(match) > 0:
        
        if match[0] == '*':
            
            frac = 100
            
        else:
                                
            frac = max(min(100,int(match[0])),0)
            
    else:
        
        return None
            
    return frac

# Extracts feedback text. 
# Returns None if none found

def getFeedback(txt):
    
    match = re.findall(r'"([^"]*)"',txt)
    
    if len(match) > 0:
        
        return match[0]
    
    else:
        
        return None
    
# Extracts tolerance in numeric questions. 
# Returns None if none found or tolerance was invalid (not convertable to float)    

def getTolerance(txt):
     
    match = re.findall(r'\{(.*?)\}',txt)

    if len(match) > 0:
        
        try:
            float(match[0])
            return match[0]
        except ValueError:
            return None
    
    else:
        
        return None 

# Parses the ordered and unordered lists as answers to numerical, multiple choice, true-false or short answer questions 

def parseListAnswers(listElement):
    
    qtype = 'unknown'
    fracset = False
    
    # List to store multiple answers 
    
    answers = []
    
    # Ordered list defaults to mc and unordered to numerical
    
    if listElement.tag == 'ol':
        
        qtype = 'multichoice'
        
    else:
        
        qtype = 'numerical'
        
    # Step through the list item elements - each one represents one answer
    
    for answer in listElement.iter('li'):
        
        atext = re.split('[\{"#]',answer.text)[0].strip()
        
        fb = getFeedback(answer.text)
        
        # if this s the first answer check to see if it is true / false
        
        if len(answers) == 0:
            
            firstWord = atext.split(None,1)[0].lower()
            
            if firstWord in 'truefalse':
                
                qtype = 'truefalse'
                
                # Create the true and false answers - this is really a special case of multichoice
                
                answers.append({'ans':firstWord,'tol':None,'fbk':fb,'frc':'100'})
                answers.append({'ans':qtype.replace(firstWord,''),'tol':None,'fbk':None,'frc':'0'})
                
                fracset = True
                
                continue
            
        # If we've already established this is true false the second answer is only there to provide feedback for incorrect
                
        if qtype == 'truefalse':
            
            answers[1]['fbk']=fb
             
            break
        
        tolerance = None

        # If this is a numercal question try to convert the answer to a number - if this fails the question switches to short answer

        if qtype == 'numerical':

            try:
                a = float(atext)
                tolerance = getTolerance(answer.text)
            except ValueError:
                qtype = 'shortanswer'
                
        # Get the score for this question. Set to zero if none found. 
        
        frac = getFraction(answer.text)
        
        if frac is not None:
            
            fracset = True
            
        else:
            
            frac = '0'
            
        # Append the answer to the list
            
        answers.append({'ans':atext,'tol':tolerance,'fbk':fb,'frc':frac})
        
    # If no fraction was specified for any answer, set the first answer to 100% correct
        
    if not fracset and len(answers)>0:
        answers[0]['frc']=100
        
    return (answers,qtype)
        

# Generate an XML answer. Non-numerical answers need their answers wrapped in CDATA section

def createAnswerXML(answer,isNumeric=True):

    answerElement = ElementWithText('answer',answer['ans'],CDATA = not isNumeric)
    answerElement.set('fraction',str(answer['frc']))

    if 'tol' in answer:

        if answer['tol'] is not None:

            SubElementWithText(answerElement, 'tolerance', answer['tol'], CDATA = False)

    if answer['fbk'] is not None:

        SubElementWithText(answerElement,'feedback',answer['fbk'])

    return answerElement

# Generate a cloze format numeric answer 

def createAnswerCloze(answer):
    
    answerString = "%{}%{}".format(answer['frc'],answer['ans'])

    if answer['tol'] is not None:

        answerString += ":{}".format(answer['tol'])

    if answer['fbk'] is not None:

        answerString += "#{}".format(answer['fbk'])

    return answerString
    
# Question text must be wrapped in CDATA tags. This function does that and also base64 converts
# image tag contents. Yes, yes I know functions should just do one thing - I'll fix it later
    
             
def generateCDATA(qtextElement):

    # Locate image tags in the XML
    images = qtextElement.findall('.//img')
    
    # Iterate over the image tags
    for image in images:
        
        # Get the image filename and extension
        src = image.get('src')
        extension = os.path.splitext(src)[1][1:] 
        
        # For jpegs and pngs, open the image file and base64 encode it, replacing the file link
        # With the encoded image in the HTML. Change tag atributes accordingly
        if extension in "jpeg jpg png":
        
            with open(src,'rb') as img_file:
                
                image64 = base64.b64encode(img_file.read()).decode('utf-8')
                imageString = "data:image/" + extension + ";base64," + image64
                image.set('src',imageString)
                
            # TO DO: Warn could not open img_file
                
        # TO DO: for SVG load and integrate the SVG into the HTML directly
        # TO DO: skip Base 64 encoding for web images
        # tO DO: raise all heading levels by 2 to allow H1 / H2 in question text
                
    # Convert the HTML back to a string and embed it in a CDATA section
    
    return et.CDATA(et.tostring(qtextElement,pretty_print=True).decode('utf-8'))      

        
# Parse arguments for input filename

argparser = argparse.ArgumentParser()
argparser.add_argument('fn',type=str,help='Markdown format source file')
argparser.add_argument('-html',action='store_true',help='Output intermediate HTML (mostly for debugging)')
argparser.add_argument('-echo',action='store_true',help='Print final XML to console')
args = argparser.parse_args()

# Read file

contents = Path(args.fn).read_text()
fnroot = os.path.splitext(args.fn)[0]
save_html = args.html
echo_to_console = args.echo

# Parse markdown into HTML

htmlString = markdown(contents)

# Create a div to act as the root node so we have a well formed doc

htmlTree = et.fromstring(wrapDiv(htmlString))

#print(et.tostring(htmlTree,pretty_print=True).decode('utf-8'))

tree = et.ElementTree(htmlTree)

if save_html:
    tree.write(fnroot+'.html', pretty_print=True, xml_declaration=True,   encoding="utf-8")

quiz = et.Element('quiz')

# Step through sibling elements 

mode = 'start'
qtype = 'none'
answercount = 0
questioncount = 0

# Find the top level headings - these define the questions

for h1 in tree.iter('h1'):
    
    # question type is initially unknown
    
    mode = 'question'
    qtype = 'unknown'
    
    questioncount = questioncount + 1
    
    # Create an empyy question
    
    question = et.SubElement(quiz,'question')
    qName = et.SubElement(question,'name')
    qNameText = et.SubElement(qName,'text')
    qNameText.text = h1.text
    
    questionText = et.SubElement(question,'questiontext')
    questionText.set("format","html")
    questionTextText = et.SubElement(questionText,'text')  
    
    qtextContents = et.Element('div')
    
    for su in h1.itersiblings():

        skipTag = False
        
        if su.tag == 'h1': # Found another question - TO DO wrap up to determine is the previous question was valid
            
            break
        
        if su.tag == 'h2' and su.text.lower().startswith('cloze'):
            
            qtype = 'cloze'
            mode = 'cloze'
            question.set("type",qtype)
            
            continue
            
        
        # An H2 tag starting 'ans' (case insensitive) starts the answer section of the question
            
        
        if su.tag == 'h2' and su.text.lower().startswith('ans') and qtype == 'unknown':
            
            # Finish the question text by converting to CDATA            
            questionTextText.text = generateCDATA(qtextContents)
            # Create an empty div for the next question's text
            qtextContents = et.Element('div')            
            
            mode = 'answer'
            
            continue
            
            
        if mode == 'answer':
        
            if su.tag in 'ol ul':
                
                answers,qtype = parseListAnswers(su)
                question.set("type",qtype)
                
                for answer in answers:
                    
                    answerXML = createAnswerXML(answer,qtype=='numerical')
                    question.append(answerXML)
                    
                continue
                     
        if mode == 'cloze':
            
            if su.tag in 'ol ul':
                
                answers,qtype = parseListAnswers(su)
                clzqtext ="{{1:{}:".format(qtype.upper())
                first = True
                 
                for answer in answers:
                    
                    if first:
                        first = False
                    else:
                        clzqtext = clzqtext + '~'
                        
                    answerStr = createAnswerCloze(answer)
                    clzqtext = clzqtext + answerStr
                    
                clzqtext = clzqtext + '}'
                
                clzqel = et.Element('span')
                clzqel.text = clzqtext
                qtextContents.append(clzqel)
                
                continue                
                    
        qtextContents.append(su)
        
    if not mode=='answer':  # No answer section was found
        
        questionTextText.text = generateCDATA(qtextContents)    
        # TO DO: Check for Cloze        
        qtextContents = et.Element('div')   
                        
        answer = et.SubElement(question,'answer')  
        answerText = et.SubElement(answer,'text')
        answer.set('fraction','0')
    
    if qtype=='unknown':
                
        question.set("type","essay")
          
        
if args.echo:    
    print(et.tostring(quiz,pretty_print=True).decode('utf-8'))
    
print("\nFound {} questions in file {}. Outputting to {}.xml".format(questioncount,args.fn,fnroot))

quizoutput = et.ElementTree(quiz)
quizoutput.write(fnroot+'.xml', pretty_print=True, xml_declaration=True,   encoding="utf-8")

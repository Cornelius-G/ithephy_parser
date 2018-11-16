headerfile = "header.html"
outputfile = "body.html"

#====================================================================

import sys
import string


letters = list(string.ascii_lowercase) # a, b, c, d, ....


 # create dictionary of labels: 1:label1, 2:label2 ...
def create_label_dict(s):
    refs = {}
    s = s.split("\\label{")
    l = len(s)
    for i in range(1, l):
        ref = s[i].split("}")[0]
        refs[i] = ref
    return refs


# get header informations
def getheader(s, keyword): 
    s = s.split("\\renewcommand{\\"+keyword+"}{")
    s = s[1].split("}")
    return s[0]


# replace every nth appearence of sub with repl
def nth_repl_all(s, sub, repl, nth): 
    find = s.find(sub)
    # loop util we find no match
    i = 1
    while find != -1:
        # if i  is equal to nth we found nth matches so replace
        if i == nth:
            s = s[:find]+repl+s[find + len(sub):]
            i = 0
        # find + len(sub) + 1 means we start after the last match
        find = s.find(sub, find + len(sub) + 1)
        i += 1
    return s


# replace math environments like $, \begin{align} and \begin{align*} with html: \( \)
def replace_math(s): 
    s=nth_repl_all(s, "$", "\) ", 2)
    s=nth_repl_all(s, "$", " \(", 1)
    s=s.replace("\\begin{align}"," \\begin{equation} ")
    s=s.replace("\\end{align}","\\end{equation} ")
    s=s.replace("\\begin{align*}"," \\begin{equation}")
    s=s.replace("\\end{align*}","\\end{equation} ")
    s=s.replace("&", "") # removes &-alignments
    s=s.replace("\\\\", "") # removes line-breaks
    return s


# divides elements like tasks, hints and controlresults in main and sub-elements
def divide_elements(s):
    tasks=[]
    if s.count("\item") == 0:
        return [s], [""]
    s=s.split("\\begin{enumerate}[a)]")
    tasks.append(s[0])

    sub = s[1].split("\item")
    end = sub[-1].split("\end{enumerate}")
    sub[-1] = end[0]
    tasks.append(end[1])

    for j in range(len(tasks)):
        tasks[j] = tasks[j].replace("\t","")
        tasks[j] = tasks[j].replace("\n","")

    for i in range(len(sub)):
        sub[i] = sub[i].replace("\t","")
        sub[i] = sub[i].replace("\n","")

    return tasks, sub
#============ End of parser function definitions =====================================#
#=====================================================================================#


path = sys.argv[1]

with open(path) as file:
    file_contents = file.read()

#========== get header information ===========
start = file_contents.split('begin{task}')
header = start[0]

exercisename = getheader(header, "exercisename")
exercisename = replace_math(exercisename)
topic = getheader(header, "topic")
topic = replace_math(topic)
exsubject = getheader(header, "exsubject")
extype = getheader(header, "type")
level = getheader(header, "level")
keywords = getheader(header, "keywords")
keywords = replace_math(keywords)
keywords = keywords.split("{")[1]


#=========== get exercise tasks ===========
file_contents = start[1]

# replace labels and refs with numbers
refs = create_label_dict(file_contents)
for key, ref in refs.items():
    file_contents=file_contents.replace("\\label{"+ref+"}", "("+str(key)+")")
    file_contents=file_contents.replace("\\ref{"+ref+"}", str(key))
    file_contents=file_contents.replace("\\eqref{"+ref+"}", "("+str(key)+")")

step_1=file_contents.split('\end{task}')
exercise=step_1[0]

exercise = replace_math(exercise)
tasks, subtasks = divide_elements(exercise)


#=========== get first-level hints ===========
step_2=step_1[1].split('begin{firstlevelhints}')
step_3=step_2[1].split('\end{firstlevelhints}')
firstlevelhints=step_3[0]

firstlevelhints = replace_math(firstlevelhints)
first_hints, first_subhints = divide_elements(firstlevelhints)


#=========== get second-level hints ===========
step_4=step_3[1].split('begin{secondlevelhints}')
step_5=step_4[1].split('\end{secondlevelhints')
secondlevelhints=step_5[0]

secondlevelhints = replace_math(secondlevelhints)
second_hints, second_subhints = divide_elements(secondlevelhints)

#=========== get control results ===========
step_6=step_5[1].split('begin{controlresults}')
step_7=step_6[1].split('\end{controlresults}')
controlresults=step_7[0]

controlresults = replace_math(controlresults)
result, subresults = divide_elements(controlresults)

for item in step_5[1].split("\n"):
    if "begin{controlresults}" in item:
        if item.strip()[0]=='%':
            result=[""]
            subresults=[""]


#===========get solution ===========
step_8=step_7[1].split('begin{solution}')
step_9=step_8[1].split('\end{solution}')
solution=step_9[0]

solution = replace_math(solution)
solution, solutions = divide_elements(solution)

#============ End of parser ==========================================================#
#=====================================================================================#



#====================================================================================#
#        To HTML
#====================================================================================#

info = []

def task(s,item=""):
    global info
    info.append(["task",s,item])
    
def subtask(s, item=""):
    global info
    info.append(["subtask",s,item])
    
def hint1(s,item=""):
    global info
    if(len(s)>1):
        info.append(["hint1",s])
    
def hint2(s,item=""):
    global info
    if(len(s.replace(" ",""))>1):
        info.append(["hint2",s,item])
    
def controlresult(s,item=""):
    global info
    if(len(s)>1):
        info.append(["controlresult",s,item])


# add main taks
task(tasks[0])
if(first_hints[0].strip()):
    hint1(first_hints[0])
if(second_hints[0].strip()):  
    hint2(second_hints[0])
if(result[0].strip()):  
    controlresult(result[0])

# add subtasks
for i in range(1,len(subtasks)):
    subtask(subtasks[i], item=letters[i-1])
    try:
        hint1(first_subhints[i])
    except IndexError:
        pass
    try:
        hint2(second_subhints[i])
    except IndexError:
        pass
    try:
        controlresult(subresults[i])
    except IndexError:
        pass



def str_to_raw(s):
    raw_map = {8:r'\b', 7:r'\a', 12:r'\f', 10:r'\n', 13:r'\r', 9:r'\t', 11:r'\v'}
    return r''.join(i if ord(i) > 32 else raw_map.get(ord(i), i) for i in s)

def WriteHeader():
    
    out=open(headerfile,"w")
        
    out.write("""
    <table>
    <thead></thead>
    <tbody>
    <tr>
    <td><span style="font-size: medium;"><b>Topic:</b></span></td>
    <td><span style="font-size: medium;">""" + topic + """</span></td>
    </tr>
    <tr>
    <td><span style="font-size: medium;"><b>Type:</b></span></td>
    <td><span style="font-size: medium;">""" + extype + """</span></td>
    </tr>
    <tr>
    <td><span style="font-size: medium;"><b>Level:</b></span></td>
    <td><span style="font-size: medium;">""" + level + """</span></td>
    </tr>
    <tr>
    <td valign="top"><span style="font-size: medium;"><b>Keywords:  &nbsp; &nbsp; <br /></b></span></td>
    <td><span style="font-size: medium;">""" + keywords + """</span></td>
    </tr>
    </tbody>
    </table> """)
    
    out.close()


def hidedivs(): # javascript for showing/hiding divisions
    return """<script type="text/javascript">
// <![CDATA[
function ShowHide(divId)
{if(document.getElementById(divId).style.display == 'none')
{document.getElementById(divId).style.display='block';}
else{document.getElementById(divId).style.display = 'none';}}
// ]]></script> \n """  


def hiddendiv(h, indent=False):
    if indent:
        return """\n<p></p><div class="mid" id="HiddenDiv"""+str(h[1])+"""" style="display: none; margin-lift: 20px;">
<div class="" style="font-size: medium; margin-left: 2em; margin-bottom: 1em">"""+h[2]+h[0]+"""</div>
<p></p>
</div>"""
    
    else:  
        return """\n<p></p><div class="mid" id="HiddenDiv"""+str(h[1])+"""" style="display: none; margin-lift: 20px;">
<div class="" style="font-size: medium; margin-left: 1em; margin-bottom: 1em">"""+h[2]+h[0]+"""</div>
<p></p>
</div>""" # was: <span class="" style....


def WriteHTML():
    
    out=open(outputfile,"w")
    
    # javascript for showing/hiding divs
    out.write(hidedivs())

    
    hiddencounter=0
    hiddendivs=[]
    
    taskflag=""


    for i, o in enumerate(info): # for all objects in info (i.e. task or hint1 or hint2 or control result)
        #o[1]=str_to_raw(o[1])
        
        if (o[0]=="task"): # Task that is not numerated
            out.write("""\n<p></p><span class="" style="font-size: medium; margin-bottom: 30px">\n"""+o[1]+"""</span>""")
            taskflag="task"
            
            
        if (o[0]=="subtask"): # Subtask that is numerated
            out.write("""\n<p></p><br /><span class="" style="font-size: medium; margin-left: 1em; margin-bottom: 30px">\n"""+o[2]+") "+o[1]+"""</span>""")
            taskflag="subtask"
                
            
        if (o[0]=="hint1"):
            hiddencounter+=1
            out.write(
            """<a onclick="javascript:ShowHide('HiddenDiv"""+str(hiddencounter)+"""')"><span class="" style="font-size: medium;cursor: pointer;margin: 0; padding: 0; border: 0"><img alt="" class="img-responsive atto_image_button_text-bottom" role="presentation" src="https://moodle.ithephy.eu/pluginfile.php/173/mod_folder/content/0/hint1.png" title="show/hide first hint" height="25" width="25"></span></a>\n""")
            hiddendivs.append([o[1],hiddencounter,"<u>Hint1:</u> "])
            
            
        if (o[0]=="hint2"):
            hiddencounter+=1
            out.write(
            """<a onclick="javascript:ShowHide('HiddenDiv"""+str(hiddencounter)+"""')"><span class="" style="font-size: medium;cursor: pointer;margin: 0; padding: 0; border: 0"><img alt="" class="img-responsive atto_image_button_text-bottom" role="presentation" src="https://moodle.ithephy.eu/pluginfile.php/173/mod_folder/content/0/hint2.png" title="show/hide second hint" height="25" width="25"></span></a>\n""")
            hiddendivs.append([o[1],hiddencounter,"<u>Hint 2:</u> "])
            
            
        if (o[0]=="controlresult"):
            hiddencounter+=1
            out.write(
            """<a onclick="javascript:ShowHide('HiddenDiv"""+str(hiddencounter)+"""')"><span class="" style="font-size: medium;cursor: pointer;margin: 0; padding: 0; border: 0"><img alt="" class="img-responsive atto_image_button_text-bottom" role="presentation" src="https://moodle.ithephy.eu/pluginfile.php/173/mod_folder/content/0/checkbox.png" title="show/hide control result" height="20" width="20"></span></a>\n""")
            hiddendivs.append([o[1],hiddencounter,"<u>Control result:</u> "])
            
        
        if (i<len(info)-1) and (info[i+1][0]!="hint1" and info[i+1][0]!="hint2" and info[i+1][0]!="controlresult") or (i==len(info)-1):
            for h in hiddendivs:
                if(taskflag=="task"):
                    out.write(hiddendiv(h))
                    
                elif(taskflag=="subtask"):
                    out.write(hiddendiv(h,True))
            
            hiddendivs[:]=[]
            
    
    out.write("\n<p>&nbsp;</p> <p>&nbsp;</p> <p>&nbsp;</p> <p>&nbsp;</p>")
    
    out.close()
    

WriteHeader()
WriteHTML()

print("Header written to file \""+headerfile+"\".")
print("Html written to file \""+outputfile+"\".")
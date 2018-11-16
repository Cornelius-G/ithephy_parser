# ithephy_parser

This script parses the iTHEPHY tex-templates for exercises and creates html files to be used for the implementation of exercises in moodle.


# currently able to parse the following latex elements:
+ enumerate[a)] 
+ math environments: $, align, align*
+ label, ref, eqref

# short instruction:
+ run `python ithephy_parser.py exercise.tex`
+ the output will be two html files (header.html, body.html)
+ sub-hints and sub-controlresults (i.e. \items in enumerate) will only appear if they have >1 letter

# todo:
+ literature
+ solution ?


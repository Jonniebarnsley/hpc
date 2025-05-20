import pandas as pd
import argparse

def parseinp(inp):

	'''
	reads a BISICLES input as a list of strings and turns it into
	a dictionary of options and their settings within that input file.
	'''

	outdict = {}
	for i, line in enumerate(inp):
		line = line.strip()
		if len(line) == 0:
			continue
		if line[0] == '#':
			continue
		try:
			opt, val = line.split('=')
		except ValueError:
			continue # e.g. for the vertical layer lines with no '='
		val = val.split('#')[0] # ignore comments
		outdict[opt.strip()] = val.strip()
   
	return outdict

def main(newinp, oldinp):

    '''
    takes paths to two input files and prints a dataframe of BISICLES
    options where the values in each input file are different.
    '''

    with open(newinp) as file:
        newtxt = file.read().splitlines()
    with open(oldinp) as file:
        oldtxt = file.read().splitlines()
	
    newops = parseinp(newtxt)
    oldops = parseinp(oldtxt)

    keys = []
    old = []
    new = []

    for key in oldops.keys():
        oldval = oldops[key]
        try:
            newval = newops[key]
        except KeyError:	# if option not selected in new input
            newval = ''
        if oldval != newval: # if inputs differ
            keys.append(key)
            old.append(oldval)
            new.append(newval)
	
    # construct and print dataframe
    df = pd.DataFrame({'option': keys, oldinp: old, newinp: new})
    pd.set_option('display.max_rows', None)
    print(df)


if __name__ == "__main__":

	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("new_input")
	parser.add_argument("old_input")
	
	args = parser.parse_args()
	main(args.new_input, args.old_input)
	
	

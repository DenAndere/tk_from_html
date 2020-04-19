Because I find typing everything out for creating a grid in tkinter,
I tought of finding a way to create my interface in Photoshop, 
then slice it as if I would export it to an html file table,
then use the html and sliced images createed by Photoshop's 
Save for Web feature to create a TK Windw with the grid.

It has only been tested with Photoshop-generated html

It generates the names for the Tk frames and image objects from the filenames 
of the images. Some fool proofing here was added so certain characters are 
replaced by and underscore _.

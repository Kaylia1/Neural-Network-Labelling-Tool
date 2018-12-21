# Neural-Network-Labelling-Tool
Writes labelling information in KITTI format to specified text file.


DEPENDENCIES:

-Python 2 (https://www.python.org/downloads/)

-PIL (https://wp.stolaf.edu/it/installing-pil-pillow-cimage-on-windows-and-mac/).


INSTRUCTIONS:

-Directly edit code, set file paths of where images are drawn from and where text files are set (text file folder can be empty).

-Directly edit code, set the image file format and the name of the object being labelled.

-Click "Create box" then click and drag to create a bounding box within which your object is.

-Click and drag sliders for accuracy.

-If the object is partially off-screen, click the "truncated" checkbox on the bottom corresponding with the box number

-"Next"/"Last" assumes the image file names are numerical, and will add and subtract one from the numerical file name respectively.  Ensure in the code, the formatting matches the number of zeroes in the file being accessed.

-Remember to save!  This writes the information into the text file.


MODE 2: KEYBOARD -Fast Editing!

-On keyboard, type numbers to select boxes of corresponding number.

-On keyboard, type WASD keys to select sliders, then type arrow keys to adjust them.


FURTHER CLARIFICATION:

-This program only records object name, truncated (boolean), xmin, ymin, xmax, ymax

-If text file folder contains content, and the content's names match with the names of the images it is drawing, it will read then edit from the text file.

-Currently, ony one object type can be labelled at a time between code edits.

-Deleting a box will not change the box numbers (ex. can jump 1-3), this does not afftect writing to file (no lines skipped)

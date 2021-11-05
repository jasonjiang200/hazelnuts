# This file allows the logic for buttons to be saved in one spot and used whenever needed.
from cmu_112_graphics import *


def drawButton(canvas, cx: int, cy: int, width: int, height: int, color: str, borderWidth: int, borderColor: str) -> None:
    '''Draws a button given a center, dimensions, colors, and a click function.'''
    canvas.create_rectangle(cx-width//2, cy - height//2, cx+width//2, cy+height//2, fill = borderColor, width = borderWidth)
    canvas.create_rectangle(cx-width//2, cy - height//2, cx+width//2, cy+height//2, fill = color) 

def isInside(x: int, y: int, cx: int, cy: int, width: int, height: int) -> bool:
    '''Returns whether a given (x,y) is inside of a rectangle centered
    at (cx, cy) with the dimensions width and height.'''
    return cx-width//2 < x < cx+width//2 and cy-height//2 < y < cy+height//2
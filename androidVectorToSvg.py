#!/usr/bin/python3
import argparse
from lxml import etree


"""
TODO: - Add gradient color compatibility
      - Keep order of Android vector (right now, paths that were drawn on top are drawn at the bottom)
"""


def main(inputfile, outputfile):
    # https://developer.android.com/reference/android/graphics/drawable/VectorDrawable
    global namespace, clipPaths
    try:
        tree = etree.parse(inputfile)
        root = tree.getroot()
        namespace = root.nsmap["android"]
        clipPaths = []  # Clip paths are added in <defs> at the end

        newFile = createRoot(root)
        for child in root:
            if child.tag == "path":
                createPath(newFile, child)
            elif child.tag == "group":
                createGroup(newFile, child)
            elif child.tag == "clip-path":
                createClipPath(newFile, child)
            else:
                pass

        # Define the clipPaths, if there are any
        if len(clipPaths) > 0:
            defs = etree.SubElement(newFile, "defs")
            for i in range(len(clipPaths)):
                data = clipPaths[i]
                pathID = "clipPath{}".format(i)
                clip = etree.SubElement(defs, "clipPath", id=pathID)
                etree.SubElement(clip, "path", d=data)

        et = etree.ElementTree(newFile)
        et.write(outputfile, pretty_print=True, xml_declaration=False, encoding="utf-8")
    except Exception as e:
        print("Failed:", e)


def hasAttribute(element, name):
    return "{{{}}}{}".format(namespace, name) in element.attrib


def getAttribute(element, name):
    return element.attrib["{{{}}}{}".format(namespace, name)]


def createRoot(vector):
    width = getAttribute(vector, "width").replace("dp", "")
    height = getAttribute(vector, "height").replace("dp", "")
    viewportWidth = getAttribute(vector, "viewportWidth").replace("dp", "")
    viewportHeight = getAttribute(vector, "viewportHeight").replace("dp", "")

    if hasAttribute(vector, "alpha"):
        alpha = getAttribute(vector, "fillColor")
        vector.set("opacity", alpha)

    root = etree.Element("svg", xmlns="http://www.w3.org/2000/svg", width=width, height=height, viewBox="0 0 {} {}".format(viewportWidth, viewportHeight))
    return root


def createPath(root, path):
    data = getAttribute(path, "pathData")
    data = " ".join(data.split())  # Remove duplicate white-spaces
    child = etree.SubElement(root, "path", d=data)

    if hasAttribute(path, "name"):
        name = getAttribute(path, "name")
        child.set("id", name)

    if hasAttribute(path, "fillColor"):
        color = getAttribute(path, "fillColor")
        child.set("fill", color)
    else:
        child.set("fill", "none")

    if hasAttribute(path, "fillType"):
        rule = getAttribute(path, "fillType")
        child.set("fill-rule", rule)

    if hasAttribute(path, "fillAlpha"):
        alpha = getAttribute(path, "fillAlpha")
        child.set("fill-opacity", alpha)

    if hasAttribute(path, "strokeColor"):
        color = getAttribute(path, "strokeColor")
        child.set("stroke", color)

    if hasAttribute(path, "strokeWidth"):
        width = getAttribute(path, "strokeWidth")
        child.set("stroke-width", width)

    if hasAttribute(path, "strokeAlpha"):
        alpha = getAttribute(path, "strokeAlpha")
        child.set("stroke-opacity", alpha)

    if hasAttribute(path, "strokeLineCap"):
        cap = getAttribute(path, "strokeLineCap")
        child.set("stroke-linecap", cap)

    if hasAttribute(path, "strokeLineJoin"):
        join = getAttribute(path, "strokeLineJoin")
        child.set("stroke-linejoin", join)

    if hasAttribute(path, "strokeMiterLimit"):
        lim = getAttribute(path, "strokeMiterLimit")
        child.set("stroke-miterlimit", lim)


def createGroup(root, group):
    g = etree.SubElement(root, "g")

    if hasAttribute(group, "name"):
        name = getAttribute(group, "name")
        g.set("id", name)

    # Initialize values to specs' defaults so setting them won't change anything visually by default
    translateX, translateY, rotate, pivotX, pivotY, scaleX, scaleY = 0, 0, 0, 0, 0, 1, 1

    # Change values according to xml
    if hasAttribute(group, "translateX") and hasAttribute(group, "translateY"):
        translateX = getAttribute(group, "translateX")
        translateY = getAttribute(group, "translateY")

    if hasAttribute(group, "rotation"):
        rotate = getAttribute(group, "rotation")

    if hasAttribute(group, "pivotX") and hasAttribute(group, "pivotY"):
        pivotX = getAttribute(group, "pivotX")
        pivotY = getAttribute(group, "pivotY")

    if hasAttribute(group, "scaleX") and hasAttribute(group, "scaleY"):
        scaleX = getAttribute(group, "scaleX")
        scaleY = getAttribute(group, "scaleY")
    elif hasAttribute(group, "scaleX"):
        scaleX = getAttribute(group, "scaleX")
        scaleY = scaleX
    elif hasAttribute(group, "scaleY"):
        scaleY = getAttribute(group, "scaleY")
        scaleX = scaleY

    # Apply to group
    g.set("transform", "translate({} {}) rotate({} {} {}) scale({} {})".format(translateX, translateY, rotate, pivotX, pivotY, scaleX, scaleY))

    # Create subelements of group
    for child in group:
        if child.tag == "path":
            createPath(g, child)
        elif child.tag == "group":
            createGroup(g, child)
        elif child.tag == "clip-path":
            createClipPath(g, child)
        else:
            pass


def createClipPath(root, clip):
    data = getAttribute(clip, "pathData")
    data = " ".join(data.split())  # Remove duplicate white-spaces

    # Save clipPath
    pathID = len(clipPaths)
    clipPaths.append(data)

    # Apply clipPath
    root.set("clip-path", "url(#clipPath{})".format(pathID))


def displayHelp():
    print('Usage: test.py -i <inputfile> -o <outputfile>')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Android vector files to svg.")
    parser.add_argument("input", type=str, help="the file to convert")
    parser.add_argument("-o", "--output", type=str, help="the output file")

    args = parser.parse_args()
    inputfile = args.input
    if args.output:
        outputfile = args.output
    else:
        outputfile = inputfile[:-3] + "svg"

    main(inputfile, outputfile)

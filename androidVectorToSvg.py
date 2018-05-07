#!/usr/bin/python3
import argparse
from lxml import etree


def main(inputfile, outputfile):
    global namespace
    try:
        tree = etree.parse(inputfile)
        root = tree.getroot()
        namespace = root.nsmap["android"]

        newFile = createRoot(root)
        for child in root:
            if child.tag == "path":
                createPath(newFile, child)
            elif child.tag == "group":
                createGroup(newFile, child)
            else:
                pass

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
    root = etree.Element("svg", xmlns="http://www.w3.org/2000/svg", width=width, height=height, viewBox="0 0 {} {}".format(viewportWidth, viewportHeight))
    return root


def createPath(root, path):
    data = getAttribute(path, "pathData")
    child = etree.SubElement(root, "path", d=data)

    if hasAttribute(path, "fillColor"):
        color = getAttribute(path, "fillColor")
        child.set("fill", color)
    else:
        child.set("fill", "none")

    if hasAttribute(path, "strokeColor"):
        color = getAttribute(path, "strokeColor")
        child.set("stroke", color)

    if hasAttribute(path, "strokeWidth"):
        width = getAttribute(path, "strokeWidth")
        child.set("stroke-width", width)

    if hasAttribute(path, "strokeLineJoin"):
        join = getAttribute(path, "strokeLineJoin")
        child.set("stroke-linejoin", join)

    if hasAttribute(path, "strokeLineCap"):
        cap = getAttribute(path, "strokeLineCap")
        child.set("stroke-linecap", cap)

    if hasAttribute(path, "strokeMiterLimit"):
        lim = getAttribute(path, "strokeMiterLimit")
        child.set("stroke-miterlimit", lim)


def createGroup(root, group):
    g = etree.SubElement(root, "g")

    if hasAttribute(group, "translateX") and hasAttribute(group, "translateY"):
        x = getAttribute(group, "translateX")
        y = getAttribute(group, "translateY")
        g.set("transform", "translate({}, {})".format(x, y))

    for child in root:
        if child.tag == "path":
            createPath(g, child)
        else:
            pass


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

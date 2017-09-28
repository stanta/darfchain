import lxml
from lxml import etree

root = etree.Element("root")
child2 = etree.SubElement(root, "child2")

print(etree.tostring(root, pretty_print=True))

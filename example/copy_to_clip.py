import plistlib
from AppKit import NSPasteboard, NSPasteboardItem

with open('example/unsigned.shortcut', 'rb') as f:
    data = plistlib.load(f)

actions = data['WFWorkflowActions']

board = NSPasteboard.generalPasteboard()

items = []
for action in actions:
    item = NSPasteboardItem()
    item.setPropertyList_forType_(action, 'com.apple.shortcuts.action')
    items.append(item)

board.clearContents()
board.writeObjects_(items)

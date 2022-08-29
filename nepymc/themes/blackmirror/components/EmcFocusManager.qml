import QtQuick
import "../utils/utils.js" as Utils


FocusScope {
    id: root

    property bool focusAllow: true
    focus: false

    function focus_stack_pop() {
        var toFocus = null
        while (emcApplicationWindow.emcFocusStack.length > 0) {
            toFocus = emcApplicationWindow.emcFocusStack.pop()
            if (toFocus.focusAllow === true)
                break
        }
        if (toFocus && toFocus.focusAllow) {
//            print("FOCUS POPPING", toFocus)
            toFocus.forceActiveFocus()
        }
        return toFocus
    }

    function focus_stack_push(obj) {
//        print("FOCUS PUSH", obj)
        if (obj && obj !== emcApplicationWindow.emcFocusStack.last) {
            emcApplicationWindow.emcFocusStack.push(obj)
        }
    }

    function focus_stack_remove(obj) {
        emcApplicationWindow.emcFocusStack.remove(obj)
    }

//    onFocusChanged: console.log("quale dei due?")
    onActiveFocusChanged: {
        // main window lost focus, nothing to do
        if (activeFocusItem == null)
            return

        // we gain focus, nothing to do
        if (activeFocus) {
            return
        }

        // print all child for debug
//        print("#### FocusManager", activeFocus ? "FOCUS" : "UNFOCUS")
//        var obj = root
//        while (obj) {
//            print("#   ->", obj.objectName ? obj.objectName : obj,
//                  "(AF:", obj.activeFocus, "F:", obj.focus, ")")
//            obj = obj.parent
//        }
//        print("####", emcApplicationWindow.emcFocusStack)

        // detect lost focus on QML root object
        if (activeFocusItem.parent == null) {
            print("======= FOCUS LOST on root", activeFocusItem)
            focus_stack_pop()
            // TODO if stack_pop() return None ??
        }

        // we lost focus, put ourself in the focus stack
        if (!activeFocus && root.focusAllow) {
            focus_stack_push(root)
        }

//        print("####", emcApplicationWindow.emcFocusStack)
//        print("")

    }

    Component.onDestruction: {
        console.log("destroyed", root)
        focus_stack_remove(root)
    }

}

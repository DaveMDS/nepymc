import QtQuick 2.12
import QtQuick.Controls 2.12
import "utils/utils.js" as Utils


ApplicationWindow {
    id: emcApplicationWindow
    objectName: "main_win"

    minimumWidth: 960
    minimumHeight: 600
    visible: true
    title: EmcBackend.application_name()

    property var emcFocusStack: []  // TODO find a better place for this

    /* theme API TODOC */
    function activate_section(section) {
        console.log("activate_section: " + section)
        switch (section) {
        case "browser":
            emc_browser.forceActiveFocus()
            break
        case "mainmenu":
            emc_mainmenu.forceActiveFocus()
            break
        }
    }

    function hide_section(section) {
        console.log("hide_section: " + section)
        emc_mainmenu.focus_stack_pop()
    }

    function page_title_set(title) {
        emc_browser.page_title = title
    }

    function page_icon_set(icon) {
        emc_browser.page_icon = icon
    }

    function page_item_select(index) {
        emc_browser.currentIndex = index
    }

    function build_dialog(title, style, text, content, spinner) {
        var dia = Utils.load_qml_obj("components/EmcDialog.qml",
                                     emcApplicationWindow, {
                                         title: title,
                                         bigger: style === "panel",
                                         main_text: text,
                                         content: content,
                                         spinner: spinner
                                    })
        dia.forceActiveFocus()
        return dia
    }

    Component.onCompleted: {
        emc_mainmenu.forceActiveFocus()
    }

//    onActiveFocusItemChanged: {
//        print("**********  activeFocusItem  > ", activeFocusItem)
//        print(emcFocusStack)
//    }

    Image {
        anchors.fill: parent
        source: "pics/background.jpg"
        //source: "pics/TESTBG.jpg"
        fillMode: Image.PreserveAspectCrop
    }

    Browser {
        id: emc_browser
    }

    MainMenu {
        id: emc_mainmenu
    }

}

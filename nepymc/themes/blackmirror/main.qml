import QtQuick 2.12
import QtQuick.Controls 2.12
import "components/"
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

    // Linear volume 0.0-1.0, to be used in linear gui elements (sliders)
    property real emcLinearVolume  // value comes from python

    onEmcLinearVolumeChanged: emcVolumeIndicator.show_and_autohide()


    function activate_section(section) {
        console.log("activate_section: " + section)
        var obj
        switch (section) {
        case "browser":
            obj = emc_browser
            break
        case "mainmenu":
            obj = emc_mainmenu
            break
        case "videoplayer":
            emcVideoPlayerLoader.active = true
            obj = emcVideoPlayerLoader.item
            break;
        default:
            print("ERROR: unknown section: " + section)
            return
        }
        obj.forceActiveFocus()
        return obj
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

    function build_dialog(title, style, text, content, spinner, list_model) {
        var bigger = (style === "panel" || style === "list" || style.startsWith("image_list"))
        var dia = Utils.load_qml_obj("components/EmcDialog.qml",
                                     emcApplicationWindow, {
                                         style: style,
                                         title: title,
                                         bigger: bigger,
                                         main_text: text,
                                         content: content,
                                         spinner: spinner,
                                         list_model: list_model,
                                         progress: style === "progress" ? 0 : -1
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
//        source: "pics/TESTBG.jpg"
        fillMode: Image.PreserveAspectCrop
    }

    Browser {
        id: emc_browser
    }

//    Navigator {
//        id: emc_navigator
//    }

    MainMenu {
        id: emc_mainmenu
    }

    Loader {
        id: emcVideoPlayerLoader
        active: false
        anchors.fill: parent
        source: "components/EmcVideoPlayer.qml"
    }

    EmcVolumeIndicator {
        id: emcVolumeIndicator
        emcVisible: false
    }

}

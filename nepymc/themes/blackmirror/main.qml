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

    function build_video_player(url) {
        var player = Utils.load_qml_obj("components/EmcVideoPlayer.qml",
                                        emcApplicationWindow, {
                                            url: url
                                       })
        player.forceActiveFocus()
        return player
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

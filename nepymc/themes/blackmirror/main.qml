import QtQuick 2.11
import QtQuick.Controls 2.0


ApplicationWindow {

    minimumWidth: 960
    minimumHeight: 600
    visible: true
    title: EmcBackend.application_name()

    Image {
        anchors.fill: parent
        source: "pics/background.jpg"
        //source: "pics/TESTBG.jpg"
        fillMode: Image.PreserveAspectCrop
    }

    /* theme API TODOC */
    function activate_section(section) {
        console.log("activate_section: " + section)
        switch (section) {
        case "browser":
            emc_mainmenu.emc_active = false

            emc_browser.emc_active = true
            emc_browser.focus = true
            break
        case "mainmenu":
            emc_browser.emc_active = false

            emc_mainmenu.emc_active = true
            emc_mainmenu.focus = true
            break
        }
    }

    function hide_section(section) {
        console.log("hide_section: " + section)
        switch (section) {
        case "browser":
            emc_browser.emc_active = false; break
        case "mainmenu":
            emc_mainmenu.emc_active = false; break
        }
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

    Component.onCompleted: {
        emc_mainmenu.emc_active = true
        emc_mainmenu.focus = true
//        emc_browser.emc_active = true
//        emc_browser.focus = true
    }

    Browser {
        id: emc_browser
//        focus: true
    }

    MainMenu {
        id: emc_mainmenu
//        focus: true
    }



}

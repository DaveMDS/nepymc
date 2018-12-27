

/* Array extensions */
if (!Array.prototype.first){
    Array.prototype.first = function() {
        return this[0]
    }
}
if (!Array.prototype.last){
    Array.prototype.last = function() {
        return this[this.length - 1]
    }
}
if (!Array.prototype.remove){
    Array.prototype.remove = function(item) {
        for (var i = 0; i < this.length; i++) {
           if (this[i] === item){
             this.splice(i, 1);
           }
        }
    }
}

/* Dynamic object creator */
function load_qml_obj(file, parent, properties) {
    var comp = Qt.createComponent("../" + file)
    if (comp.status === Component.Ready) {
        return comp.createObject(
                    parent ? parent : emcApplicationWindow,
                    properties ? properties : {})
    }
    console.log(comp.errorString())
    return null
}

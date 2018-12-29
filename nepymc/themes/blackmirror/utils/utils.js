

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

/* String extensions */
if (!String.prototype.format){
    String.prototype.format = function() {
        var content = this
        for (var i = 0; i < arguments.length; i++) {
            var replacement = '{' + i + '}'
            content = content.replace(replacement, arguments[i])
        }
        return content
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

/* Milliseconds to time string
    Convert the number of seconds in a readable duration
    hours: If True then hours will be visible also when < 1
*/
function ms_to_duration(ms, hours) {
    if (hours === undefined) hours = false

   var seconds = Math.round(ms / 1000),
       h = Math.floor(seconds / 3600),
       m = Math.floor((seconds / 60) % 60),
       s = Math.floor(seconds % 60)
   if (h > 0 || hours) {
       if (m < 10) m = "0" + m
       if (s < 10) s = "0" + s
       return "{0}:{1}:{2}".format(h, m, s)
   } else {
       if (s < 10) s = "0" + s
       return "{0}:{1}".format(m, s)
   }
}

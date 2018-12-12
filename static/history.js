$(document).ready(function() {
    var socket = io.connect('http://localhost:5000/')
    socket.on('connect', function(){
        console.log("User has connected")

    })

    //  Receive a message
    socket.on('message', function(msg){
        console.log('got html message' +  msg)

        m = msg.split('~')
        var id_num = m[0] // don't use this right now, carry over from index.js
        var html = m[1]

        table_to_append = "history"
        console.log('appending to', table_to_append)
        $(table_to_append).append(html)
    })

});


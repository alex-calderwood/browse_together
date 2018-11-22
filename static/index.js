$(document).ready(function() {
    var socket = io.connect('http://localhost:5000/')
    socket.on('connect', function(){
        console.log("User has connected")

    })

    //  Receive a message
    socket.on('message', function(msg){
//        console.log('got html message' +  msg)

        m = msg.split('~')
        var id_num = m[0]
        var html = m[1]

//        console.log(id_num, html)

        table_to_append = "#" + id_num + "-messages"
        console.log('appending to', table_to_append)
        $(table_to_append).append(html)
    })

    //  Send a message
    $("#sendButton").click(function(){
        var myMessage = $("#myMessage").val()
        var user = $('#title').text()

        myMessage = myMessage + '~' + user
        socket.send(myMessage)
        console.log('Sent message', myMessage)
    })

//    console.log('alex', document.getElementById("my-frame").contentWindow.location.href)
});


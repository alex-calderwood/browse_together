$(document).ready(function() {
    var socket = io.connect('http://localhost:5000/')
    socket.on('connect', function(){
        console.log("User has connected")

    })

    //  Receive a message
    socket.on('message', function(msg){

        m = msg.split('~')
        var id_num = m[0]
        var html = m[1]

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

    // Collapse sidebar
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    })

    // Start sending history to a group
    $('#send-history').on('click', function() {

        console.log('something')

        var checked = false

        if ($('#send-history').is(":checked")) {
            checked = true
        }

        // Get the group name
        var group_url = window.location.pathname
        group_url = group_url.replace(/%20/g," ");
        var group = group_url.split('/')
        console.log('group', group)
        group = group[2]

        url = '../toggle_send_browsing/' + group

        console.log(url, checked)

        const request_data = {
          group_name: group,
          should_send: checked
        }

        $.post(url, request_data, function( data ) {
//            console.log('posted', request_data)
//c            console.log(data)
        });


    });


//    console.log('alex', document.getElementById("my-frame").contentWindow.location.href)
});


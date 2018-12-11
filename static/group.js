$(document).ready(function() {
    var socket = io.connect('http://localhost:5000/')
    socket.on('connect', function(){
        console.log("User has connected")

    });

    //  Receive a message
    socket.on('message', function(msg){

        m = msg.split('~')
        var id_num = m[0]
        var html = m[1]

        table_to_append = "#" + id_num + "-messages"
        $(table_to_append).append(html)
    });

    //  Send a message
    $("#sendButton").click(function(){
        var myMessage = $("#myMessage").val()
        var user = $('#title').text()

        myMessage = myMessage + '~' + user
        socket.send(myMessage)
    });

    // Collapse sidebar
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
        $(this).toggleClass('active');
    });

    // Toggle Options
    $( "#myOptionsButton").click(function() {
        if ( $('.options-card').css('visibility') == 'hidden' )
            $('.options-card').css('visibility','visible');
        else
            $('.options-card').css('visibility','hidden');

    });

    // Start sending history to a group
    $('#send-history').on('click', function() {

        var checked = false

        if ($('#send-history').is(":checked")) {
            checked = true
        }

        // Get the group name
        var group_url = window.location.pathname
        group_url = group_url.replace(/%20/g," ");
        var group = group_url.split('/')
        group = group[2]
        url = '../toggle_send_browsing/' + group
        user = 'Alex'

        const request_data = {
          user: user, // Unused for now
          group_name: group,
          should_send: checked
        }

        $.post(url, request_data, function( data ) {
//            console.log('posted', request_data)
//c            console.log(data)
        });
    });
});

// Toggle color of clicked checkbox
function voteClick(link) {
    const url = '/api/register_vote/'
    const element = document.getElementById(link.id)

    element.classList.toggle('checked')
    is_checked = element.classList.contains('checked')

    user = $("#username").text()
    const request_data = {"user": user, "link": link.id, 'vote_status': is_checked}

    console.log('vote', request_data)

    $.post(url, request_data, function(response_data) {
        console.log('posted', request_data, response_data)
    });
}

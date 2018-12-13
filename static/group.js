$(document).ready(function() {


    function sleep(delay) {
        var start = new Date().getTime();
        while (new Date().getTime() < start + delay);
    }

    // Get the delete card modal ready
    var modal = document.getElementById('delete-modal');
    var del_x = document.getElementsByClassName('card-delete');
    var modal_close = document.getElementsByClassName('delete-modal-close')[0];
    var delete_button = document.getElementsByClassName('delete-button')[0];
    var prev_clicked_delete_button = -1;


    modal_close.onclick = function() {
        modal.style.display = "none"
    };

    delete_button.onclick = function() {
        modal.style.display = "none"
        console.log(prev_clicked_delete_button)

        // Delete the link whose 'x' was last pressed from the database
        const delete_url = '../delete_link/'

        $.post(delete_url, prev_clicked_delete_button, function( data ) {

        });

        // Delete the card html from the document
//      document.getElementById("custom-card-" + prev_clicked_delete_button).style.height = "0px";
        document.getElementById("custom-card-" + prev_clicked_delete_button).remove();
    };

    for (var i = 0; i < del_x.length; i++) {
        del_x[i].onclick = function(event) {
            modal.style.display = "block";
            target = event.currentTarget;
            id = target.id.split('-')[1];

            // Keep track of the last 'x' that was pressed by the user
            prev_clicked_delete_button = id;
        }
    }

    // End delete modal stuff

    // Do the same for the finalize modal
    var finalize_floating = document.getElementById('finalize-button');
    var finalize_modal = document.getElementById('finalize-modal');
    var finalize_modal_close = document.getElementById('finalize-modal-close');
    var do_finalize_button = document.getElementById('do-finalize-button');
    var top_card = document.getElementsByClassName('custom-card-title')[0];

    finalize_modal_close.onclick = function() {
        finalize_modal.style.display = "none"
    };

    do_finalize_button.onclick = function() {
        finalize_modal.style.display = "none"
    };

    finalize_floating.onclick = function() {
        finalize_modal.style.display = "block"
        console.log(top_card)
        top_card.style.zIndex = "3";
    }

    // End finalize modal stuff

    if (del_x.length > 0) {
        finalize_floating.style.display = "block";
    }

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

        console.log(group)

        const request_data = {
          user: user, // Unused for now
          group_name: group,
          should_send: checked
        }

        $.post(url, request_data, function( data ) {

        });

        location.reload();
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

    // Increment or decrement the vote count number
    id = link.id.split('-')[1]

    vote_count = $('#vote-count-' + id)
    if (is_checked) {
        new_count = parseInt(vote_count.text()) + 1
    } else {
        new_count = parseInt(vote_count.text()) - 1
    }
    vote_count.text(new_count) // set the new value

    $.post(url, request_data, function(response_data) {
        console.log('posted', request_data, response_data)
    });
}
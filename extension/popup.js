$(document).ready(function() {

    $( "#star" ).click(function() {
        star = $("#star")

        if (! star.hasClass("checked")) {
            star.toggleClass("checked")

            $("#message").replaceWith("<span id=\"message\">Sent URL to Group</span>");

                chrome.tabs.query({'active': true, 'lastFocusedWindow':true}, function (tabs) {
                    const url = tabs[0].url
                    const url_data = {"url": url}
                    const endpointUrl='http://localhost:5000/api/register_url_change/'
                    $.post(endpointUrl, url_data, function(data, status){
                      console.log(url_data.url + ' sent: ' + changeInfo)
                      alert(data + ' ' + status)
                    });
                });

        }
    });
});


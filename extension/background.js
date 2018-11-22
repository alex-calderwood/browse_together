// The listener for adding vistited sites to database
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
//    console.log(tabId)

    const request_data = {
      user: "Said",
      new_url: changeInfo.url
    }

    // Url to post browsing data to
    const Url='http://localhost:5000/api/register_url_change/'

    $.post(Url, request_data, function(data, status){
      console.log(data + ' is and status is ' + status)
    });
});

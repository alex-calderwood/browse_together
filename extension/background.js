// The listener for adding vistited sites to database
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
//    console.log(tabId)

//    const request_data = {
//      user: "Said",
//      new_url: changeInfo.url
//    }

    // Url to post browsing data to
    const endpointUrl='http://localhost:5000/api/register_url_change/'

    $.post(endpointUrl, changeInfo, function(data, status){
      console.log(changeInfo.url + ' sent: ' + changeInfo)
    });
});

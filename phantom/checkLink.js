//phantomjs checkLink.js domain password uid url
var system = require('system');
if (system.args.length < 5) {
    console.log("Missing args!");
    phantom.exit();
}
var domain = system.args[1];
var password = system.args[2];
var userid = system.args[3];
var userurl = system.args[4]

console.log(userid+' Starting')

var page = require('webpage').create();
page.userAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36";
page.onAlert = function(msg) {
    console.log(userid+' Caused alert: '+msg);
}
page.onUrlChanged = function(url) {
    console.log(userid+' Went to page: '+url);
}

var login = function() { 
    page.open(
        'http://'+domain+'/api/login', 
        'post', 
        'name=moderator&pass='+encodeURIComponent(password),
        function(status) {
            if (status !== 'success') {
                console.log(userid+' Failed to login as moderator... User might be fucked...');
            } else {
                //console.log(page.content);
                console.log(userid+' Logged in as moderator');
            }
            visitLink();
        }
    )
}

var visitLink = function() {
    console.log(userid+' Loading page: '+userurl);
    page.open(userurl,function(status) {
        if (status === 'success') {
            //console.log(page.content);
        }
    });
    setTimeout(killPhantom, 2000);
}

var killPhantom = function() {
    console.log(userid+' Killing phantom');
    phantom.exit();
}

login();

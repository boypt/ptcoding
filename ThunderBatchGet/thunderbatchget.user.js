// ==UserScript==

// @name          ThunderBatchGet

// @namespace     PTScript.vip.xunlei.com

// @description   PTScript: get download links and cookies from thunder cloud.

// @match         http://*.cloud.vip.xunlei.com/*

// @require       http://ajax.googleapis.com/ajax/libs/jquery/1.7.0/jquery.min.js

// ==/UserScript==

console.log("gm run");

var request_for_download = function(name, url) {
    $.get("http://localhost:8080/new_single_file_task", 
            { name: name, url: url, cookies: document.cookie });
}

$().ready(function () {
    console.log("ready run");
    var nav_wget_btn = $('<h2 class="saveside"><a href="#"><em class="ic_sf"></em>InsertDownLink</a></h2>').click(function () {
        console.log("Insert");
        if ($("#rowbox_list").is(":visible")) {
            console.log("rowbox_list visible");

            $("div#rowbox_list div.rw_list").each(function () { 
                icon = $(this).find("img.png");
                if ($(icon).attr("src").indexOf("bt") == -1) {
                    var tid = $(this).attr("taskid"); 
                    console.log("tid", tid);
                    var btns = $(this).find("div.rwset p").last();
                    $('<a class="rwbtn ic_redownloca batchget" href="#">Down</a>')
                        .click(function () { 
                            var pardiv = $(this).parents("div.rw_inter");
                            dl_name = $(pardiv).children('input[id^="durl"]').attr("value");
                            dl_url = $(pardiv).children('input[id^="dl_url"]').attr("value");
                            console.log("dl_url", dl_url);
                            console.log("dl_name", dl_name);
                            request_for_download(dl_name, dl_url);
                        }).appendTo(btns);
                }
            }); // single files


            var downall_btn = $('<a style="margin-left: 15px;" class="batchget" href="#">DownAll(Files)</a>')
                .click(function (){
                    $("div#rowbox_list div.rw_list").each(function () { 
                        icon = $(this).find("img.png");
                        if ($(icon).attr("src").indexOf("bt") == -1) {
                            dl_name = $(this).find('input[id^="durl"]').attr("value");
                            dl_url = $(this).find('input[id^="dl_url"]').attr("value");
                            console.log("dl_url", dl_url);
                            console.log("dl_name", dl_name);
                            //request_for_download(dl_name, dl_url);
                        }
                    });
            }).appendTo("div.sellection:visible p");// all single files

        } // insert main view

        if ($("#rwbox_bt_list").is(":visible")) {
            console.log("rwbox_bt_list visible");

            // each one
            $("div#rwbox_bt_list div.rw_list").each(function () { 
                var btns = $(this).find("div.rwset p").last();
                $('<a class="rwbtn ic_redownloca batchget" href="#">Down</a>')
                    .click(function () { 
                        var btid  = $(this).parents("div.rw_list").attr('i');
                        dl_name = $('#bt_taskname' + btid).attr("value");
                        dl_url = $('#btdownurl' + btid).attr("value");
                        console.log("dl_url", dl_url);
                        console.log("dl_name", dl_name);
                        request_for_download(dl_name, dl_url);
                }).appendTo(btns);
            });

            // down all
            var downall_btn = $('<a style="margin-left: 15px;" href="#">DownAll</a>')
                .click(function (){
                    $('input[name="bt_taskname"]').each(function () {
                        var dl_name = $(this).attr("value");
                        var dl_url = $(this).nextUntil("input[id^=btdownurl").attr("value");
                        console.log("dl_name", dl_name);
                        console.log("dl_url", dl_url);
                        //request_for_download(dl_name, dl_url);
                    });
            }).appendTo("div.sellection:visible p");

        } // insert bt view

        return false;
    }).appendTo("div.side_nav");
});


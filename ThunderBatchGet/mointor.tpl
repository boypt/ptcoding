<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Control Panel</title>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.0/jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="http://jquery.offput.ca/js/jquery.timers.js" type="text/javascript" charset="utf-8"></script>
<style type="text/css">


* {
    margin: 0;
    padding: 0;
}

body {
    background-color: #eee;

}

a:link, a:visited {
    color: #000;
    text-decoration:none;
}


#tasks {
    margin: 5px;
    padding: 5px;
    background-color: #ddd;
    float: left;
    width: 30%;
    min-height:480px;
}

#tasks ul li{
    margin: 10px 5px 10px 20px;
    background-color: #ccc;
}

a.taskbuttom {
    margin-left: 3px;
    font-size: 12px;
}

#tasks ul li a em{
    margin: 3px;
    float: right;
}


#control {
    margin: 5px;
    padding: 5px;
    float: left;
    width: 65%;
    background-color: #ddd;
    min-height:480px;
}

.filename_head {
    font-size: 1.2em;
}

.filename_head em{
    float: right;
}


.logwindow {
    margin: 10px 0;
    font-family:monospace;
    overflow-y: scroll;
    background-color: #ccc;
    height: 380px;
}

</style>
<script type="text/javascript">

API_BASE = "http://127.0.0.1:8080"


function update_tasks() {
    $.get(API_BASE + "/list_all_tasks").success(function (data) {
        //$("#tasks ul li").remove();
        $.each(data.tasks, function () {
            var uid = this[0];
            var filename = this[1];
            var status = this[2];

            if ($("#empty_task").is(":visible")) {$("#empty_task").hide();}

            if ($("#uid" + uid).length == 0) {

                var task = $('<li id="uid' + uid + '"><a class="taskbuttom" href="#">' + filename + '<em>' + status + '</em></a></li>').appendTo("#tasks ul");
                $(task).children("a").attr("uid", uid).click(function () {

                    console.log("click", $(this).attr("uid"));
                    var uid = $(this).attr("uid");
                    if ($("#task_control_" + uid).length == 0){
                        var tc = $("#task_control_tpl").clone().attr("id", 
                                "task_control_" + uid).appendTo("#control");
                        $(tc).children("h2").html($(this).html());

                        $(tc).everyTime(1000, "timer"+uid, function (){
                            $.getJSON(API_BASE + "/query_task_log/" + uid)
                                .success(function (data){
                                    console.log(data);
                                    var logwindow = $(tc).children("div.logwindow");

                                    if (data.line.length != 0) {;
                                        $(logwindow).append(data.line.replace(/\n/g, '<br /> \n'));
                                    }
                                    if (data.status != "Running") {
                                        $(tc).stopTime("timer"+uid);
                                        update_tasks();
                                        $(tc).children("h2").children("em").text(data.status);
                                        $(logwindow).append("subprocess ended.<br />");
                                    }

                                    // scroll to buttom
                                    $(logwindow).animate(
                                        { "scrollTop": $(logwindow).prop("scrollHeight") }, 100);
                            })
                                .error(function (err) {
                                    console.log(err);
                                    $(tc).stopTime("timer"+uid);
                            });
                        });


                    }

                    $(".taskinfo:visible").hide();
                    var tc = $("#task_control_" + uid).show();
                    return false;
                });
            }
            else {
                $("#uid" + uid).children("a").children("em").text(status);
            }
        });
    });
};




$(function () {

    $("#update_tasks").click(function (){update_tasks(); return false;});
    $("#clear_ended").click(function (){

        $("li[id^=uid]:visible").each(function() {
            if ($(this).children("a").children("em").text() == "Ended") {
                $(this).fadeOut();
            }
        });
        return false;
    });
    update_tasks();
    
    
});
    //$("#tasks ul").append($("<li>test</li>"));

//});

</script>
</head>

<body>

<div id="tasks">
    <div><p><a id="update_tasks" href="#">Update Task</a></p></div>
    <ul>
        <li id="empty_task">No task. Click 'Updata Tasks'.</li>
    </ul>
    <div><p><a id="clear_ended" href="#">Clear Ended</a></p></div>
</div>

<div id="control">
    <div id="task_control_tpl" style="display:none;" class="taskinfo">
        <h2 class="filename_head"></h2>
        <div class="logwindow">
        </div>
    </div>
</div>

</body>
</html>


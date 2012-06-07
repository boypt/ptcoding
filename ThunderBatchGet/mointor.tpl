<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Control Panel</title>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.0/jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="https://raw.github.com/patryk/jquery.timers/master/jquery.timers.min.js" type="text/javascript" charset="utf-8"></script>

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
    padding: 3px 5px;
    font-family:monospace;
    overflow-y: scroll;
    background-color: #ccc;
    height: 380px;
}

#ctl_buttons {
    list-style: none outside;
}


#ctl_buttons li {
    display: inline;
    margin: 10px;
}

#tasks div {
    margin: 5px 0;

}

.qq_task {
    background-color: #d1bbbb;
}

.thunder_task {
    background-color: #bcc;
}

</style>
<script type="text/javascript">

API_BASE = ""


function update_tasks() {
    $.get(API_BASE + "/list_all_tasks").success(function (data) {
        //$("#tasks ul li").remove();
        $.each(data.tasks, function () {
            var uid = this.uid;
            var tasktype = this.tasktype;
            var filename = this.filename;
            var status = this.status;

            if ($("#empty_task").is(":visible")) {$("#empty_task").hide();}

            if ($("#uid" + uid).length == 0) {

                var task = $('<li id="uid' + uid + '"><a class="taskbuttom" href="#">' + filename + '<em>' + status + '</em></a></li>').addClass(tasktype + "_task").appendTo("#tasks ul");
                $(task).children("a").attr("uid", uid).click(function () {

                    var uid = $(this).attr("uid");

                    console.log("click", uid);

                    if ($("#task_control_" + uid).length == 0){
                        $("#task_control_tpl").clone()
                                .attr("id","task_control_" + uid).attr("taskuid", uid).appendTo("#taskcontainer")
                                .children("h2").html($(this).html());
                    }

                    $(".taskinfo:visible").stopTime().slideUp();
                    $("#task_control_" + uid).slideDown()
                        .everyTime(500, "timer"+uid, function (){
                            $.getJSON(API_BASE + "/query_task_log/" + uid)
                                .success(function (data){
                                    //console.log(data);
                                    var tc = $("#task_control_" + uid);
                                    var logwindow = $(tc).children("div.logwindow");

                                    if (data.line.length != 0) {;
                                        $(logwindow).append(data.line.replace(/\n/g, '<br /> \n'));
                                    }
                                    if (data.status != "Running") {
                                        if (data.status == "Done" || data.status === "Stop" || data.status === "Queue")
                                            $(tc).stopTime("timer"+uid);
                                        update_tasks();
                                        $(tc).children("h2").children("em").text(data.status);
                                        $(logwindow).append("subprocess ended.<br />");
                                        if (data.retry_time > 1) 
                                            $(logwindow).append("Task Retried " + data.retry_time + " times.<br />");
                                        if (data.retry_time > 5) {
                                            $(logwindow).append("Update stoped.");
                                            $(tc).stopTime("timer"+uid);
                                        }

                                    }

                                    // scroll to buttom
                                    $(logwindow).animate(
                                        { "scrollTop": $(logwindow).prop("scrollHeight") }, 0);
                            })
                                .error(function (err) {
                                    console.log(err);
                                    $(tc).stopTime("timer"+uid);
                            });
                        });
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
    $("#clear_done").click(function (){

        $("li[id^=uid]:visible").each(function() {
            if ($(this).children("a").children("em").text() == "Done") {
                $(this).slideUp();
            }
        });
        return false;
    });

    $("#pauselog").click(function (){
        $(".taskinfo:visible").stopTime();
        return false;
    });
    $("#clearlog").click(function (){
        $(".taskinfo:visible div.logwindow").empty();
        return false;
    });
    $("#forcerestart").click(function (){
        var uid = $("div[id^=task_control_]:visible").attr('taskuid');
        $.get(API_BASE + "/force_restart/" + uid).success(function (data) {
        });
        update_tasks();
        $("a[uid=" + uid + "]").click();
        return false;
    });
    $("#forcestop").click(function (){
        var uid = $("div[id^=task_control_]:visible").attr('taskuid');
        $.get(API_BASE + "/force_stop/" + uid).success(function (data) { });
        update_tasks();
        $("a[uid=" + uid + "]").click();
        return false;
    });
    $("#tasks").everyTime(5000, "timer_tasks", update_tasks);
    update_tasks();
    
    
});

</script>
</head>

<body>

<div id="tasks">
    <div><a id="update_tasks" href="#">Update Task</a></div>
    <ul>
        <li id="empty_task">No task. Click 'Updata Tasks'.</li>
    </ul>
    <div><a id="clear_done" href="#">Clear</a></div>
</div>

<div id="control">
    <div id="taskcontainer">
        <div id="task_control_tpl" style="display:none;" class="taskinfo">
            <h2 class="filename_head"></h2>
            <div class="logwindow">
            </div>
        </div>
    </div>
    <ul id="ctl_buttons">
        <li><a id="pauselog" href="#">PauseLog</a></li>
        <li><a id="clearlog" href="#">ClearLog</a></li>
        <li><a id="forcerestart" href="#">ForceRestart</a></li>
        <li><a id="forcestop" href="#">ForceStop</a></li>
    </ul>
</div>
<!-- -->
</body>
</html>


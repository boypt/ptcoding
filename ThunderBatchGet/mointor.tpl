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
    margin: 10px 5px 5px 20px;
    background-color: #ccc;
}

#tasks ul li a{
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

.logwindow {
    margin: 10px 0;
    font-family:monospace;
    overflow-y: scroll;
    background-color: #ccc;
    height: 380px;
}

</style>
<script type="text/javascript">

API_BASE = "http://localhost:8080"


function update_tasks() {
    $.get(API_BASE + "/list_all_tasks").success(function (data) {
        $("#tasks ul li").remove();
        $.each(data.tasks, function () {
            var filename = this[0];
            var status = this[1] ? "Running" : "Stoped";
            var task = $('<li><a href="#">' + filename + '<em>' + status + '</em></a></li>').appendTo("#tasks ul");
            $(task).children("a").click(function () {

                console.log("click");
                return false;
            });
        });
    });
};




$(function () {

    $("#update_tasks").click(update_tasks);
    
    
});
    //$("#tasks ul").append($("<li>test</li>"));

//});

</script>
</head>

<body>

<div id="tasks">
    <div><p><a id="update_tasks" href="#">Update Task</a></p></div>
    <ul>
        <li>No task. Click 'Updata Tasks'.</li>
    </ul>
</div>

<div id="control">
    <div id="taskinfo">
        <h2>TaskName</h2>
        <div style="display: none;" class="logwindow">
            <p></p>
        </div>
    </div>
</div>

</body>
</html>

